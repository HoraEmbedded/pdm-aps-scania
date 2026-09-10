#!/usr/bin/env bash
# Prepare a Raspberry Pi 4 to serve the frozen model.
#
# Written on the development machine and run once on the board: a slow ARM
# device is the worst place to improvise, and every apt install here takes
# minutes rather than seconds.
#
# Requires Raspberry Pi OS 64-bit. The 32-bit build ships an ARMv7 Python for
# which numpy and xgboost wheels are scarce, and building them on the board is
# a multi-hour proposition.

set -euo pipefail

DEPOT="${DEPOT:-$HOME/pdm-aps-scania}"
DEPOT_URL="${DEPOT_URL:-https://github.com/HoraEmbedded/pdm-aps-scania.git}"

echo "=================== 1. Contrôle de l'architecture"
uname -m
if [ "$(uname -m)" != "aarch64" ]; then
    echo "ERREUR : système 32 bits détecté."
    echo "Réinstalle Raspberry Pi OS 64-bit avant de continuer."
    exit 1
fi

cat /etc/os-release | grep PRETTY_NAME
python3 --version
echo "mémoire disponible :"
free -h | head -2

echo
echo "=================== 2. Fichier d'échange"
# XGBoost links with several gigabytes of intermediate objects if it has to be
# built from source. The default 100 MB swap on Raspberry Pi OS is not enough,
# and the failure mode is an out-of-memory kill halfway through, after forty
# minutes of compilation.
ACTUEL=$(grep CONF_SWAPSIZE /etc/dphys-swapfile | cut -d= -f2)
echo "taille actuelle : ${ACTUEL} Mo"
if [ "${ACTUEL}" -lt 2048 ]; then
    echo "passage à 2048 Mo"
    sudo dphys-swapfile swapoff
    sudo sed -i 's/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    free -h | head -3
fi

echo
echo "=================== 3. Paquets système"
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    python3-venv python3-dev python3-pip \
    build-essential cmake git curl \
    libatlas-base-dev libgomp1
# libgomp1 is what XGBoost links against for OpenMP. Without it the first
# import fails with "libgomp.so.1: cannot open shared object file", which is
# the single most common deployment failure on this kind of project.

echo
echo "=================== 4. Dépôt"
if [ -d "$DEPOT" ]; then
    echo "déjà présent, mise à jour"
    cd "$DEPOT" && git pull
else
    git clone "$DEPOT_URL" "$DEPOT"
    cd "$DEPOT"
fi

echo
echo "=================== 5. Environnement Python"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip wheel

# Piwheels serves ARM wheels for Raspberry Pi OS. Listed as an extra index so
# that PyPI still wins when it has a wheel, and Piwheels only fills the gaps.
./.venv/bin/pip install \
    --extra-index-url https://www.piwheels.org/simple \
    -r requirements-serve.txt

echo
echo "=================== 6. Versions installées"
./.venv/bin/python - << 'EOF'
import numpy, pandas, sklearn, xgboost
print("numpy       ", numpy.__version__)
print("pandas      ", pandas.__version__)
print("scikit-learn", sklearn.__version__)
print("xgboost     ", xgboost.__version__)
EOF

echo
echo "=================== 7. Poids du modèle"
bash scripts/fetch_models.sh
ls -lh models/

echo
echo "=================== 8. Chargement du modèle"
./.venv/bin/python - << 'EOF'
from src.inference import Predictor

predictor = Predictor.load()
print("modèle    :", predictor.name)
print("seuil     :", predictor.threshold)
print("colonnes  :", len(predictor.raw_columns))
EOF

echo
echo "=================== Installation terminée"
echo "Étape suivante : ./.venv/bin/python scripts/measure_pi.py"
