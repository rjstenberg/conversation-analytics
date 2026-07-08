import json
from pathlib import Path

import mlx_whisper

from config import WHISPER_MODEL, LANGUAGE


def transcribe_audio(audio_path: str, output_path: str | None = None) -> dict:
    audio = Path(audio_path)

    if not audio.exists():
        raise FileNotFoundError(f"Audio file not found: {audio}")

    kwargs = {
        "path_or_hf_repo": WHISPER_MODEL,
    }

    if LANGUAGE:
        kwargs["language"] = LANGUAGE

    result = mlx_whisper.transcribe(
        str(audio),
        **kwargs,
    )

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return result