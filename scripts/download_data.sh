#!/usr/bin/env bash
set -euo pipefail

RAW_DIR="$(cd "$(dirname "$0")/.." && pwd)/data/raw"
URL="https://archive.ics.uci.edu/static/public/421/aps+failure+at+scania+trucks.zip"
ARCHIVE="$RAW_DIR/aps_scania.zip"

mkdir -p "$RAW_DIR"

if [ -f "$RAW_DIR/aps_failure_training_set.csv" ]; then
  echo "[ok] dataset already present"
  exit 0
fi

wget -O "$ARCHIVE" "$URL"
unzip -o "$ARCHIVE" -d "$RAW_DIR" > /dev/null
find "$RAW_DIR" -mindepth 2 -name "aps_failure_*.csv" -exec mv -t "$RAW_DIR" {} + 2>/dev/null || true
rm -f "$ARCHIVE"

sha256sum "$RAW_DIR"/aps_failure_*.csv
ls -lh "$RAW_DIR"/aps_failure_*.csv
