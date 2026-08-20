"""Structural analysis of the APS feature space.

The 170 sensor columns are not homogeneous: part of them are single counters,
the rest are histogram bins sharing a common prefix. Knowing which is which
drives the feature engineering strategy in week 3.
"""

from collections import defaultdict


def group_by_prefix(columns) -> dict:
    """Group column names by their prefix, e.g. ee_000..ee_009 -> 'ee'."""
    groups = defaultdict(list)
    for col in columns:
        if "_" in col:
            prefix = col.rsplit("_", 1)[0]
            groups[prefix].append(col)
    return {prefix: sorted(cols) for prefix, cols in groups.items()}


def histogram_groups(columns, min_bins: int = 10) -> dict:
    """Prefixes owning at least `min_bins` columns: these are histograms."""
    return {
        prefix: cols
        for prefix, cols in group_by_prefix(columns).items()
        if len(cols) >= min_bins
    }


def single_counters(columns, min_bins: int = 10) -> list:
    """Columns that stand alone: plain numeric counters."""
    groups = group_by_prefix(columns)
    return sorted(
        col
        for prefix, cols in groups.items()
        if len(cols) < min_bins
        for col in cols
    )

