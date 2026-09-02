"""Single source of truth: paths, seed, cost matrix, protocol constants."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "reports" / "figures"
MODELS_DIR = ROOT / "models"

TRAIN_FILE = RAW_DIR / "aps_failure_training_set.csv"
TEST_FILE = RAW_DIR / "aps_failure_test_set.csv"

SEED = 42

COST_FP = 10
COST_FN = 500

# The class weighting comes from the cost ratio, not from the observed class
# frequencies, which would give 59:1 (decision D-11).
COST_RATIO = COST_FN / COST_FP
CLASS_WEIGHT = {0: 1, 1: COST_RATIO}

# Diagnostic reference on a calibrated probability, never an operating point.
BAYES_THRESHOLD = COST_FP / (COST_FP + COST_FN)

VALIDATION_SHARE = 0.20
N_FOLDS = 5
N_INNER_FOLDS = 3

TARGET = "class"
POSITIVE_LABEL = "pos"
MISSING_TOKEN = "na"

# Written before the computation it selects on (decision D-09).
GAP_THRESHOLD = 0.10
