# Audio Transcriber Service Implementation

## Goal

Build a new standalone async audio transcription service without modifying the existing `video-trans` project.

## Scope

- Audio uploads only in v1
- Async API with job creation, polling, and result retrieval
- Local disk persistence on a shared data directory
- SQLite for job state
- FastAPI for HTTP API
- Single worker process polling queued jobs
- Whisper model default: `large-v3-turbo`
- Kubernetes deployment target: k3s on `legion-server`

## Non-Goals

- Video support
- Frame sampling or summaries
- Redis, Celery, Postgres, object storage
- Multi-worker concurrency in v1
- UI frontend

## Architecture

- API process accepts uploads and creates jobs
- Worker process polls SQLite for queued jobs and transcribes audio
- Shared filesystem layout under `/data`
- Shared Docker image, different commands for API and worker

## Data Layout

- `/data/db/jobs.sqlite3`
- `/data/uploads/<job_id>__<safe_filename>`
- `/data/work/<job_id>.wav`
- `/data/results/<job_id>.json`

## Job States

- `queued`
- `processing`
- `completed`
- `failed`

## API Surface

- `POST /transcriptions`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/result`
- `GET /jobs`
- `GET /health`

## Transcript Result Shape

- `job_id`
- `status`
- `filename`
- `language`
- `detected_language`
- `duration_seconds`
- `text`
- `segments`
- `created_at`
- `started_at`
- `completed_at`

## Implementation Notes

- Refactor transcription logic into service-native functions instead of importing CLI-oriented code directly
- Convert any incoming audio to mono 16k WAV before Whisper
- Keep errors typed and service-safe
- Use structured logging instead of print-heavy stage output
- Add optional bearer-token auth via env var; if unset, auth is disabled

## Deployment Notes

- One API deployment
- One worker deployment
- One PVC
- One ClusterIP service
- One Traefik ingress
- The default worker deployment requests one NVIDIA GPU on `legion-server`

## Whisper Cache

- Store downloaded Whisper model files on the shared PVC
- Use `WHISPER_CACHE_DIR=/data/cache/whisper`
- Load the model once per worker process and reuse it across jobs
- Avoid redownloading model weights on pod restart when the PVC persists

## GPU Enablement Notes

- Host driver alone is not enough for k3s GPU pods
- `nvidia-container-toolkit` and `nvidia-container-runtime` must exist on the host
- k3s/containerd must be configured to use the NVIDIA runtime
- The NVIDIA device plugin must run with `runtimeClassName: nvidia` so the node advertises `nvidia.com/gpu`
- The default worker deployment uses `runtimeClassName: nvidia` and requests `nvidia.com/gpu: 1`

## Validation

- Local smoke test with an `.m4a` file
- Verify job creation, processing, result retrieval, and failure handling
