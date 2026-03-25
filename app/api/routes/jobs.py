from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import require_token
from app.domain.jobs import get_job, list_jobs
from app.domain.transcripts import load_transcript_result

router = APIRouter(tags=["jobs"])


@router.get("/jobs", dependencies=[Depends(require_token)])
def get_jobs(limit: int = 20) -> dict[str, list[dict[str, object]]]:
    return {"jobs": list_jobs(limit=limit)}


@router.get("/jobs/{job_id}", dependencies=[Depends(require_token)])
def get_job_status(job_id: str) -> dict[str, object]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs/{job_id}/result", dependencies=[Depends(require_token)])
def get_job_result(job_id: str) -> dict[str, object]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=409, detail="Job is not completed")
    return load_transcript_result(job_id)
