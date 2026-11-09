#!/usr/bin/env bash
# Prepare this checkout on a 64-bit Raspberry Pi. See docs/reproduction.md.
set -euo pipefail

cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python3.12}"

if [ "$(uname -m)" != "aarch64" ]; then
    echo "This setup requires a 64-bit Raspberry Pi OS or Debian." >&2
    exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null; then
    echo "Install Python 3.12 with venv support, or set PYTHON_BIN to its path." >&2
    exit 1
fi

"$PYTHON_BIN" -m venv .venv
.venv/bin/python -m pip install -r requirements-serve.txt
bash scripts/download_data.sh
.venv/bin/python scripts/prepare_demo.py
.venv/bin/python scripts/check_port.py
