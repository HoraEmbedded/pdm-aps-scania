"""Train / validation split and cross-validation strategy.

Single source of truth for the evaluation protocol. Every model in the
benchmark must go through these functions, otherwise the comparison is void.
"""

from sklearn.model_selection import StratifiedKFold, train_test_split

from src.config import N_SPLITS, SEED, VAL_SIZE
from src.data.load_aps import load_aps, split_xy


def get_train_val(val_size: float = VAL_SIZE, seed: int = SEED):
    """Split the training file into a fitting set and a validation set.

    Stratified: both sides keep the original 1.67% failure rate. Without
    stratification the rare class would drift between splits and make
    recall estimates unstable.
    """
    frame = load_aps("train")
    features, target = split_xy(frame)

    return train_test_split(
        features,
        target,
        test_size=val_size,
        stratify=target,
        random_state=seed,
    )


def get_cv(n_splits: int = N_SPLITS, seed: int = SEED) -> StratifiedKFold:
    """Cross-validation strategy shared by every model of the benchmark."""
    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)


def get_sealed_test():
    """Load the held-out test set. Do not call before week 8."""
    frame = load_aps("test")
    return split_xy(frame)
