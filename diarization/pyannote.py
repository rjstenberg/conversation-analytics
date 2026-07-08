import json
from pathlib import Path

from pyannote.audio import Pipeline


def cache_path_for(audio_file: str, cache_dir: str | None = None) -> Path:
    audio = Path(audio_file)

    if cache_dir:
        return Path(cache_dir) / f"{audio.stem}.json"

    return Path("data/diarization") / f"{audio.stem}.json"


def load_cached_diarization(cache_path: Path) -> list[dict]:
    return json.loads(cache_path.read_text(encoding="utf-8"))


def save_cached_diarization(cache_path: Path, segments: list[dict]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(segments, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_pyannote(audio_file: str) -> list[dict]:
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-community-1"
    )

    output = pipeline(audio_file)
    diarization = output.speaker_diarization

    segments = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = round(turn.start, 2)
        end = round(turn.end, 2)

        segments.append({
            "speaker": speaker,
            "start": start,
            "end": end,
            "duration": round(end - start, 2),
        })

    return segments


def diarize_audio(audio_file: str, cache_dir: str | None = None) -> list[dict]:
    cache_path = cache_path_for(audio_file, cache_dir)

    if cache_path.exists():
        print(f"Using cached diarization: {cache_path}")
        return load_cached_diarization(cache_path)

    print("Running pyannote diarization...")
    segments = run_pyannote(audio_file)
    save_cached_diarization(cache_path, segments)

    return segments