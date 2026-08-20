"""Loader for the APS Failure at Scania Trucks dataset."""

from pathlib import Path

import pandas as pd

from src.config import NA_TOKEN, POSITIVE_LABEL, TARGET, TEST_FILE, TRAIN_FILE


def _detect_header_row(path: Path) -> int:
    """Return the 0-based index of the line holding the column names."""
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for index, line in enumerate(handle):
            if line.lower().startswith(f"{TARGET},"):
                return index
    raise ValueError(f"No header line starting with '{TARGET},' found in {path}")


def load_aps(split: str = "train", encode_target: bool = True) -> pd.DataFrame:
    """Load one split as a DataFrame with numeric features and 0/1 target."""
    path = {"train": TRAIN_FILE, "test": TEST_FILE}[split]
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing. Run: bash scripts/download_data.sh")

    frame = pd.read_csv(
        path,
        skiprows=_detect_header_row(path),
        na_values=NA_TOKEN,
        low_memory=False,
    )

    if encode_target:
        frame[TARGET] = (frame[TARGET] == POSITIVE_LABEL).astype(int)

    feature_cols = [col for col in frame.columns if col != TARGET]
    frame[feature_cols] = frame[feature_cols].apply(pd.to_numeric, errors="coerce")

    return frame


def split_xy(frame: pd.DataFrame):
    """Split a loaded DataFrame into features X and target y."""
    return frame.drop(columns=[TARGET]), frame[TARGET]
