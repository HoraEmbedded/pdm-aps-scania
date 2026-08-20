"""Scania asymmetric cost metric and threshold utilities ."""

import numpy as np
from sklearn.metrics import confusion_matrix

from src.config import COST_FN, COST_FP


def total_cost(y_true, y_pred, cost_fp=COST_FP, cost_fn=COST_FN) -> int:
    """Total maintenance cost = 10 * false positives + 500 * false negatives."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return int(cost_fp * fp + cost_fn * fn)


def optimal_threshold(cost_fp=COST_FP, cost_fn=COST_FN) -> float:
    """Bayes-optimal threshold for a calibrated probability: 10 / 510."""
    return cost_fp / (cost_fp + cost_fn)


def cost_at_threshold(y_true, y_proba, threshold: float) -> int:
    return total_cost(y_true, (np.asarray(y_proba) >= threshold).astype(int))


def best_threshold(y_true, y_proba, grid=None):
    """Empirical threshold minimising the cost, plus the cost reached."""
    if grid is None:
        grid = np.linspace(0.001, 0.999, 999)
    costs = [cost_at_threshold(y_true, y_proba, t) for t in grid]
    index = int(np.argmin(costs))
    return float(grid[index]), int(costs[index])


def baseline_costs(y_true) -> dict:
    """Reference costs of the two naive rules, required by section 12."""
    y_true = np.asarray(y_true)
    return {
        "always_negative": total_cost(y_true, np.zeros_like(y_true)),
        "always_positive": total_cost(y_true, np.ones_like(y_true)),
    }

