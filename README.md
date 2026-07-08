# Conversation Analytics for Sports Broadcasts

A Python tool for analyzing conversational dynamics in live sports studio broadcasts
using automatic speech recognition, speaker diarization and statistical analysis.

Created by Rebecca Stenberg.

Originally developed as a personal data analysis project to explore speaking patterns
in Swedish football broadcasts. The project combines Whisper transcription, Pyannote
speaker diarization and a custom analysis pipeline to produce interactive reports of
studio conversations.

## Features

- Automatic extraction of predefined broadcast segments
- Automatic speech transcription using Whisper
- Speaker diarization using Pyannote
- Interactive speaker identification
- Speaking time statistics
- Turn-based conversation metrics
- Speaker timeline visualizations
- HTML report generation
- Support for analyzing multiple broadcasts

## Example report

Example analysis of **FIFA Fotbolls-VM 2026 – Brasilien vs Marocko**
(originally broadcast by SVT).

*(Insert screenshot of the report overview here.)*

## Example workflow

```
Broadcast
    ↓
Segment extraction
    ↓
Speech transcription
    ↓
Speaker diarization
    ↓
Interactive speaker mapping
    ↓
Conversation analysis
    ↓
HTML report
```

## Metrics

The generated report currently includes:

- Total speaking time
- Share of total speaking time
- Number of words
- Number of speaking turns
- Average speaking turn
- Median speaking turn
- Longest speaking turn
- Words per minute
- Speaker timeline visualization

Metrics are presented both for the full broadcast and for each analyzed segment.

## Installation

Clone the repository:

```bash
git clone https://github.com/<username>/conversation-analytics.git
cd conversation-analytics
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install FFmpeg.
Mac example:

```bash
brew install ffmpeg
```

Configure Hugging Face access for Pyannote by creating a user access token and accepting the Pyannote model license.

## Usage

### 1. Create a new broadcast

```bash
./scripts/new_broadcast.sh
```

The script will:

- download the audio (optional)
- create a new broadcast configuration
- prompt you to enter broadcast metadata

Afterwards, edit the generated JSON file and specify the start and end times for each segment.

### 2. Analyze the broadcast

```bash
./scripts/run_broadcast.sh <broadcast_id>
```

The pipeline automatically performs:

- segment extraction
- transcription
- speaker diarization
- interactive speaker mapping
- statistical analysis
- report generation

### 3. View the report

Open:

```
data/reports/<broadcast_id>/broadcast-report.html
```

## Future work

Planned improvements include:

- Cross-broadcast statistics
- Longitudinal analysis across multiple broadcasts
- Automatic speaker suggestions during speaker mapping
- Additional conversational metrics

## Notes

This repository contains the analysis software and example analysis output only.

Broadcast media, extracted audio segments and speech transcripts are intentionally
not included.

Users are responsible for ensuring they have the right to access and analyze any
media used with the software.

Whisper occasionally produces hallucinated repetitions in noisy multilingual clips. The pipeline removes the most obvious cases but does not attempt to correct all transcription artifacts. Whisper language detection is used by default, since broadcasts may include Swedish studio talk, foreign-language interviews and mixed-language inserts.

## Acknowledgements

Built using:

- Whisper
- Pyannote
- FFmpeg

ChatGPT was used during development for programming support, debugging,
architectural discussions and code review.