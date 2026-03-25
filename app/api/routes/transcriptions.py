from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.deps import require_token
from app.domain.jobs import create_job

router = APIRouter(tags=["transcriptions"])

ALLOWED_EXTENSIONS = {".m4a", ".mp3", ".wav", ".ogg", ".oga", ".webm"}


@router.post("/transcriptions", dependencies=[Depends(require_token)])
async def create_transcription(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> dict[str, str]:
    filename = file.filename or "upload"
    if "." not in filename:
        raise HTTPException(status_code=400, detail="File must have an extension")
    ext = f".{filename.rsplit('.', 1)[1].lower()}"
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    try:
        job = await create_job(upload=file, filename=filename, language=language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"job_id": job["id"], "status": job["status"]}
