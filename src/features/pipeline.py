"""Reproducible preprocessing pipeline (EF02)."""

import warnings
import numpy as np
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src.config import SEED
from src.features.histograms import HistogramFeatures


def build_imputer(strategy: str = "median", add_indicator: bool = True):
    """Return the imputation step, or None when the model handles NaN itself."""
    if strategy is None:
        return None
    if strategy == "median":
        return SimpleImputer(strategy="median", add_indicator=add_indicator)
    if strategy == "zero":
        return SimpleImputer(strategy="constant", fill_value=0, add_indicator=add_indicator)
    if strategy == "mice":
        return IterativeImputer(max_iter=10, random_state=SEED, add_indicator=add_indicator)
    raise ValueError(f"Unknown imputation strategy: {strategy}")


def build_pipeline(
    estimator,
    imputation: str = "median",
    log_transform: bool = False,
    scale: bool = True,
    resampling: str = None,
) -> Pipeline:
    steps = [("histograms", HistogramFeatures(keep_raw_bins=True))]

    if log_transform:
        steps.append((
            "log",
            FunctionTransformer(
                lambda X: np.log1p(np.clip(X, 0, None)),
                feature_names_out="one-to-one"
            ),
        ))

    imputer = build_imputer(imputation)
    if imputer is not None:
        steps.append(("imputer", imputer))

    if scale:
        steps.append(("scaler", StandardScaler()))

    if resampling == "smote":
        steps.append(("smote", SMOTE(random_state=SEED, k_neighbors=5)))

    steps.append(("model", estimator))
    return Pipeline(steps)
