import json

from app.core.config import settings


def build_text_from_segments(segments: list[dict[str, object]]) -> str:
    return " ".join(str(segment["text"]).strip() for segment in segments).strip()


def save_transcript_result(job_id: str, payload: dict[str, object]) -> str:
    output_path = settings.result_dir / f"{job_id}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return str(output_path)


def load_transcript_result(job_id: str) -> dict[str, object]:
    result_path = settings.result_dir / f"{job_id}.json"
    with result_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
