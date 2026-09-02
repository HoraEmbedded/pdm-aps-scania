"""Loading and splitting. The official test file stays sealed until step 6.4."""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import (MISSING_TOKEN, POSITIVE_LABEL, SEED, TARGET, TEST_FILE,
                        TRAIN_FILE, VALIDATION_SHARE)


def _header_line(path: Path) -> int:
    # The UCI archive carries a 20 line GPL preamble that the Kaggle mirror
    # does not, so the header is located instead of skipped by a fixed count.
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for index, line in enumerate(handle):
            if line.lower().startswith(f"{TARGET},"):
                return index
    raise ValueError(f"No header line found in {path}")


def load(split: str = "train") -> pd.DataFrame:
    """Load one raw file, with numeric features and a 0/1 target.

    Label encoding, never to be inverted: 1 = APS failure = rare class.
    """
    path = {"train": TRAIN_FILE, "test": TEST_FILE}[split]
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing. Run scripts/download_data.sh")

    frame = pd.read_csv(path, skiprows=_header_line(path),
                        na_values=MISSING_TOKEN, low_memory=False)

    frame[TARGET] = (frame[TARGET] == POSITIVE_LABEL).astype(int)
    measures = [c for c in frame.columns if c != TARGET]
    frame[measures] = frame[measures].apply(pd.to_numeric, errors="coerce")
    return frame


def train_validation_split(seed: int = SEED):
    """Stratified 80/20 split of the training file, before any preparation.

    Stratification is not cosmetic: over 500 unstratified draws the validation
    positive rate ranges from 1.36% to 1.98% (notebook 01), which straddles
    the 1.96% break-even rate and therefore flips which constant rule is the
    cheaper reference on that part.
    """
    frame = load("train")
    X, y = frame.drop(columns=[TARGET]), frame[TARGET]
    return train_test_split(X, y, test_size=VALIDATION_SHARE, stratify=y,
                            random_state=seed)


def load_sealed_test():
    """Load the sealed test set. Not to be called before step 6.4."""
    frame = load("test")
    return frame.drop(columns=[TARGET]), frame[TARGET]
