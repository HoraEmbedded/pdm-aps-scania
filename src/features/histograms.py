"""Feature engineering on the 7 histogram groups of the APS dataset.

Each group holds 10 ordered bins of one distribution. Raw bins mix shape and
scale; the derived features separate them, which is what actually carries the
degradation signal.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from src.data.schema import histogram_groups


class HistogramFeatures(BaseEstimator, TransformerMixin):
    """Add shape descriptors for every histogram group.

    keep_raw_bins : keep the original bin columns alongside the new features.
                    True by default so tree models can still use them.
    """

    def __init__(self, keep_raw_bins: bool = True, min_bins: int = 10):
        self.keep_raw_bins = keep_raw_bins
        self.min_bins = min_bins

    def fit(self, X, y=None):
        # Group detection depends only on column names, never on values,
        # so there is no statistic learned here and no leakage risk.
        self.groups_ = histogram_groups(X.columns, min_bins=self.min_bins)
        self.feature_names_in_ = list(X.columns)
        return self

    def transform(self, X):
        X = X.copy()
        derived = {}

        for prefix, bins in self.groups_.items():
            block = X[bins].to_numpy(dtype=float)
            ranks = np.arange(block.shape[1])

            total = np.nansum(block, axis=1)
            # Guard against division by zero on trucks with an empty histogram
            safe_total = np.where(total > 0, total, np.nan)
            shares = block / safe_total[:, None]

            mean_rank = np.nansum(shares * ranks, axis=1)
            variance = np.nansum(shares * (ranks - mean_rank[:, None]) ** 2, axis=1)

            with np.errstate(divide="ignore", invalid="ignore"):
                entropy = -np.nansum(shares * np.log(shares + 1e-12), axis=1)
            
            
            derived[f"{prefix}_total"] = total
            derived[f"{prefix}_mean_rank"] = mean_rank
            derived[f"{prefix}_std_rank"] = np.sqrt(variance)
            derived[f"{prefix}_max_share"] = np.nanmax(shares, axis=1)
            derived[f"{prefix}_entropy"] = entropy
            derived[f"{prefix}_tail_ratio"] = shares[:, 0] + shares[:, -1]

        new_features = pd.DataFrame(derived, index=X.index)

        if self.keep_raw_bins:
            return pd.concat([X, new_features], axis=1)

        raw_bins = [col for cols in self.groups_.values() for col in cols]
        return pd.concat([X.drop(columns=raw_bins), new_features], axis=1)
