from collections import defaultdict
import re
from statistics import median


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\wÅÄÖåäö']+\b", text))


def merge_into_turns(segments: list[dict], max_gap: float = 1.0) -> list[dict]:
    turns = []

    for segment in segments:
        if not turns:
            turns.append(segment.copy())
            continue

        previous = turns[-1]

        same_speaker = previous["speaker"] == segment["speaker"]
        close_enough = segment["start"] - previous["end"] <= max_gap

        if same_speaker and close_enough:
            previous["end"] = segment["end"]
            previous["duration"] = round(previous["end"] - previous["start"], 2)
            previous["text"] = f"{previous.get('text', '')} {segment.get('text', '')}".strip()
        else:
            turns.append(segment.copy())

    return turns

def speaker_statistics(
    merged_segments: list[dict],
    speaker_map: dict | None = None,
) -> dict:
    speaker_map = speaker_map or {}
    turns = merge_into_turns(merged_segments)

    stats = defaultdict(lambda: {
        "speech_time": 0.0,
        "segments": 0,
        "words": 0,
        "turns": 0,
        "longest_turn": 0.0,
        "turn_lengths": [],
    })

    for segment in turns:
        raw_speaker = segment["speaker"]
        speaker = speaker_map.get(raw_speaker, raw_speaker)

        stats[speaker]["speech_time"] += segment["duration"]
        stats[speaker]["segments"] += 1
        stats[speaker]["words"] += word_count(segment["text"])

        stats[speaker]["turns"] += 1
        stats[speaker]["longest_turn"] = max(
            stats[speaker]["longest_turn"],
            segment["duration"],
        )
        duration = segment["duration"]

        stats[speaker]["turn_lengths"].append(duration)

        stats[speaker]["longest_turn"] = max(
            stats[speaker]["longest_turn"],
            duration,
        )

    total = sum(v["speech_time"] for v in stats.values())

    for values in stats.values():
        values["speech_time"] = round(values["speech_time"], 1)
        values["share"] = round(values["speech_time"] / total * 100, 1)
        values["average_turn"] = round(
            values["speech_time"] / values["turns"],
            1,
        ) if values["turns"] else 0

        values["longest_turn"] = round(values["longest_turn"], 1)

        values["average_turn"] = round(
            values["speech_time"] / values["turns"],
            1,
        )

        values["median_turn"] = round(
            median(values["turn_lengths"]),
            1,
        )

        values["longest_turn"] = round(
            values["longest_turn"],
            1,
        )

        values["words_per_minute"] = round(
            values["words"] / (values["speech_time"] / 60),
            1,
        )

    return dict(stats)