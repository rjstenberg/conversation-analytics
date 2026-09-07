import json
from pathlib import Path

STATISTICS_PATH = Path("data/world_cup/statistics.json")
OUTPUT_PATH = Path(
    "data/reports/world-cup/world-cup-report.html"
)

EXCLUDED_FROM_EXPERTS = {"Andre", "Inslag"}

SEGMENT_ORDER = [
    "pre_match",
    "halftime",
    "post_regulation",
    "post_extra_time",
    "post_match",
]

SEGMENT_LABELS = {
    "pre_match": "Uppsnack",
    "halftime": "Halvtid",
    "post_regulation": "Efter ordinarie tid",
    "post_extra_time": "Efter förlängning",
    "post_match": "Efter match",
}


def load_statistics() -> dict:
    return json.loads(
        STATISTICS_PATH.read_text(encoding="utf-8")
    )


def max_value(people: dict, key: str):
    values = [
        stats.get(key)
        for stats in people.values()
        if stats.get(key) is not None
    ]

    return max(values) if values else None


def highlight_class(value, maximum) -> str:
    if maximum is not None and value == maximum:
        return ' class="highlight"'

    return ""


def format_duration(seconds: float) -> str:
    seconds = int(round(seconds))

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    return f"{minutes}:{seconds:02d}"


def format_number(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def segment_type_table(
    segment_types: dict,
    average_durations: dict,
) -> str:
    rows = ""

    for name in SEGMENT_ORDER:
        if name not in segment_types:
            continue

        count = segment_types[name]
        average_duration = average_durations.get(name, 0)

        rows += f"""
        <tr>
            <td>{SEGMENT_LABELS[name]}</td>
            <td>{count}</td>
            <td>{format_duration(average_duration)}</td>
        </tr>
        """

    return f"""
    <table class="segment-table">
        <thead>
            <tr>
                <th>Segmenttyp</th>
                <th>Antal</th>
                <th>Genomsnittlig längd</th>
            </tr>
        </thead>

        <tbody>
            {rows}
        </tbody>
    </table>
    """


def person_table(people: dict) -> str:
    max_broadcasts = max_value(
        people,
        "broadcasts",
    )
    max_segments = max_value(
        people,
        "segments",
    )
    max_hours = max_value(
        people,
        "hours",
    )
    max_tournament_share = max_value(
        people,
        "tournament_speaking_share",
    )
    max_avg_share = max_value(
        people,
        "average_segment_share_when_present",
    )
    max_avg_turn = max_value(
        people,
        "average_turn",
    )
    max_median_turn = max_value(
        people,
        "median_turn",
    )
    max_longest_turn = max_value(
        people,
        "longest_turn",
    )
    max_wpm = max_value(
        people,
        "words_per_minute",
    )
    max_segment_share_rate = max_value(
        people,
        "segment_share_win_rate",
    )
    max_broadcast_share_rate = max_value(
        people,
        "broadcast_share_win_rate",
    )

    rows = ""

    for person, stats in sorted(
        people.items(),
        key=lambda item: item[1]["speech_time"],
        reverse=True,
    ):
        rows += f"""
        <tr>
            <td>{person}</td>

            <td{highlight_class(
                stats["broadcasts"],
                max_broadcasts,
            )}>
                {stats["broadcasts"]}
            </td>

            <td{highlight_class(
                stats["segments"],
                max_segments,
            )}>
                {stats["segments"]}
            </td>

            <td{highlight_class(
                stats["hours"],
                max_hours,
            )}>
                {stats["hours"]}
            </td>

            <td{highlight_class(
                stats["tournament_speaking_share"],
                max_tournament_share,
            )}>
                {stats["tournament_speaking_share"]}%
            </td>

            <td{highlight_class(
                stats["average_segment_share_when_present"],
                max_avg_share,
            )}>
                {stats["average_segment_share_when_present"]}%
            </td>

            <td{highlight_class(
                stats["average_turn"],
                max_avg_turn,
            )}>
                {stats["average_turn"]}
            </td>

            <td{highlight_class(
                stats["median_turn"],
                max_median_turn,
            )}>
                {stats["median_turn"]}
            </td>

            <td{highlight_class(
                stats["longest_turn"],
                max_longest_turn,
            )}>
                {stats["longest_turn"]}
            </td>

            <td{highlight_class(
                stats["words_per_minute"],
                max_wpm,
            )}>
                {stats["words_per_minute"]}
            </td>

            <td{highlight_class(
                stats["segment_share_win_rate"],
                max_segment_share_rate,
            )}>
                {stats["segment_share_wins"]}
                ({stats["segment_share_win_rate"]}%)
            </td>

            <td{highlight_class(
                stats["broadcast_share_win_rate"],
                max_broadcast_share_rate,
            )}>
                {stats["broadcast_share_wins"]}
                ({stats["broadcast_share_win_rate"]}%)
            </td>
        </tr>
        """

    return f"""
    <table>
        <thead>
            <tr>
                <th rowspan="2">Person</th>
                <th rowspan="2">Sändningar</th>
                <th rowspan="2">Segment</th>
                <th rowspan="2">Taltid (h)</th>
                <th rowspan="2">Andel (%)</th>
                <th rowspan="2">Snittandel (%)</th>
                <th rowspan="2">Snittprata (s)</th>
                <th rowspan="2">Median (s)</th>
                <th rowspan="2">Längst (s)</th>
                <th rowspan="2">Ord/min</th>

                <th class="group-header">
                    Segment
                </th>

                <th class="group-header">
                    Sändning
                </th>
            </tr>

            <tr>
                <th>Högst andel</th>
                <th>Högst andel</th>
            </tr>
        </thead>

        <tbody>
            {rows}
        </tbody>
    </table>
    """


def expert_table(people: dict) -> str:
    experts = {
        person: stats
        for person, stats in people.items()
        if person not in EXCLUDED_FROM_EXPERTS
    }

    max_broadcasts = max_value(
        experts,
        "broadcasts",
    )
    max_segments = max_value(
        experts,
        "segments",
    )
    max_hours = max_value(
        experts,
        "hours",
    )
    max_avg_share = max_value(
        experts,
        "average_segment_share_when_present",
    )
    max_avg_turn = max_value(
        experts,
        "average_turn",
    )
    max_median_turn = max_value(
        experts,
        "median_turn",
    )
    max_longest_turn = max_value(
        experts,
        "longest_turn",
    )
    max_wpm = max_value(
        experts,
        "words_per_minute",
    )
    max_segment_share_rate = max_value(
        experts,
        "expert_segment_share_win_rate",
    )
    max_segment_longest_rate = max_value(
        experts,
        "expert_segment_longest_turn_win_rate",
    )
    max_broadcast_share_rate = max_value(
        experts,
        "expert_broadcast_share_win_rate",
    )
    max_broadcast_longest_rate = max_value(
        experts,
        "expert_broadcast_longest_turn_win_rate",
    )

    rows = ""

    for person, stats in sorted(
        experts.items(),
        key=lambda item: item[1]["speech_time"],
        reverse=True,
    ):
        rows += f"""
        <tr>
            <td>{person}</td>

            <td{highlight_class(
                stats["broadcasts"],
                max_broadcasts,
            )}>
                {stats["broadcasts"]}
            </td>

            <td{highlight_class(
                stats["segments"],
                max_segments,
            )}>
                {stats["segments"]}
            </td>

            <td{highlight_class(
                stats["hours"],
                max_hours,
            )}>
                {stats["hours"]}
            </td>

            <td{highlight_class(
                stats["average_segment_share_when_present"],
                max_avg_share,
            )}>
                {stats["average_segment_share_when_present"]}%
            </td>

            <td{highlight_class(
                stats["average_turn"],
                max_avg_turn,
            )}>
                {stats["average_turn"]}
            </td>

            <td{highlight_class(
                stats["median_turn"],
                max_median_turn,
            )}>
                {stats["median_turn"]}
            </td>

            <td{highlight_class(
                stats["longest_turn"],
                max_longest_turn,
            )}>
                {stats["longest_turn"]}
            </td>

            <td{highlight_class(
                stats["words_per_minute"],
                max_wpm,
            )}>
                {stats["words_per_minute"]}
            </td>

            <td{highlight_class(
                stats["expert_segment_share_win_rate"],
                max_segment_share_rate,
            )}>
                {stats["expert_segment_share_wins"]}
                ({stats["expert_segment_share_win_rate"]}%)
            </td>

            <td{highlight_class(
                stats["expert_segment_longest_turn_win_rate"],
                max_segment_longest_rate,
            )}>
                {stats["expert_segment_longest_turn_wins"]}
                ({stats["expert_segment_longest_turn_win_rate"]}%)
            </td>

            <td{highlight_class(
                stats["expert_broadcast_share_win_rate"],
                max_broadcast_share_rate,
            )}>
                {stats["expert_broadcast_share_wins"]}
                ({stats["expert_broadcast_share_win_rate"]}%)
            </td>

            <td{highlight_class(
                stats["expert_broadcast_longest_turn_win_rate"],
                max_broadcast_longest_rate,
            )}>
                {stats["expert_broadcast_longest_turn_wins"]}
                ({stats["expert_broadcast_longest_turn_win_rate"]}%)
            </td>
        </tr>
        """

    return f"""
    <table class="expert-table">
        <thead>
            <tr>
                <th rowspan="2">Expert</th>
                <th rowspan="2">Sändningar</th>
                <th rowspan="2">Segment</th>
                <th rowspan="2">Taltid (h)</th>
                <th rowspan="2">Snittandel (%)</th>
                <th rowspan="2">Snittprata (s)</th>
                <th rowspan="2">Median (s)</th>
                <th rowspan="2">Längst (s)</th>
                <th rowspan="2">Ord/min</th>

                <th colspan="2" class="group-header">
                    Segment
                </th>

                <th colspan="2" class="group-header">
                    Sändning
                </th>
            </tr>

            <tr>
                <th>Högst andel</th>
                <th>Längst prata</th>
                <th>Högst andel</th>
                <th>Längst prata</th>
            </tr>
        </thead>

        <tbody>
            {rows}
        </tbody>
    </table>
    """


def create_report() -> None:
    result = load_statistics()

    tournament = result["tournament"]
    people = result["people"]

    html = f"""
    <!doctype html>

    <html lang="sv">

    <head>
        <meta charset="utf-8">

        <title>VM 2026 - Studioanalys SVT</title>

        <style>
            body {{
                font-family: system-ui, sans-serif;
                max-width: 1500px;
                margin: 40px auto;
                padding: 0 24px;
                color: #222;
                line-height: 1.45;
            }}

            h1 {{
                margin-bottom: 6px;
            }}

            h2 {{
                margin-top: 48px;
                margin-bottom: 16px;
            }}

            .subtitle {{
                margin-top: 0;
                margin-bottom: 30px;
                color: #666;
                font-size: 1.05rem;
            }}

            .summary {{
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(160px, 1fr));
                gap: 16px;
                margin: 24px 0 36px;
            }}

            .metric {{
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 16px;
            }}

            .metric strong {{
                display: block;
                font-size: 1.8rem;
                margin-bottom: 2px;
            }}

            .metric span {{
                color: #666;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 0 0 14px;
            }}

            th,
            td {{
                border: 1px solid #ddd;
                padding: 9px 12px;
                text-align: right;
                vertical-align: middle;
            }}

            th:first-child,
            td:first-child {{
                text-align: left;
            }}

            th {{
                background: #f4f4f4;
                font-weight: 600;
            }}

            .segment-table {{
                max-width: 650px;
                margin-bottom: 36px;
            }}

            .group-header {{
                text-align: center;
            }}

            .highlight {{
                background: #eaf3ff;
                font-weight: 600;
            }}

            .legend {{
                margin-top: 8px;
                margin-bottom: 36px;
                color: #666;
                font-size: 0.92rem;
            }}

            @media (max-width: 900px) {{
                body {{
                    margin: 24px auto;
                    padding: 0 14px;
                }}

                table {{
                    font-size: 0.9rem;
                }}

                th,
                td {{
                    padding: 7px 8px;
                }}

                @media print {{

                    body {{
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }}

                    table {{
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }}

                    th,
                    td {{
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }}

                    .highlight {{
                        background: #eaf3ff !important;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }}
                }}
            }}

        </style>
    </head>

    <body>

        <h1>VM 2026 - Studioanalys SVT</h1>

        <p class="subtitle">
            Analys av talutrymme och samtalsmönster i SVT:s
            studiosändningar under fotbolls-VM 2026
        </p>

        <div class="summary">

            <div class="metric">
                <strong>{tournament["broadcasts"]}</strong>
                <span>Sändningar</span>
            </div>

            <div class="metric">
                <strong>{tournament["segments"]}</strong>
                <span>Segment</span>
            </div>

            <div class="metric">
                <strong>{tournament["segment_hours"]}</strong>
                <span>Analyserade timmar</span>
            </div>

            <div class="metric">
                <strong>{tournament["speech_hours"]}</strong>
                <span>Taltimmar</span>
            </div>

            <div class="metric">
                <strong>{format_number(tournament["words"])}</strong>
                <span>Ord</span>
            </div>

            <div class="metric">
                <strong>{format_number(tournament["turns"])}</strong>
                <span>Prator</span>
            </div>

        </div>

        <h2>Segment</h2>

        {segment_type_table(
            tournament["segment_types"],
            tournament["segment_type_average_duration"],
        )}

        <h2>Alla talare</h2>

        {person_table(people)}

        <div class="legend">
            De två sista kolumnerna visar antal tillfällen följt av
            andelen av de segment eller sändningar där personen medverkade.
            Markerade värden är högst inom respektive kolumn.
        </div>

        <h2>Experter</h2>

        {expert_table(people)}

        <div class="legend">
            Andre och Inslag är exkluderade från jämförelsen.
            De fyra sista kolumnerna visar antal tillfällen följt av
            andelen av de segment eller sändningar där experten medverkade.
            Markerade värden är högst inom respektive kolumn.
        </div>

    </body>

    </html>
    """

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        html,
        encoding="utf-8",
    )

      
    print(f"Saved report: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_report()