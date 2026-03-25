import time
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.core.db import init_db
from app.core.logging import get_logger
from app.domain.jobs import claim_next_job, complete_job, fail_job
from app.domain.transcripts import build_text_from_segments, save_transcript_result
from app.services.storage import ensure_storage_dirs
from app.services.transcription import transcribe_audio_file

logger = get_logger("worker")


def process_job(job: dict[str, object]) -> None:
    job_id = str(job["id"])
    input_path = Path(str(job["stored_input_path"]))
    wav_path = settings.work_dir / f"{job_id}.wav"
    logger.info("processing job %s", job_id)

    result = transcribe_audio_file(input_path=input_path, wav_path=wav_path, language=job.get("language") or None)
    payload = {
        "job_id": job_id,
        "status": "completed",
        "filename": job["original_filename"],
        "language": job.get("language"),
        "detected_language": result["detected_language"],
        "duration_seconds": result["duration_seconds"],
        "text": build_text_from_segments(result["segments"]),
        "segments": result["segments"],
        "created_at": job["created_at"],
        "started_at": job["started_at"],
        "completed_at": None,
    }
    result_path = save_transcript_result(job_id, payload)
    complete_job(job_id, result_path, result["detected_language"], result["duration_seconds"])

    saved_payload = payload | {"completed_at": datetime.now(timezone.utc).isoformat()}
    save_transcript_result(job_id, saved_payload)
    wav_path.unlink(missing_ok=True)
    logger.info("completed job %s", job_id)


def main() -> None:
    ensure_storage_dirs(settings)
    init_db(settings.database_path)
    logger.info("worker started")
    while True:
        job = claim_next_job()
        if not job:
            time.sleep(settings.poll_interval_seconds)
            continue
        try:
            process_job(job)
        except Exception as exc:
            logger.exception("job failed: %s", job["id"])
            fail_job(str(job["id"]), str(exc))


if __name__ == "__main__":
    main()
