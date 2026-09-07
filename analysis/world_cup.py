import csv
import json
from datetime import datetime
from pathlib import Path


RESULTS_DIR = Path("data/results")
BROADCASTS_DIR = Path("data/broadcasts")
OUTPUT_DIR = Path("data/world_cup")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def duration_seconds(start: str, end: str) -> float:
    fmt = "%H:%M:%S"

    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime(end, fmt)

    return (end_dt - start_dt).total_seconds()

def get_broadcast_metadata(broadcast_id: str) -> dict:
    path = BROADCASTS_DIR / f"{broadcast_id}.json"

    if not path.exists():
        return {
            "broadcast_id": broadcast_id,
            "title": broadcast_id,
            "segments": [],
        }

    return load_json(path)


def build_world_cup_data() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    broadcasts = []
    segment_rows = []
    people_rows = []

    for broadcast_dir in sorted(RESULTS_DIR.iterdir()):
        if not broadcast_dir.is_dir():
            continue

        broadcast_id = broadcast_dir.name
        metadata = get_broadcast_metadata(broadcast_id)

        segment_lookup = {
            segment["name"]: segment
            for segment in metadata.get("segments", [])
        }

        broadcast_data = {
            "broadcast_id": broadcast_id,
            "title": metadata.get("title", broadcast_id),
            "segments": [],
        }

        for result_path in sorted(broadcast_dir.glob("*.json")):
            result = load_json(result_path)

            segment_name = result_path.stem
            segment_meta = segment_lookup.get(segment_name, {})

            label = segment_meta.get("label", segment_name)

            segment_duration = None
            if segment_meta.get("start") and segment_meta.get("end"):
                segment_duration = duration_seconds(
                segment_meta["start"],
                segment_meta["end"],
                )

            stats = result.get("stats", {})

            total_speech_time = sum(
                values.get("speech_time", 0)
                for values in stats.values()
            )

            total_words = sum(
                values.get("words", 0)
                for values in stats.values()
            )

            total_turns = sum(
                values.get("turns", 0)
                for values in stats.values()
            )

            participants = [
                person
                for person in stats
                if person != "Inslag"
            ]

            segment_data = {
                "name": segment_name,
                "label": label,
                "segment_duration": segment_duration,
                "total_speech_time": round(total_speech_time, 1),
                "words": total_words,
                "turns": total_turns,
                "participants": participants,
                "stats": stats,
            }

            broadcast_data["segments"].append(segment_data)

            segment_rows.append({
                "broadcast_id": broadcast_id,
                "title": metadata.get("title", broadcast_id),
                "segment": segment_name,
                "label": label,
                "segment_duration": segment_duration,
                "total_speech_time": round(total_speech_time, 1),
                "words": total_words,
                "turns": total_turns,
                "participants": ";".join(participants),
            })

            for person, values in stats.items():
                people_rows.append({
                    "broadcast_id": broadcast_id,
                    "title": metadata.get("title", broadcast_id),
                    "segment": segment_name,
                    "label": label,
                    "segment_duration": segment_duration,
                    "person": person,
                    "speech_time": values.get("speech_time", 0),
                    "share": values.get("share", 0),
                    "words": values.get("words", 0),
                    "turns": values.get("turns", 0),
                    "average_turn": values.get("average_turn", 0),
                    "median_turn": values.get("median_turn", 0),
                    "longest_turn": values.get("longest_turn", 0),
                    "words_per_minute": values.get("words_per_minute", 0),
                })

        broadcasts.append(broadcast_data)

    summary = {
        "broadcast_count": len(broadcasts),
        "segment_count": len(segment_rows),
        "total_speech_time": round(
            sum(row["total_speech_time"] for row in segment_rows),
            1,
        ),
        "total_hours": round(
            sum(row["total_speech_time"] for row in segment_rows) / 3600,
            2,
        ),
        "total_words": sum(
            row["words"]
            for row in segment_rows
        ),
        "total_turns": sum(
            row["turns"]
            for row in segment_rows
        ),
        "broadcasts": broadcasts,
        "total_segment_duration": round(
            sum(row["segment_duration"] or 0 for row in segment_rows),
            1,
        ),
        "total_segment_hours": round(
            sum(row["segment_duration"] or 0 for row in segment_rows) / 3600,
            2,
        ),
    }

    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    segments_path = OUTPUT_DIR / "segments.csv"
    with segments_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "broadcast_id",
                "title",
                "segment",
                "label",
                "segment_duration",
                "total_speech_time",
                "words",
                "turns",
                "participants",
            ],
        )
        writer.writeheader()
        writer.writerows(segment_rows)

    people_path = OUTPUT_DIR / "people.csv"
    with people_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "broadcast_id",
                "title",
                "segment",
                "label",
                "segment_duration",
                "person",
                "speech_time",
                "share",
                "words",
                "turns",
                "average_turn",
                "median_turn",
                "longest_turn",
                "words_per_minute",
            ],
        )
        writer.writeheader()
        writer.writerows(people_rows)

    print(f"Saved: {summary_path}")
    print(f"Saved: {segments_path}")
    print(f"Saved: {people_path}")

    print()
    print(f"Broadcasts: {summary['broadcast_count']}")
    print(f"Segments: {summary['segment_count']}")
    print(f"Hours: {summary['total_hours']}")
    print(f"Words: {summary['total_words']}")
    print(f"Turns: {summary['total_turns']}")


if __name__ == "__main__":
    build_world_cup_data()