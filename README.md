# Audio Transcriber Service

Async audio upload and transcription service built for self-hosted deployment on k3s.

## Features

- Audio-only upload API
- Async job lifecycle with polling
- SQLite-backed job state
- Shared local storage for uploads and results
- Whisper transcription with `large-v3-turbo`
- Persistent Whisper model cache support
- Separate API and worker process modes

## API

- `POST /transcriptions`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/result`
- `GET /health`

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
python -m app.workers.poller
```

## Deployment

Kubernetes manifests are under `k8s/base/`.

- Base deployment: `kubectl apply -k k8s/base`
- GPU-ready overlay after NVIDIA runtime is configured on the cluster: `kubectl apply -k k8s/overlays/gpu`
- Tailnet/backend access via NodePort: `http://<legion-tailnet-ip>:30800`
