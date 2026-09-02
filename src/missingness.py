"""Encode the information carried by missing values (decision D-09).

Two groups emerge from the per-class absence rates:
    group 1: 8 columns, absence nested, summed into one ordinal depth variable
    group 2: 56 columns, grouped into sub-blocks by absence rate, one flag each
Group 2 is deliberately not summed: it fails the nesting test that group 1
passes (notebook 01). Detection runs on the fitting split only.
"""

import pandas as pd

from src.config import GAP_THRESHOLD


def per_class_missing_rate(X, y) -> pd.DataFrame:
    missing = X.isna().astype(int)
    return pd.DataFrame({
        "rate_aps": missing[y == 1].mean(),
        "rate_other": missing[y == 0].mean(),
    })


def gap_cliff(X, y) -> dict:
    """Measure the drop between the last selected column and the next one.

    Reported because it is what makes the group 1 threshold defensible: the
    eight columns of group 1 sit above 0.32 and the ninth largest gap is below
    0.03, a factor of more than ten. The group 2 side has no comparable break,
    so its threshold is a declared choice and nothing more.
    """
    gap = (per_class_missing_rate(X, y)
           .pipe(lambda f: f["rate_other"] - f["rate_aps"]))

    positive = gap[gap > 0].sort_values(ascending=False)
    negative = gap[gap < 0].sort_values()

    def drop(series, n):
        if len(series) <= n:
            return None
        inner, outer = abs(series.iloc[n - 1]), abs(series.iloc[n])
        return {"last_selected": float(inner), "next": float(outer),
                "factor": float(inner / outer) if outer else float("inf")}

    return {"gap": gap.sort_values(ascending=False),
            "group1_cliff": drop(positive, 8),
            "group2_cliff": drop(negative, 56)}


def detect_groups(X, y, threshold: float = GAP_THRESHOLD) -> dict:
    """Split columns into group 1, group 2 and mute columns.

    Group 1 is absent far more often among non-APS failures, group 2 far more
    often among APS failures. On the group 1 side the threshold falls inside a
    real break in the sorted gaps; on the group 2 side it does not, so the
    value was written down before the computation it selects on
    (docs/technical_decisions.md). Use gap_cliff to measure both.
    """
    rates = per_class_missing_rate(X, y)
    gap = rates["rate_other"] - rates["rate_aps"]

    group1 = gap[gap > threshold].index.tolist()
    group2 = gap[gap < -threshold].index.tolist()
    mute = gap[gap.abs() <= threshold].index.tolist()

    # Ordered by increasing absence rate, which the nesting report requires.
    missing = X.isna()
    group1 = missing[group1].mean().sort_values().index.tolist()
    group2 = missing[group2].mean().sort_values().index.tolist()

    return {"group1": group1, "group2": group2, "mute": mute,
            "gap": gap.sort_values(ascending=False)}


def duplicate_absence_columns(X, columns=None) -> list:
    """Column pairs whose absence indicators are perfectly correlated.

    These carry the same missingness information twice, which matters when
    reading feature importances rather than when fitting.
    """
    missing = X[columns].isna() if columns is not None else X.isna()
    missing = missing.loc[:, missing.std() > 0]
    correlation = missing.astype(int).corr()

    pairs = []
    names = correlation.columns
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            if correlation.loc[left, right] == 1.0:
                pairs.append((left, right))
    return pairs


def nesting_report(X, columns) -> dict:
    """Is absence nested along these columns, taken in the given order?

    Nesting means that once a column is absent, every column after it is too,
    which forbids the pattern "10" in a row's 0/1 string. Counting distinct
    patterns is not a proof: any 9 patterns out of 256 give the same count.
    """
    patterns = X[columns].isna().astype(int).astype(str).agg("".join, axis=1)
    nested = patterns.map(lambda pattern: "10" not in pattern)
    return {
        "n_patterns": int(patterns.nunique()),
        "n_possible": 2 ** len(columns),
        "n_if_nested": len(columns) + 1,
        "nested_share": float(nested.mean()),
        "n_exceptions": int((~nested).sum()),
        "counts": patterns.value_counts(),
        "exceptions": patterns[~nested].value_counts(),
    }


def sub_blocks(X, columns, decimals: int = 3) -> dict:
    """Group columns by rounded absence rate. These are the sub-blocks."""
    rates = X[columns].isna().mean().round(decimals)
    return {rate: sorted(rates[rates == rate].index.tolist())
            for rate in sorted(rates.unique())}


def sub_block_homogeneity(X, blocks: dict) -> pd.DataFrame:
    """How close each sub-block is to moving as a single column.

    A perfectly homogeneous block shows 2 patterns, all-present and
    all-absent. This is what licenses reading one member per block instead of
    all of them.
    """
    rows = []
    for rate, members in sorted(blocks.items()):
        if len(members) < 2:
            rows.append({"rate": rate, "n_columns": 1, "n_patterns": 1,
                         "agreement": 1.0})
            continue
        missing = X[members].isna()
        share = missing.mean(axis=1)
        rows.append({
            "rate": rate,
            "n_columns": len(members),
            "n_patterns": int(missing.astype(int).astype(str)
                              .agg("".join, axis=1).nunique()),
            "agreement": float(share.isin([0.0, 1.0]).mean()),
        })
    return pd.DataFrame(rows)


def depth(X, columns) -> pd.Series:
    """Number of absent columns in the block. Ordinal, 0 to len(columns)."""
    return X[columns].isna().sum(axis=1).astype(int)


class MissingnessEncoder:
    """Turn absence patterns into variables, before imputation destroys them.

    Fitted on the fitting split; the column lists it learns are then applied
    unchanged to validation and test.
    """

    def __init__(self, threshold: float = GAP_THRESHOLD):
        self.threshold = threshold

    def fit(self, X, y):
        groups = detect_groups(X, y, self.threshold)
        self.group1_ = groups["group1"]
        self.group2_ = groups["group2"]
        self.mute_ = groups["mute"]
        self.sub_blocks_ = sub_blocks(X, self.group2_)
        # One representative column per sub-block, alphabetically first so the
        # choice does not depend on the order the columns arrive in. Licensed
        # by sub_block_homogeneity, which notebook 01 reports.
        self.representatives_ = [members[0]
                                 for _, members in sorted(self.sub_blocks_.items())]
        self.flag_names_ = [f"missing_sb{i}"
                            for i in range(1, len(self.sub_blocks_) + 1)]
        return self

    def transform(self, X):
        X = X.copy()
        X["depth_g1"] = depth(X, self.group1_)
        for name, column in zip(self.flag_names_, self.representatives_):
            X[name] = X[column].isna().astype(int)
        return X

    def fit_transform(self, X, y):
        return self.fit(X, y).transform(X)
