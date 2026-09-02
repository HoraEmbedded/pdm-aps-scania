"""Scania cost function and threshold sweep.

A false alarm costs 10, a missed failure 500. Lower is better.
"""

import numpy as np

from src.config import BAYES_THRESHOLD, COST_FN, COST_FP, COST_RATIO


def total_cost(y_true, y_predicted) -> int:
    y_true = np.asarray(y_true)
    y_predicted = np.asarray(y_predicted)

    fp = int(((y_predicted == 1) & (y_true == 0)).sum())
    fn = int(((y_predicted == 0) & (y_true == 1)).sum())

    return COST_FP * fp + COST_FN * fn


def best_threshold(y_true, probability):
    """Cheapest threshold under the rule `probability >= threshold`.

    Sorts once by decreasing probability and reads the confusion counts off
    cumulative sums, so O(n log n) instead of sweeping every observed value.

    Returns (threshold, cost).
    """
    y = np.asarray(y_true).astype(int)
    p = np.asarray(probability, dtype=float)

    order = np.argsort(-p, kind="mergesort")
    y_sorted, p_sorted = y[order], p[order]
    n_positive = int(y.sum())

    tp = np.cumsum(y_sorted)
    fp = np.cumsum(1 - y_sorted)
    fn = n_positive - tp
    costs = COST_FP * fp + COST_FN * fn

    # With ties, only the last occurrence of a value is a valid cut point:
    # every row sharing that probability is flagged together.
    is_cut = np.r_[p_sorted[1:] != p_sorted[:-1], True]
    valid_costs, valid_thresholds = costs[is_cut], p_sorted[is_cut]

    flag_nothing = COST_FN * n_positive
    best = int(np.argmin(valid_costs))
    if flag_nothing < valid_costs[best]:
        return float(p_sorted[0]) + 1e-9, int(flag_nothing)

    return float(valid_thresholds[best]), int(valid_costs[best])


def unweight(weighted_probability):
    """Invert the 50:1 class weighting to recover a comparable probability.

    Weighting multiplies the odds by COST_RATIO, so the model outputs
    p_w = r*p / (1 + (r - 1)*p). Comparing a weighted threshold directly to
    BAYES_THRESHOLD would apply the cost ratio a second time (decision D-11).
    """
    p = np.asarray(weighted_probability, dtype=float)
    return p / (COST_RATIO - (COST_RATIO - 1) * p)


def weighted_bayes_threshold() -> float:
    """Where BAYES_THRESHOLD lands on the weighted scale. Equals exactly 0.5."""
    return COST_RATIO * BAYES_THRESHOLD / (1 + (COST_RATIO - 1) * BAYES_THRESHOLD)


def constant_rule_costs(y_true) -> dict:
    """Cost of the two constant rules, and which one is cheaper.

    Which rule wins depends on whether the positive rate sits above or below
    BAYES_THRESHOLD, so the answer is not a property of the problem but of the
    sample. It flips between the split taken from the training file (1.67%
    positives) and the official test file (2.34%), which is why the reference
    to beat has to be stated per dataset (docs/technical_decisions.md).
    """
    y = np.asarray(y_true)
    never = total_cost(y, np.zeros_like(y))
    always = total_cost(y, np.ones_like(y))
    rate = float(y.mean())

    return {
        "never_flag": never,
        "always_flag": always,
        "cheaper": "never_flag" if never < always else "always_flag",
        "reference": min(never, always),
        "positive_rate": rate,
        "break_even_rate": BAYES_THRESHOLD,
        "above_break_even": rate > BAYES_THRESHOLD,
    }
