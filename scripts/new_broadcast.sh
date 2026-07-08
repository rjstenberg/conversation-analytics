#!/usr/bin/env bash
set -e

read -p "Broadcast id, e.g. england-france: " BROADCAST_ID
read -p "Title, e.g. England - France: " TITLE
read -p "SVT Play URL: " URL

if [ -z "$BROADCAST_ID" ] || [ -z "$TITLE" ] || [ -z "$URL" ]; then
  echo "Missing input."
  exit 1
fi

mkdir -p data/audio data/broadcasts

echo ""
echo "Downloading audio..."
yt-dlp \
  -f ba \
  -P data/audio \
  -o "${BROADCAST_ID}.%(ext)s" \
  "$URL"

AUDIO_FILE=$(ls data/audio/${BROADCAST_ID}.* | head -n 1)

BROADCAST_JSON="data/broadcasts/${BROADCAST_ID}.json"

cat > "$BROADCAST_JSON" <<JSON
{
  "broadcast_id": "$BROADCAST_ID",
  "title": "$TITLE",
  "source_audio": "$AUDIO_FILE",
  "segments": [
    {
      "name": "pre_match",
      "label": "Uppsnack",
      "start": "",
      "end": ""
    },
    {
      "name": "halftime",
      "label": "Halvtid",
      "start": "",
      "end": ""
    },
    {
      "name": "post_match",
      "label": "Efter match",
      "start": "",
      "end": ""
    }
  ]
}
JSON

echo ""
echo "Done."
echo "Edit this file and add start/end times:"
echo "$BROADCAST_JSON"