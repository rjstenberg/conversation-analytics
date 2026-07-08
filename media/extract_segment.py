import subprocess
from pathlib import Path


def extract_audio_segment(
    source_audio: str,
    output_audio: str,
    start: str,
    end: str,
) -> None:
    Path(output_audio).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", source_audio,
        "-ss", start,
        "-to", end,
        "-ac", "1",
        "-ar", "16000",
        output_audio,
    ]

    subprocess.run(cmd, check=True)