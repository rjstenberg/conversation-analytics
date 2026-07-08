import json
import re
from collections import Counter
from pathlib import Path


def overlap_seconds(a_start, a_end, b_start, b_end) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def is_bad_text(text: str) -> bool:
    words = text.strip().split()

    if not words:
        return True

    if len(words) >= 8:
        most_common = max(set(words), key=words.count)
        if words.count(most_common) / len(words) > 0.6:
            return True

    return False


def has_repeated_phrase(
    words: list[str],
    phrase_len: int,
    min_repeats: int,
) -> bool:
    limit = len(words) - phrase_len * min_repeats + 1

    for i in range(limit):
        phrase = words[i:i + phrase_len]

        repeated = True
        for r in range(1, min_repeats):
            start = i + r * phrase_len
            if words[start:start + phrase_len] != phrase:
                repeated = False
                break

        if repeated:
            return True

    return False


def is_repetitive_hallucination(text: str) -> bool:
    if text.count("�") >= 5:
        return True

    if re.search(r"(.)\1{20,}", text.lower()):
        return True

    words = re.findall(r"\b[\wÅÄÖåäö']+\b", text.lower())

    if len(words) < 12:
        return False

    if len(words) >= 20:
        counts = Counter(words)
        _, count = counts.most_common(1)[0]

        if count >= 20:
            return True

        if count / len(words) > 0.8:
            return True

    unique_ratio = len(set(words)) / len(words)

    if unique_ratio < 0.35:
        return True

    for i in range(len(words) - 5):
        window = words[i:i + 6]
        if len(set(window)) <= 2:
            return True

    return False


def merge_transcript_and_speakers(
    transcript_json: str,
    diarization_segments: list[dict],
) -> list[dict]:
    transcript = json.loads(Path(transcript_json).read_text(encoding="utf-8"))
    merged = []

    for segment in transcript.get("segments", []):
        start = float(segment["start"])
        end = float(segment["end"])
        text = segment.get("text", "").strip()

        if is_bad_text(text):
            continue

        if is_repetitive_hallucination(text):
            continue

        best_speaker = "UNKNOWN"
        best_overlap = 0.0

        for diar in diarization_segments:
            overlap = overlap_seconds(start, end, diar["start"], diar["end"])

            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = diar["speaker"]

        merged.append({
            "speaker": best_speaker,
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(end - start, 2),
            "text": text,
        })

    return merged