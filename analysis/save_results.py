import json
from pathlib import Path


def save_analysis_results(
    output_file: str,
    stats: dict,
    merged_segments: list[dict],
    speaker_map: dict,
    timeline: str | None = None,
) -> None:
    output = {
        "stats": stats,
        "speaker_map": speaker_map,
        "segments": merged_segments,
        "timeline": timeline,
    }

    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )