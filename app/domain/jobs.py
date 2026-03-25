import shutil
import uuid
from datetime import datetime, timezone

from fastapi import UploadFile

from app.core.config import settings
from app.core.db import get_connection
from app.services.storage import safe_filename


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def create_job(upload: UploadFile, filename: str, language: str | None) -> dict[str, str]:
    job_id = str(uuid.uuid4())
    target_filename = f"{job_id}__{safe_filename(filename)}"
    target_path = settings.upload_dir / target_filename

    size = 0
    with target_path.open("wb") as handle:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > settings.max_upload_mb * 1024 * 1024:
                handle.close()
                target_path.unlink(missing_ok=True)
                raise ValueError("Upload exceeds size limit")
            handle.write(chunk)

    with get_connection(settings.database_path) as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                id, status, original_filename, stored_input_path, language, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (job_id, "queued", filename, str(target_path), language, _now()),
        )

    return {"id": job_id, "status": "queued"}


def list_jobs(limit: int = 20) -> list[dict[str, object]]:
    with get_connection(settings.database_path) as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_job(job_id: str) -> dict[str, object] | None:
    with get_connection(settings.database_path) as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return dict(row) if row else None


def claim_next_job() -> dict[str, object] | None:
    with get_connection(settings.database_path) as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at ASC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE jobs SET status = ?, started_at = ? WHERE id = ? AND status = 'queued'",
            ("processing", _now(), row["id"]),
        )
        updated = conn.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone()
    return dict(updated) if updated else None


def complete_job(
    job_id: str,
    result_path: str,
    detected_language: str | None,
    duration_seconds: float | None,
) -> None:
    with get_connection(settings.database_path) as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, stored_result_path = ?, detected_language = ?, duration_seconds = ?, completed_at = ?
            WHERE id = ?
            """,
            ("completed", result_path, detected_language, duration_seconds, _now(), job_id),
        )


def fail_job(job_id: str, error_message: str) -> None:
    with get_connection(settings.database_path) as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, error_message = ?, completed_at = ? WHERE id = ?",
            ("failed", error_message[:2000], _now(), job_id),
        )
