import argparse
import json
from pathlib import Path

from transcription.whisper import transcribe_audio
from diarization.pyannote import diarize_audio
from analysis.merge_segments import merge_transcript_and_speakers
from analysis.speaker_statistics import speaker_statistics
from visualization.timeline import create_speaker_timeline
from analysis.speaker_mapping import load_people, load_mapping
from analysis.save_results import save_analysis_results
from analysis.broadcast import load_broadcast, get_segments
from media.extract_segment import extract_audio_segment
from analysis.speaker_mapper import create_speaker_map_from_results
from reporting.broadcast_report import create_broadcast_report

def print_speaker_stats(stats: dict) -> None:
    for speaker, values in sorted(
        stats.items(),
        key=lambda x: x[1]["speech_time"],
        reverse=True,
    ):
        print(f"\n{speaker}")
        for key, value in values.items():
            print(f"  {key}: {value}")


def analyze(audio_file: str, broadcast_id: str | None = None) -> dict:
    audio = Path(audio_file)
    stem = audio.stem

    if broadcast_id:
        transcript_dir = Path("data/transcripts") / broadcast_id
        diarization_dir = Path("data/diarization") / broadcast_id
        results_dir = Path("data/results") / broadcast_id
        speaker_map_dir = Path("data/speaker_maps") / broadcast_id
        report_dir = Path("data/reports") / broadcast_id
    else:
        transcript_dir = Path("data/transcripts")
        diarization_dir = Path("data/diarization")
        results_dir = Path("data/results")
        speaker_map_dir = Path("data/speaker_maps")
        report_dir = Path("data/reports")


    transcript_path = transcript_dir / f"{stem}.json"
    timeline_path = report_dir / f"{stem}-speaker-timeline.png" 

    if not transcript_path.exists():
        print("Transcribing...")
        transcribe_audio(str(audio), str(transcript_path))
    else:
        print(f"Using existing transcript: {transcript_path}")

    print("Running diarization...")
    diarization = diarize_audio(str(audio), cache_dir=str(diarization_dir))

    print("Merging transcript and speakers...")
    merged = merge_transcript_and_speakers(str(transcript_path), diarization)
    people = load_people()

    mapping_path = speaker_map_dir / f"{stem}.json"

    if mapping_path.exists():
        speaker_map = load_mapping(mapping_path)
    else:
        speaker_map = {}

    print("\nSpeaker statistics:")
    stats = speaker_statistics(merged, speaker_map=speaker_map)
    results_path = results_dir / f"{stem}.json"
    print_speaker_stats(stats)

    print("\nPeople:")
    print(people)

    print("\nSpeaker map:")
    print(speaker_map)
    print("\nCreating speaker timeline...")

    create_speaker_timeline(
        merged,
        str(timeline_path),
        speaker_map=speaker_map,
        people=people,
    )

    save_analysis_results(
        str(results_path),
        stats,
        merged,
        speaker_map,
        timeline=str(timeline_path),
    )

    print(f"Saved analysis: {results_path}")

    print(f"\nSaved timeline: {timeline_path}")

    return {
        "audio": str(audio),
        "transcript": str(transcript_path),
        "timeline": str(timeline_path),
        "results": str(results_path),
        "stats": stats,
    }

def extract_broadcast(broadcast_json: str) -> None:
    broadcast = load_broadcast(broadcast_json)
    broadcast_id = broadcast["broadcast_id"]
    source_audio = broadcast["source_audio"]

    output_dir = Path(f"data/temp/{broadcast_id}")

    for segment in get_segments(broadcast):
        name = segment["name"]
        start = segment["start"]
        end = segment["end"]

        output_audio = output_dir / f"{name}.wav"

        print(f"Extracting {name}: {start}–{end}")
        extract_audio_segment(
            source_audio,
            str(output_audio),
            start,
            end,
        )

        print(f"Saved {output_audio}")

def analyze_broadcast(broadcast_json: str) -> None:
    broadcast = load_broadcast(broadcast_json)
    broadcast_id = broadcast["broadcast_id"]
    source_audio = broadcast["source_audio"]

    output_dir = Path(f"data/temp/{broadcast_id}")
    broadcast_results = []

    for segment in get_segments(broadcast):
        name = segment["name"]
        start = segment["start"]
        end = segment["end"]

        output_audio = output_dir / f"{name}.wav"

        print(f"\n=== {segment.get('label', name)} ===")
        print(f"Extracting {start}–{end}")

        extract_audio_segment(
            source_audio,
            str(output_audio),
            start,
            end,
        )

        result = analyze(str(output_audio), broadcast_id=broadcast_id)
        result["segment"] = segment

        broadcast_results.append(result)

    print("\nBroadcast analysis complete.")
    print(f"Segments analyzed: {len(broadcast_results)}")

def report_broadcast(broadcast_json: str) -> None:
    broadcast = load_broadcast(broadcast_json)
    broadcast_id = broadcast["broadcast_id"]
    title = broadcast.get("title", broadcast_id)

    segment_results = []

    for segment in get_segments(broadcast):
        name = segment["name"]
        result_path = Path(f"data/results/{broadcast_id}/{name}.json")

        if not result_path.exists():
            print(f"Missing result: {result_path}")
            continue

        result = json.loads(result_path.read_text(encoding="utf-8"))
        result["segment"] = segment
        segment_results.append(result)

    output_html = f"data/reports/{broadcast_id}/broadcast-report.html"

    create_broadcast_report(
        title,
        segment_results,
        output_html,
    )

    print(f"Saved broadcast report: {output_html}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Conversation analytics")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze_parser = sub.add_parser("analyze")
    analyze_parser.add_argument("audio_file")

    extract_parser = sub.add_parser("extract-broadcast")
    extract_parser.add_argument("broadcast_json")

    broadcast_parser = sub.add_parser("analyze-broadcast")
    broadcast_parser.add_argument("broadcast_json")

    map_parser = sub.add_parser("map-speakers")
    map_parser.add_argument("results_json")

    report_broadcast_parser = sub.add_parser("report-broadcast")
    report_broadcast_parser.add_argument("broadcast_json")

    args = parser.parse_args()

    if args.command == "analyze":
        analyze(args.audio_file)

    elif args.command == "extract-broadcast":
        extract_broadcast(args.broadcast_json)

    elif args.command == "analyze-broadcast":
        analyze_broadcast(args.broadcast_json)

    elif args.command == "map-speakers":
        results = Path(args.results_json)
        if "data/results" in str(results):
            relative = results.relative_to("data/results")
            output = Path("data/speaker_maps") / relative
        else:
            output = Path(f"data/speaker_maps/{results.stem}.json")
        create_speaker_map_from_results(str(results), str(output))

    elif args.command == "report-broadcast":
        report_broadcast(args.broadcast_json)    


if __name__ == "__main__":
    main()