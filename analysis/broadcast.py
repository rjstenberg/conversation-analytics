import json
from pathlib import Path


def load_broadcast(path: str) -> dict:
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def get_segments(broadcast: dict) -> list[dict]:
    return broadcast["segments"]