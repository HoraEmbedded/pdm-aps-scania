#!/usr/bin/env bash
# Fetch the trained model weights from the project's GitHub release.
#
# Weights are not versioned in Git: they are binary, they are large, and they
# are regenerable from the scripts, which are versioned instead.

set -euo pipefail

REPO="${MODEL_REPO:-<your-account>/pdm-aps-scania}"
TAG="${MODEL_TAG:-weights-v1}"
MODELS_DIR="$(cd "$(dirname "$0")/.." && pwd)/models"

mkdir -p "$MODELS_DIR"

if [ -f "$MODELS_DIR/final_model.json" ]; then
  echo "[ok] models already present in $MODELS_DIR"
  exit 0
fi

echo "[..] downloading weights from release $TAG"
URL="https://github.com/$REPO/releases/download/$TAG/models.tar.gz"

if ! curl -fL -o /tmp/models.tar.gz "$URL"; then
  echo "[error] download failed."
  echo "Fallback: rebuild the artefacts locally with"
  echo "  python scripts/build_dataset.py"
  echo "  jupyter nbconvert --execute --inplace notebooks/05_arbitration.ipynb"
  exit 1
fi

tar -xzf /tmp/models.tar.gz -C "$MODELS_DIR" --strip-components=1
rm /tmp/models.tar.gz

echo "[ok] models available:"
ls -lh "$MODELS_DIR"
