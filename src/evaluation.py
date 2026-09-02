"""Cross-validated evaluation under the frozen protocol.

The cost ratio enters the chain exactly once, through class weighting, and the
decision threshold is then measured rather than derived (decision D-11). The
threshold is tuned on out-of-sample probabilities obtained by an inner
cross-validation inside each fold; the first implementation tuned it on the
fold's own training rows, which is near-meaningless on any model that fits its
training set closely (docs/technical_decisions.md).
"""

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from src.config import COST_FN, N_FOLDS, N_INNER_FOLDS, SEED
from src.cost import best_threshold, total_cost, unweight

SUMMARY_COLUMNS = ["cost", "recall", "precision", "auc", "auc_pr",
                   "TP", "FP", "FN", "threshold", "unweighted_threshold"]


def _positive_probability(model, X):
    return model.predict_proba(X)[:, 1]


def _as_frame(X):
    return X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)


def _evaluate_with_cv(factory, X, y, cv, name, n_inner, n_jobs, seed,
                      out_of_sample_threshold=True):
    rows = []

    for fold, (fit_idx, eval_idx) in enumerate(cv.split(X, y), start=1):
        X_fit, X_eval = X.iloc[fit_idx], X.iloc[eval_idx]
        y_fit, y_eval = y[fit_idx], y[eval_idx]

        if out_of_sample_threshold:
            inner_cv = StratifiedKFold(n_splits=n_inner, shuffle=True,
                                       random_state=seed)
            p_fit = cross_val_predict(factory(), X_fit, y_fit, cv=inner_cv,
                                      method="predict_proba",
                                      n_jobs=n_jobs)[:, 1]
        else:
            in_sample = factory()
            in_sample.fit(X_fit, y_fit)
            p_fit = _positive_probability(in_sample, X_fit)
        threshold, _ = best_threshold(y_fit, p_fit)

        model = factory()
        model.fit(X_fit, y_fit)
        p_eval = _positive_probability(model, X_eval)
        predicted = (p_eval >= threshold).astype(int)

        tp = int(((predicted == 1) & (y_eval == 1)).sum())
        fp = int(((predicted == 1) & (y_eval == 0)).sum())
        fn = int(((predicted == 0) & (y_eval == 1)).sum())
        tn = int(((predicted == 0) & (y_eval == 0)).sum())

        rows.append({
            "model": name, "fold": fold,
            "cost": total_cost(y_eval, predicted),
            "recall": tp / (tp + fn) if tp + fn else np.nan,
            "precision": tp / (tp + fp) if tp + fp else np.nan,
            "auc": roc_auc_score(y_eval, p_eval),
            "auc_pr": average_precision_score(y_eval, p_eval),
            "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "threshold": threshold,
            "unweighted_threshold": float(unweight(threshold)),
        })

    return pd.DataFrame(rows)


def evaluate(factory, X, y, name: str = "", n_folds: int = N_FOLDS,
             n_inner: int = N_INNER_FOLDS, out_of_sample_threshold: bool = True,
             n_jobs: int = -1, seed: int = SEED):
    """Run the frozen protocol on one model. One row per fold.

    factory: a callable returning a fresh untrained model on each call.
    out_of_sample_threshold=False reproduces the first, leaky implementation;
    it is kept because the comparison between the two is a reported result.
    """
    X = _as_frame(X)
    y = np.asarray(y).ravel()
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    return _evaluate_with_cv(factory, X, y, cv, name, n_inner, n_jobs, seed,
                             out_of_sample_threshold)


def evaluate_repeated(factory, X, y, name: str = "", n_repeats: int = 6,
                      n_folds: int = N_FOLDS, n_inner: int = N_INNER_FOLDS,
                      n_jobs: int = -1):
    """Repeat the whole cross-validation with different fold partitions.

    Each repeat reseeds the outer split, so a paired comparison rests on
    n_repeats * n_folds measurements. The standard error on a paired difference
    falls as the square root of the number of repeats, which is what makes
    small effects detectable at all.
    """
    X = _as_frame(X)
    y = np.asarray(y).ravel()

    parts = []
    for repeat in range(n_repeats):
        seed = SEED + repeat
        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
        part = _evaluate_with_cv(factory, X, y, cv, name, n_inner, n_jobs, seed)
        part["repeat"] = repeat
        parts.append(part)

    return pd.concat(parts, ignore_index=True)


def summarise(results: pd.DataFrame) -> pd.DataFrame:
    """Mean and standard deviation across folds, as the protocol requires."""
    return pd.DataFrame({"mean": results[SUMMARY_COLUMNS].mean(),
                         "std": results[SUMMARY_COLUMNS].std()}).round(4)


def report(results: pd.DataFrame, name: str = "") -> None:
    """Print the arbitration criterion first, the details after."""
    mean, std = results["cost"].mean(), results["cost"].std()
    rows_per_fold = results[["TP", "FP", "FN", "TN"]].sum(axis=1).mean()
    positives_per_fold = (results["TP"] + results["FN"]).mean()

    print("=" * 58)
    print(f"  {name or results['model'].iloc[0]}")
    print("=" * 58)
    print(f"  MEAN COST : {mean:>10,.0f}  +/-  {std:,.0f}")
    print("=" * 58)
    print(f"  fold scale        : {rows_per_fold:,.0f} rows, "
          f"{positives_per_fold:.0f} failures")
    print(f"  never-flag rule   : {COST_FN * positives_per_fold:,.0f}")
    print(f"  mean unweighted threshold : "
          f"{results['unweighted_threshold'].mean():.4f}\n")
    print(summarise(results).to_string())
