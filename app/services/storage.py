import re
from pathlib import Path

from app.core.config import Settings


def ensure_storage_dirs(settings: Settings) -> None:
    for path in [
        settings.data_dir,
        settings.upload_dir,
        settings.work_dir,
        settings.result_dir,
        settings.database_path.parent,
        settings.whisper_cache_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", filename)
    return sanitized.strip("._") or "upload"
