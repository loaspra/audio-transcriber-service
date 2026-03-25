from fastapi import FastAPI

from app.api.routes import health, jobs, transcriptions
from app.core.config import settings
from app.core.db import init_db
from app.services.storage import ensure_storage_dirs


def create_app() -> FastAPI:
    ensure_storage_dirs(settings)
    init_db(settings.database_path)

    app = FastAPI(title="Audio Transcriber Service", version="0.1.0")
    app.include_router(health.router)
    app.include_router(transcriptions.router)
    app.include_router(jobs.router)
    return app


app = create_app()
