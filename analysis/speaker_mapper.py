import json
import re
from collections import defaultdict
from pathlib import Path


def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def shorten(text: str, max_length: int = 120) -> str:
    text = " ".join(text.split())
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\wÅÄÖåäö']+\b", text))


def load_known_people(path: str = "data/people.json") -> list[str]:
    people_path = Path(path)
    if not people_path.exists():
        return []

    people = json.loads(people_path.read_text(encoding="utf-8"))
    return list(people.keys())


def raw_speaker_stats(segments: list[dict]) -> dict:
    stats = defaultdict(lambda: {
        "speech_time": 0.0,
        "segments": 0,
        "words": 0,
    })

    for segment in segments:
        speaker = segment["speaker"]
        stats[speaker]["speech_time"] += segment.get("duration", 0)
        stats[speaker]["segments"] += 1
        stats[speaker]["words"] += word_count(segment.get("text", ""))

    for values in stats.values():
        values["speech_time"] = round(values["speech_time"], 1)

    return dict(stats)


def examples_for_speaker(
    segments: list[dict],
    speaker: str,
    max_examples: int = 4,
) -> list[dict]:
    speaker_segments = [
        segment for segment in segments
        if segment.get("speaker") == speaker
    ]

    speaker_segments = sorted(
        speaker_segments,
        key=lambda s: s.get("duration", 0),
        reverse=True,
    )

    return speaker_segments[:max_examples]


def create_speaker_map_from_results(results_json: str, output_json: str) -> None:
    data = json.loads(Path(results_json).read_text(encoding="utf-8"))
    segments = data.get("segments", [])
    stats = raw_speaker_stats(segments)
    known_people = load_known_people()

    speaker_map = {}

    print("\nKnown people/groups:")
    print(", ".join(known_people) if known_people else "(none found)")

    print("\nFound speakers:\n")

    for speaker, values in sorted(
        stats.items(),
        key=lambda x: x[1]["speech_time"],
        reverse=True,
    ):
        print("=" * 60)
        print(f"{speaker}")
        print(f"  speech_time: {values['speech_time']} s")
        print(f"  words: {values['words']}")
        print(f"  segments: {values['segments']}")

        print("\nExamples:")
        examples = examples_for_speaker(segments, speaker)

        if examples:
            for example in examples:
                start = format_time(example["start"])
                text = shorten(example.get("text", ""))
                print(f"  {start}  {text}")
        else:
            print("  No examples found.")

        default = "Inslag" if values["speech_time"] < 60 else speaker
        answer = input(f"\nName/group [{default}]: ").strip()

        speaker_map[speaker] = answer or default
        print()

    path = Path(output_json)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(speaker_map, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved speaker map: {path}")