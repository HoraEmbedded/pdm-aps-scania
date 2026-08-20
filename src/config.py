"""Central configuration: paths, seeds and business constants."""

from pathlib import Path

# Racine du projet = dossier parent de src/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

TRAIN_FILE = RAW_DIR / "aps_failure_training_set.csv"
TEST_FILE = RAW_DIR / "aps_failure_test_set.csv"

SEED = 42

COST_FP = 10    # inspection inutile à l'atelier
COST_FN = 500   # panne non détectée, camion immobilisé sur route

TARGET = "class"
POSITIVE_LABEL = "pos"
NA_TOKEN = "na"

# Evaluation protocol, frozen in week 3 and never changed afterwards
VAL_SIZE = 0.20
N_SPLITS = 5

# Preprocessing thresholds, justified by the week 3 EDA
MISSING_DROP_THRESHOLD = 0.70   # columns emptier than this are dropped
CORRELATION_THRESHOLD = 0.95    # above this, keep only one of the pair


METRICS_DIR = DATA_DIR.parent / "reports" / "metrics"
