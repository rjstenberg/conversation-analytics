import json
from pathlib import Path
from statistics import median

def load_result(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


from statistics import median


def merge_stats(results: list[dict]) -> dict:
    total = {}

    for result in results:
        for person, stats in result["stats"].items():
            if person not in total:
                total[person] = {
                    "speech_time": 0.0,
                    "turns": 0,
                    "words": 0,
                    "longest_turn": 0.0,
                    "turn_lengths": [],
                }

            total[person]["speech_time"] += stats.get("speech_time", 0)
            total[person]["turns"] += stats.get("turns", 0)
            total[person]["words"] += stats.get("words", 0)
            total[person]["longest_turn"] = max(
                total[person]["longest_turn"],
                stats.get("longest_turn", 0),
            )
            total[person]["turn_lengths"].extend(
                stats.get("turn_lengths", [])
            )

    total_time = sum(v["speech_time"] for v in total.values())

    for values in total.values():
        values["speech_time"] = round(values["speech_time"], 1)
        values["share"] = round(values["speech_time"] / total_time * 100, 1) if total_time else 0
        values["average_turn"] = round(values["speech_time"] / values["turns"], 1) if values["turns"] else 0
        values["median_turn"] = round(median(values["turn_lengths"]), 1) if values["turn_lengths"] else "-"
        values["longest_turn"] = round(values["longest_turn"], 1)
        values["words_per_minute"] = round(values["words"] / (values["speech_time"] / 60), 1) if values["speech_time"] else 0

    return total


def stats_table(stats: dict) -> str:
    rows = ""

    for person, values in sorted(
        stats.items(),
        key=lambda x: x[1]["speech_time"],
        reverse=True,
    ):
        rows += f"""
        <tr>
            <td>{person}</td>
            <td>{values["speech_time"]}</td>
            <td>{values["share"]}%</td>
            <td>{values["words"]}</td>
            <td>{values["turns"]}</td>
            <td>{values["average_turn"]}</td>
            <td>{values["median_turn"]}</td>
            <td>{values["longest_turn"]}</td>
            <td>{values["words_per_minute"]}</td>
        </tr>
        """

    return f"""
    <table>
        <tr>
            <th>Person</th>
            <th>Speech time (s)</th>
            <th>Share</th>
            <th>Words</th>
            <th>Turns</th>
            <th>Avg turn (s)</th>
            <th>Median turn (s)</th>
            <th>Longest turn (s)</th>
            <th>Words/min</th>
        </tr>
        {rows}
    </table>
    """


def create_broadcast_report(
    title: str,
    segment_results: list[dict],
    output_html: str,
) -> None:
    total_stats = merge_stats(segment_results)

    sections = ""

    for result in segment_results:
        segment = result.get("segment", {})
        label = segment.get("label", segment.get("name", "Segment"))
        timeline = result.get("timeline")

        if not timeline:
            segment_name = segment.get("name")
            timeline = f"reports/{segment_name}-speaker-timeline.png"

        sections += f"""
        <h2>{label}</h2>
        {stats_table(result["stats"])}
        <img src="{Path(timeline).name}" />
        """

    html = f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: system-ui, sans-serif;
                margin: 40px;
                max-width: 1200px;
            }}
            table {{
                border-collapse: collapse;
                margin-bottom: 24px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: left;
            }}
            th {{
                background: #f4f4f4;
            }}
            img {{
                max-width: 100%;
                margin-bottom: 40px;
                border: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>

        <h2>Total statistik</h2>
        {stats_table(total_stats)}

        {sections}
    </body>
    </html>
    """

    path = Path(output_html)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")