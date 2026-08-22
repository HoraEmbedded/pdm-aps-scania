"""Scania cost function and threshold sweep.

False alarm costs 10, missed failure costs 500. Ratio 50:1. Lower is better.
"""

import numpy as np

from src.config import COUT_FN, COUT_FP, RAPPORT_COUT, SEUIL_BAYES


def cout_scania(y_vrai, y_predit) -> int:
    """Total Scania cost of a set of binary predictions.

    Counts are written explicitly rather than read from confusion_matrix,
    whose four-value ordering is a classic source of silent errors.
    """
    y_vrai = np.asarray(y_vrai)
    y_predit = np.asarray(y_predit)

    fp = int(((y_predit == 1) & (y_vrai == 0)).sum())
    fn = int(((y_predit == 0) & (y_vrai == 1)).sum())

    return COUT_FP * fp + COUT_FN * fn


def meilleur_seuil(y_vrai, proba):
    """Cheapest threshold, using `proba >= seuil` as the decision rule.

    Vectorised: sort once by decreasing probability, then read the confusion
    counts off cumulative sums. Equivalent to sweeping every observed
    probability in a loop, but O(n log n) instead of O(n^2).

    Returns (threshold, cost).
    """
    y = np.asarray(y_vrai).astype(int)
    p = np.asarray(proba, dtype=float)

    ordre = np.argsort(-p, kind="mergesort")
    y_tri, p_tri = y[ordre], p[ordre]
    n_pos = int(y.sum())

    # Thresholding at p_tri[k] flags exactly the first k+1 rows
    vp = np.cumsum(y_tri)
    fp = np.cumsum(1 - y_tri)
    fn = n_pos - vp
    couts = COUT_FP * fp + COUT_FN * fn

    # With ties, only the last occurrence of each distinct value is a valid
    # cut point: every row sharing that probability is flagged together.
    garder = np.r_[p_tri[1:] != p_tri[:-1], True]
    couts_valides, seuils_valides = couts[garder], p_tri[garder]

    # Degenerate case: flag nothing at all
    cout_vide = COUT_FN * n_pos
    k = int(np.argmin(couts_valides))
    if cout_vide < couts_valides[k]:
        return float(p_tri[0]) + 1e-9, int(cout_vide)

    return float(seuils_valides[k]), int(couts_valides[k])


def depondere(p_ponderee):
    """Undo the 50:1 class weighting to recover a comparable probability.

    Weighting by 50 multiplies the odds by 50, so the model outputs
    p_w = 50p / (1 + 49p). This inverts it. Required before comparing an
    empirical threshold to SEUIL_BAYES (D-11 §4): comparing the raw weighted
    threshold to 1.96% would reapply the ratio and give an effective 2501:1.
    """
    p_ponderee = np.asarray(p_ponderee, dtype=float)
    return p_ponderee / (RAPPORT_COUT - (RAPPORT_COUT - 1) * p_ponderee)


def seuil_bayes_pondere() -> float:
    """Where SEUIL_BAYES lands on the weighted scale. Equals exactly 0.5."""
    p = SEUIL_BAYES
    return RAPPORT_COUT * p / (1 + (RAPPORT_COUT - 1) * p)


def couts_naifs(y_vrai) -> dict:
    """Cost of the two constant rules, computed on the set at hand."""
    y = np.asarray(y_vrai)
    return {
        "toujours_sain": cout_scania(y, np.zeros_like(y)),
        "toujours_panne": cout_scania(y, np.ones_like(y)),
    }
