#!/usr/bin/env bash
set -e

BROADCAST_ID="$1"

if [ -z "$BROADCAST_ID" ]; then
  echo "Usage: ./scripts/run_broadcast.sh <broadcast_id>"
  echo "Example: ./scripts/run_broadcast.sh brasilien-marocko"
  exit 1
fi

BROADCAST_JSON="data/broadcasts/${BROADCAST_ID}.json"

if [ ! -f "$BROADCAST_JSON" ]; then
  echo "Broadcast JSON not found: $BROADCAST_JSON"
  exit 1
fi

echo "Extracting and analyzing broadcast..."
python main.py extract-broadcast "$BROADCAST_JSON"
python main.py analyze-broadcast "$BROADCAST_JSON"

echo ""
echo "Mapping speakers..."

SEGMENTS=$(python - <<PY
import json
from pathlib import Path

data = json.loads(Path("$BROADCAST_JSON").read_text(encoding="utf-8"))
for segment in data["segments"]:
    print(segment["name"])
PY
)

for SEGMENT in $SEGMENTS; do
  RESULT="data/results/${BROADCAST_ID}/${SEGMENT}.json"
  echo ""
  echo "Mapping $SEGMENT"
  python main.py map-speakers "$RESULT"
done

echo ""
echo "Re-running analysis with speaker maps..."
python main.py analyze-broadcast "$BROADCAST_JSON"

echo ""
echo "Creating report..."
python main.py report-broadcast "$BROADCAST_JSON"

echo ""
echo "Done."
echo "Open:"
echo "data/reports/${BROADCAST_ID}/broadcast-report.html"