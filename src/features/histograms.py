"""Transformer extracting domain features from Scania histogram bins."""

import re
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

HIST_PATTERN = re.compile(r"^([a-z]+)_(\d{3})$")


class HistogramFeatures(BaseEstimator, TransformerMixin):
    """Derive total counts, shares, and concentration metrics from bin groups."""

    def __init__(self, keep_raw_bins: bool = True):
        self.keep_raw_bins = keep_raw_bins

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        groups = {}
        for col in X_df.columns:
            match = HIST_PATTERN.match(str(col))
            if match:
                prefix = match.group(1)
                groups.setdefault(prefix, []).append(col)
        self.hist_groups_ = {p: cols for p, cols in groups.items() if len(cols) > 1}
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X)
        derived = {}

        # Suppress harmless NaN slice warnings during vectorized operations
        with np.errstate(invalid="ignore", divide="ignore"):
            for prefix, cols in self.hist_groups_.items():
                bins = X_df[cols].to_numpy(dtype=float)
                total = np.nansum(bins, axis=1)
                derived[f"{prefix}_sum"] = total

                shares = bins / np.where(total[:, None] == 0, np.nan, total[:, None])
                derived[f"{prefix}_max_share"] = np.nanmax(shares, axis=1)

                non_zero = np.sum(bins > 0, axis=1)
                derived[f"{prefix}_active_bins"] = non_zero

        derived_df = pd.DataFrame(derived, index=X_df.index)

        if not self.keep_raw_bins:
            all_hist_cols = [c for cols in self.hist_groups_.values() for c in cols]
            X_df = X_df.drop(columns=all_hist_cols)

        return pd.concat([X_df, derived_df], axis=1)
