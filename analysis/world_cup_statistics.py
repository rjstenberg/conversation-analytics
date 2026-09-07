import json
from collections import defaultdict
from pathlib import Path
from statistics import median


SUMMARY_PATH = Path("data/world_cup/summary.json")
OUTPUT_PATH = Path("data/world_cup/statistics.json")

OVERALL_WIN_EXCLUDED = set()
EXPERT_WIN_EXCLUDED = {"Inslag", "Andre"}


def load_summary() -> dict:
    return json.loads(
        SUMMARY_PATH.read_text(encoding="utf-8")
    )


def add_wins(
    eligible: dict,
    people: dict,
    share_key: str,
    longest_key: str,
) -> None:
    if not eligible:
        return

    max_speech_time = max(
        values.get("speech_time", 0)
        for values in eligible.values()
    )

    for person, values in eligible.items():
        if values.get("speech_time", 0) == max_speech_time:
            people[person][share_key] += 1

    max_longest_turn = max(
        values.get("longest_turn", 0)
        for values in eligible.values()
    )

    for person, values in eligible.items():
        if values.get("longest_turn", 0) == max_longest_turn:
            people[person][longest_key] += 1


def calculate_statistics(summary: dict) -> dict:
    total_broadcasts = summary["broadcast_count"]
    total_segments = summary["segment_count"]

    people = defaultdict(
        lambda: {
            "broadcasts": set(),
            "segments": 0,
            "speech_time": 0.0,
            "words": 0,
            "turns": 0,
            "turn_lengths": [],
            "longest_turn": 0.0,
            "segment_shares": [],

            "segment_share_wins": 0,
            "segment_longest_turn_wins": 0,
            "broadcast_share_wins": 0,
            "broadcast_longest_turn_wins": 0,

            "expert_segment_share_wins": 0,
            "expert_segment_longest_turn_wins": 0,
            "expert_broadcast_share_wins": 0,
            "expert_broadcast_longest_turn_wins": 0,
        }
    )

    segment_type_counts = defaultdict(int)
    segment_type_durations = defaultdict(float)
    total_segment_duration = 0.0
    total_speech_time = 0.0
    total_words = 0
    total_turns = 0

    broadcast_people = defaultdict(
        lambda: defaultdict(
            lambda: {
                "speech_time": 0.0,
                "longest_turn": 0.0,
            }
        )
    )

    for broadcast in summary["broadcasts"]:
        broadcast_id = broadcast["broadcast_id"]

        for segment in broadcast["segments"]:
            segment_name = segment["name"]
            stats = segment["stats"]

            segment_type_counts[segment_name] += 1

            segment_duration = segment.get("segment_duration") or 0

            total_segment_duration += segment_duration
            segment_type_durations[segment_name] += segment_duration

            for person, values in stats.items():
                speech_time = values.get("speech_time", 0)
                words = values.get("words", 0)
                turns = values.get("turns", 0)
                turn_lengths = values.get("turn_lengths", [])
                longest_turn = values.get("longest_turn", 0)
                share = values.get("share", 0)

                people[person]["broadcasts"].add(broadcast_id)
                people[person]["segments"] += 1
                people[person]["speech_time"] += speech_time
                people[person]["words"] += words
                people[person]["turns"] += turns
                people[person]["turn_lengths"].extend(turn_lengths)
                people[person]["segment_shares"].append(share)

                people[person]["longest_turn"] = max(
                    people[person]["longest_turn"],
                    longest_turn,
                )

                total_speech_time += speech_time
                total_words += words
                total_turns += turns

                broadcast_people[broadcast_id][person]["speech_time"] += (
                    speech_time
                )

                broadcast_people[broadcast_id][person]["longest_turn"] = max(
                    broadcast_people[broadcast_id][person]["longest_turn"],
                    longest_turn,
                )

            overall_eligible = {
                person: values
                for person, values in stats.items()
                if person not in OVERALL_WIN_EXCLUDED
            }

            add_wins(
                overall_eligible,
                people,
                "segment_share_wins",
                "segment_longest_turn_wins",
            )

            expert_eligible = {
                person: values
                for person, values in stats.items()
                if person not in EXPERT_WIN_EXCLUDED
            }

            add_wins(
                expert_eligible,
                people,
                "expert_segment_share_wins",
                "expert_segment_longest_turn_wins",
            )

    # Broadcast-level wins
    for person_stats in broadcast_people.values():
        overall_eligible = {
            person: values
            for person, values in person_stats.items()
            if person not in OVERALL_WIN_EXCLUDED
        }

        add_wins(
            overall_eligible,
            people,
            "broadcast_share_wins",
            "broadcast_longest_turn_wins",
        )

        expert_eligible = {
            person: values
            for person, values in person_stats.items()
            if person not in EXPERT_WIN_EXCLUDED
        }

        add_wins(
            expert_eligible,
            people,
            "expert_broadcast_share_wins",
            "expert_broadcast_longest_turn_wins",
        )

    final_people = {}

    for person, values in people.items():
        broadcasts = len(values["broadcasts"])
        segments = values["segments"]
        speech_time = values["speech_time"]
        words = values["words"]
        turns = values["turns"]
        turn_lengths = values["turn_lengths"]
        segment_shares = values["segment_shares"]

        person_stats = {
            "broadcasts": broadcasts,
            "broadcast_presence_rate": round(
                broadcasts / total_broadcasts * 100,
                1,
            ) if total_broadcasts else 0,

            "segments": segments,
            "segment_presence_rate": round(
                segments / total_segments * 100,
                1,
            ) if total_segments else 0,

            "speech_time": round(speech_time, 1),
            "hours": round(speech_time / 3600, 2),

            "tournament_speaking_share": round(
                speech_time / total_speech_time * 100,
                1,
            ) if total_speech_time else 0,

            "average_segment_share_when_present": round(
                sum(segment_shares) / len(segment_shares),
                1,
            ) if segment_shares else 0,

            "words": words,
            "turns": turns,

            "average_turn": round(
                speech_time / turns,
                1,
            ) if turns else 0,

            "median_turn": round(
                median(turn_lengths),
                1,
            ) if turn_lengths else 0,

            "longest_turn": round(
                values["longest_turn"],
                1,
            ),

            "words_per_minute": round(
                words / (speech_time / 60),
                1,
            ) if speech_time else 0,
        }

        # Overall wins
        for key in [
            "segment_share_wins",
            "segment_longest_turn_wins",
            "broadcast_share_wins",
            "broadcast_longest_turn_wins",
            "expert_segment_share_wins",
            "expert_segment_longest_turn_wins",
            "expert_broadcast_share_wins",
            "expert_broadcast_longest_turn_wins",
        ]:
            person_stats[key] = values[key]

        person_stats["segment_share_win_rate"] = round(
            values["segment_share_wins"] / segments * 100,
            1,
        ) if segments else 0

        person_stats["segment_longest_turn_win_rate"] = round(
            values["segment_longest_turn_wins"] / segments * 100,
            1,
        ) if segments else 0

        person_stats["broadcast_share_win_rate"] = round(
            values["broadcast_share_wins"] / broadcasts * 100,
            1,
        ) if broadcasts else 0

        person_stats["broadcast_longest_turn_win_rate"] = round(
            values["broadcast_longest_turn_wins"] / broadcasts * 100,
            1,
        ) if broadcasts else 0

        # Expert-only rates only make sense for experts
        if person not in EXPERT_WIN_EXCLUDED:
            person_stats["expert_segment_share_win_rate"] = round(
                values["expert_segment_share_wins"] / segments * 100,
                1,
            ) if segments else 0

            person_stats["expert_segment_longest_turn_win_rate"] = round(
                values["expert_segment_longest_turn_wins"]
                / segments * 100,
                1,
            ) if segments else 0

            person_stats["expert_broadcast_share_win_rate"] = round(
                values["expert_broadcast_share_wins"]
                / broadcasts * 100,
                1,
            ) if broadcasts else 0

            person_stats["expert_broadcast_longest_turn_win_rate"] = round(
                values["expert_broadcast_longest_turn_wins"]
                / broadcasts * 100,
                1,
            ) if broadcasts else 0

        final_people[person] = person_stats

    return {
        "tournament": {
            "broadcasts": total_broadcasts,
            "segments": total_segments,
            "segment_types": dict(
                sorted(segment_type_counts.items())
            ),
            "segment_type_average_duration": {
                name: round(
                    segment_type_durations[name] / count,
                    1,
                )
                for name, count in segment_type_counts.items()
                if count
            },
            "segment_hours": round(
                total_segment_duration / 3600,
                2,
            ),
            "speech_hours": round(
                total_speech_time / 3600,
                2,
            ),
            "words": total_words,
            "turns": total_turns,
        },
        "people": final_people,
    }


def print_statistics(result: dict) -> None:
    tournament = result["tournament"]

    print("\nWORLD CUP TOTALS")
    print("=" * 60)
    print(f"Broadcasts: {tournament['broadcasts']}")
    print(f"Segments: {tournament['segments']}")
    print(f"Analyzed hours: {tournament['segment_hours']}")
    print(f"Speech hours: {tournament['speech_hours']}")
    print(f"Words: {tournament['words']}")
    print(f"Turns: {tournament['turns']}")

    print("\nSegments by type:")
    for name, count in tournament["segment_types"].items():
        print(f"  {name}: {count}")

    print("\nPERSON STATISTICS")
    print("=" * 60)

    for person, stats in sorted(
        result["people"].items(),
        key=lambda item: item[1]["speech_time"],
        reverse=True,
    ):
        print(f"\n{person}")
        print(
            f"  Broadcasts: {stats['broadcasts']}/"
            f"{tournament['broadcasts']}"
        )
        print(
            f"  Segments: {stats['segments']}/"
            f"{tournament['segments']}"
        )
        print(f"  Hours: {stats['hours']}")
        print(
            f"  Tournament speaking share: "
            f"{stats['tournament_speaking_share']}%"
        )
        print(
            f"  Avg share when present: "
            f"{stats['average_segment_share_when_present']}%"
        )
        print(f"  Average turn: {stats['average_turn']} s")
        print(f"  Median turn: {stats['median_turn']} s")
        print(f"  Longest turn: {stats['longest_turn']} s")
        print(f"  Words/min: {stats['words_per_minute']}")

        if person not in EXPERT_WIN_EXCLUDED:
            print(
                f"  Expert segment share wins: "
                f"{stats['expert_segment_share_wins']} "
                f"({stats['expert_segment_share_win_rate']}%)"
            )
            print(
                f"  Expert longest-turn wins: "
                f"{stats['expert_segment_longest_turn_wins']} "
                f"({stats['expert_segment_longest_turn_win_rate']}%)"
            )

        print("\nÖVERGRIPANDE MÅTT")
        print("=" * 90)

        print(
            f"{'Person':<12}"
            f"{'Segment':^32}"
            f"{'Sändning':^32}"
        )

        print(
            f"{'':<12}"
            f"{'Högst andel':>16}"
            f"{'Längst prata':>16}"
            f"{'Högst andel':>16}"
            f"{'Längst prata':>16}"
        )

        for person, stats in sorted(
            result["people"].items(),
            key=lambda item: item[1]["speech_time"],
            reverse=True,
        ):
            print(
                f"{person:<12}"
                f"{stats['segment_share_wins']:>4}"
                f" ({stats['segment_share_win_rate']:>5.1f}%)"
                f"{stats['segment_longest_turn_wins']:>4}"
                f" ({stats['segment_longest_turn_win_rate']:>5.1f}%)"
                f"{stats['broadcast_share_wins']:>4}"
                f" ({stats['broadcast_share_win_rate']:>5.1f}%)"
                f"{stats['broadcast_longest_turn_wins']:>4}"
                f" ({stats['broadcast_longest_turn_win_rate']:>5.1f}%)"
            )


def main() -> None:
    summary = load_summary()
    result = calculate_statistics(summary)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print_statistics(result)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()