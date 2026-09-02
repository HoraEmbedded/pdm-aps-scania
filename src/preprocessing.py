"""Differentiated imputation then scaling (decision D-10).

Written by hand rather than with ColumnTransformer, which returns a bare array
and emits its columns in transformer order: the notebook version had to rebuild
the column list and the index by hand on every call to compensate.
"""

import joblib
from sklearn.preprocessing import StandardScaler

from src.config import PROCESSED_DIR


class Preprocessor:
    """Impute, then scale. Everything is learned on the fitting split only.

    Group 1 is imputed with zero rather than the median: its columns are absent
    for the least used trucks, so the median of the 18% that do carry a value
    is the median of a heavily used population. The depth variable and the
    sub-block flags are left unscaled (docs/technical_decisions.md).
    """

    def __init__(self, group1, unscaled):
        self.group1 = list(group1)
        self.unscaled = list(unscaled)

    def fit(self, X):
        self.columns_ = list(X.columns)
        self.others_ = [c for c in X.columns if c not in self.group1]
        self.medians_ = X[self.others_].median()
        self.to_scale_ = [c for c in X.columns if c not in self.unscaled]
        self.scaler_ = StandardScaler().fit(self._impute(X)[self.to_scale_])
        return self

    def _impute(self, X):
        X = X.copy()
        X[self.group1] = X[self.group1].fillna(0.0)
        X[self.others_] = X[self.others_].fillna(self.medians_)
        return X

    def transform(self, X):
        X = self._impute(X)[self.columns_]
        X[self.to_scale_] = self.scaler_.transform(X[self.to_scale_])
        return X

    def fit_transform(self, X):
        return self.fit(X).transform(X)


def save(obj, name: str) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, PROCESSED_DIR / name)


def load(name: str):
    return joblib.load(PROCESSED_DIR / name)
