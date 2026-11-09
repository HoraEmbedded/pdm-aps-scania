#!/usr/bin/env bash
# Fetch the trained model weights from the project's GitHub release.
#
# Weights are not versioned in Git: they are binary, they are large, and they
# are regenerable from the scripts, which are versioned instead.

set -euo pipefail

REPO="${MODEL_REPO:-HoraEmbedded/pdm-aps-scania}"
TAG="${MODEL_TAG:-weights-v1}"
MODELS_DIR="$(cd "$(dirname "$0")/.." && pwd)/models"

mkdir -p "$MODELS_DIR"

if [ -f "$MODELS_DIR/final_model.json" ] &&
   [ -f "$MODELS_DIR/gradient_boosting.joblib" ]; then
  echo "[ok] models already present in $MODELS_DIR"
  exit 0
fi

echo "[..] downloading weights from release $TAG"
URL="https://github.com/$REPO/releases/download/$TAG/models.tar.gz"

if ! curl -fL -o /tmp/models.tar.gz "$URL"; then
  echo "[error] download failed."
  echo "See docs/reproduction.md to rebuild the selected model and preprocessing locally."
  exit 1
fi

tar -xzf /tmp/models.tar.gz -C "$MODELS_DIR" --strip-components=1
rm /tmp/models.tar.gz

echo "[ok] model weights available. See docs/reproduction.md for preprocessing."
ls -lh "$MODELS_DIR"
