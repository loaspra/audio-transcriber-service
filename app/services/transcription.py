from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.ffmpeg import convert_to_wav

_model: Any | None = None


def load_model() -> Any:
    global _model
    if _model is None:
        import whisper  # type: ignore

        _model = whisper.load_model(settings.whisper_model)
    return _model


def format_segments(result: dict[str, Any]) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    for segment in result.get("segments", []):
        text = str(segment.get("text", "")).strip()
        if not text or len(text) < 2:
            continue
        item = {
            "start": segment["start"],
            "end": segment["end"],
            "text": text,
            "words": [],
        }
        for word in segment.get("words", []):
            item["words"].append(
                {
                    "word": word["word"],
                    "start": word["start"],
                    "end": word["end"],
                }
            )
        segments.append(item)
    return segments


def transcribe_audio_file(input_path: Path, wav_path: Path, language: str | None) -> dict[str, Any]:
    convert_to_wav(input_path, wav_path)
    model = load_model()
    result = model.transcribe(
        str(wav_path),
        language=language or settings.default_language,
        verbose=False,
        word_timestamps=True,
        hallucination_silence_threshold=1.0,
        no_speech_threshold=0.6,
        logprob_threshold=-1.0,
        condition_on_previous_text=False,
    )
    segments = format_segments(result)
    duration_seconds = segments[-1]["end"] if segments else 0.0
    return {
        "segments": segments,
        "detected_language": result.get("language"),
        "duration_seconds": duration_seconds,
    }
