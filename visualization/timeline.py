from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter


DEFAULT_COLORS = [
    "#4E79A7",
    "#E15759",
    "#59A14F",
    "#F28E2B",
    "#B07AA1",
    "#76B7B2",
    "#EDC948",
    "#9C755F",
    "#BAB0AC",
    "#86BCB6",
]

def format_x_axis_as_minutes(ax, max_seconds: float) -> None:
    if max_seconds <= 15 * 60:
        interval = 60
    else:
        interval = 5 * 60

    ax.set_xlabel("Minutes")
    ax.xaxis.set_major_locator(MultipleLocator(interval))
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: f"{int(x // 60)}")
    )

def sort_speakers(speakers: set[str], people: dict) -> list[str]:
    def sort_key(name: str):
        person = people.get(name, {})
        return (
            person.get("order", 999),
            name,
        )

    return sorted(speakers, key=sort_key)

def create_speaker_timeline(
    merged_segments: list[dict],
    output_png: str,
    speaker_map: dict | None = None,
    people: dict | None = None,
) -> None:
    speaker_map = speaker_map or {}
    people = people or {}

    print("\nTimeline received:")
    print(speaker_map)
    print(people.keys())

    def display_name(raw_speaker: str) -> str:
        return speaker_map.get(raw_speaker, raw_speaker)

    def display_color(name: str) -> str:
        return people.get(name, {}).get("color", "#999999")

    timeline_segments = [
        {
            **segment,
            "display_name": display_name(segment["speaker"]),
        }
        for segment in merged_segments
    ]

    speakers = sort_speakers(
        {s["display_name"] for s in timeline_segments},
        people,
    )

    speaker_to_y = {speaker: i for i, speaker in enumerate(speakers)}

    fig_height = max(3, 0.7 * len(speakers) + 1.5)
    fig, ax = plt.subplots(figsize=(14, fig_height))

    for segment in timeline_segments:
        speaker = segment["display_name"]
        y = speaker_to_y[speaker]
        start = segment["start"]
        duration = segment["end"] - segment["start"]
        color = display_color(speaker)

        ax.broken_barh(
            [(start, duration)],
            (y - 0.35, 0.7),
            facecolors=color,
        )

    ax.set_yticks(list(speaker_to_y.values()))
    ax.set_yticklabels(speakers)
    ax.invert_yaxis()
    max_seconds = max(s["end"] for s in timeline_segments) if timeline_segments else 0
    format_x_axis_as_minutes(ax, max_seconds)
    ax.set_title("Speaker timeline")
    ax.grid(axis="x", alpha=0.3)

    if timeline_segments:
        ax.set_xlim(0, max_seconds)

    Path(output_png).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_png, dpi=150)
    plt.close(fig)