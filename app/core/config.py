import os
from dataclasses import dataclass
from pathlib import Path


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


@dataclass(frozen=True)
class Settings:
    app_env: str
    host: str
    port: int
    data_dir: Path
    database_path: Path
    upload_dir: Path
    work_dir: Path
    result_dir: Path
    default_language: str | None
    whisper_model: str
    max_upload_mb: int
    poll_interval_seconds: int
    api_token: str | None


def get_settings() -> Settings:
    data_dir = Path(_env("DATA_DIR", "./data"))
    return Settings(
        app_env=_env("APP_ENV", "development"),
        host=_env("HOST", "0.0.0.0"),
        port=int(_env("PORT", "8000")),
        data_dir=data_dir,
        database_path=Path(_env("DATABASE_PATH", str(data_dir / "db" / "jobs.sqlite3"))),
        upload_dir=Path(_env("UPLOAD_DIR", str(data_dir / "uploads"))),
        work_dir=Path(_env("WORK_DIR", str(data_dir / "work"))),
        result_dir=Path(_env("RESULT_DIR", str(data_dir / "results"))),
        default_language=_env("DEFAULT_LANGUAGE", "") or None,
        whisper_model=_env("WHISPER_MODEL", "large-v3-turbo"),
        max_upload_mb=int(_env("MAX_UPLOAD_MB", "100")),
        poll_interval_seconds=int(_env("POLL_INTERVAL_SECONDS", "2")),
        api_token=_env("API_TOKEN", "") or None,
    )


settings = get_settings()
