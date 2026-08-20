"""Unified evaluation: every model of the benchmark goes through here.

A single function guarantees the identical protocol required by EF05.
Accepts either calibrated probabilities or raw decision scores.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.evaluation.cost import (
    baseline_costs,
    best_threshold,
    optimal_threshold,
    total_cost,
)


def get_scores(fitted_model, X):
    """Return (score, is_probability) for any scikit-learn classifier."""
    if hasattr(fitted_model, "predict_proba"):
        return fitted_model.predict_proba(X)[:, 1], True
    return fitted_model.decision_function(X), False


def evaluate(y_true, y_score, is_probability: bool = True,
             model_name: str = "", fit_seconds: float = None) -> dict:
    """Compute the full metric set at three decision thresholds.

    Threshold 1: 0.5, the library default, reported to show how bad it is here.
    Threshold 2: the Bayes-optimal one, only meaningful on probabilities.
    Threshold 3: the empirical minimiser of the cost on this very set.
    """
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)

    result = {"model": model_name}
    if fit_seconds is not None:
        result["fit_seconds"] = round(fit_seconds, 1)

    # Threshold-free metrics: the honest way to rank models under imbalance
    result["roc_auc"] = roc_auc_score(y_true, y_score)
    result["pr_auc"] = average_precision_score(y_true, y_score)
    
    # Empirical best threshold and the cost it reaches
    thr_best, cost_best = best_threshold(y_true, y_score)
    result["threshold_best"] = round(thr_best, 4)
    result["cost_best"] = cost_best

    # Full picture at that operating point
    y_pred = (y_score >= thr_best).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    result.update({
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    })

    # Reference operating points
    if is_probability:
        result["cost_at_0.5"] = total_cost(y_true, (y_score >= 0.5).astype(int))
        thr_theory = optimal_threshold()
        result["cost_at_theory"] = total_cost(
            y_true, (y_score >= thr_theory).astype(int)
        )
    else:
        # A raw decision score has no calibrated 0.5 and no Bayes threshold
        result["cost_at_0.5"] = None
        result["cost_at_theory"] = None

    # Gain against the cheaper naive rule, computed on THIS set
    naive = min(baseline_costs(y_true).values())
    result["naive_cost"] = naive
    result["cost_ratio"] = round(cost_best / naive, 4)

    return result


def to_table(results: list) -> pd.DataFrame:
    """Assemble evaluation dicts into the benchmark table, best cost first."""
    frame = pd.DataFrame(results)
    return frame.sort_values("cost_best").reset_index(drop=True)

