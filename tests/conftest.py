"""Fixtures and skip conditions.

Every figure asserted in this suite comes from a file in reports/ or from the
printed output of scripts/build_dataset.py. Nothing here is a target value
chosen to make a test pass.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import MODELS_DIR, PROCESSED_DIR, TRAIN_FILE  # noqa: E402

CHECKSUM = 313_696.0
SPLIT_CHECKSUM = 357_794_337


def pytest_collection_modifyitems(config, items):
    """Skip what the machine cannot run rather than failing it."""
    absent = {
        "needs_raw": not TRAIN_FILE.exists(),
        "needs_prepared": not (PROCESSED_DIR / "X_fit.csv").exists(),
        "needs_model": not (MODELS_DIR / "final_model.json").exists(),
    }
    reasons = {
        "needs_raw": "data/raw absent, run scripts/download_data.sh",
        "needs_prepared": "data/processed absent, run scripts/build_dataset.py",
        "needs_model": "models/ absent, run scripts/fetch_models.sh",
    }
    for item in items:
        for marker, missing in absent.items():
            if missing and marker in item.keywords:
                item.add_marker(pytest.mark.skip(reason=reasons[marker]))


@pytest.fixture(scope="session")
def split():
    from src.data import train_validation_split
    return train_validation_split()


@pytest.fixture(scope="session")
def fitting(split):
    X_fit, _, y_fit, _ = split
    return X_fit, y_fit


@pytest.fixture(scope="session")
def groups(fitting):
    from src.missingness import detect_groups
    return detect_groups(*fitting)


@pytest.fixture(scope="session")
def encoder(fitting):
    from src.missingness import MissingnessEncoder
    return MissingnessEncoder().fit(*fitting)


@pytest.fixture(scope="session")
def prepared():
    import pandas as pd
    X = pd.read_csv(PROCESSED_DIR / "X_fit.csv", index_col=0)
    y = pd.read_csv(PROCESSED_DIR / "y_fit.csv", index_col=0).squeeze()
    return X, y
