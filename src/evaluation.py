"""Cross-validated evaluation under the frozen protocol.

Threshold handling follows decision D-11: the cost ratio enters the chain
exactly once, through class weighting, and the threshold is then measured
rather than derived.

Correction on the first implementation: the threshold used to be tuned on
predict_proba of the fold's own training rows, which the model had just
memorised. On a random forest, in-sample probabilities are near-perfect, so
the threshold found would be excellent in-sample and arbitrary out of it.
It is now tuned on out-of-sample probabilities obtained by an inner
cross-validation inside the fold.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import average_precision_score, roc_auc_score

from src.config import GRAINE, N_PLIS, N_PLIS_INTERNES
from src.cout import cout_scania, depondere, meilleur_seuil


def _proba(modele, X):
    """Probabilities from any classifier exposing predict_proba."""
    return modele.predict_proba(X)[:, 1]


def evalue(fabrique, X, y, nom: str = "", n_plis: int = N_PLIS,
           n_internes: int = N_PLIS_INTERNES,
           seuil_hors_echantillon: bool = True, n_jobs: int = -1):
    """Run the frozen protocol on one model. One row per fold.

    fabrique: a callable returning a FRESH untrained model each time.
    """
    X = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
    y = np.asarray(y).ravel()

    vc = StratifiedKFold(n_splits=n_plis, shuffle=True, random_state=GRAINE)
    lignes = []

    for i, (idx_app, idx_ev) in enumerate(vc.split(X, y), start=1):
        X_a, X_e = X.iloc[idx_app], X.iloc[idx_ev]
        y_a, y_e = y[idx_app], y[idx_ev]

        # --- Seuil ---------------------------------------------------------
        if seuil_hors_echantillon:
            vc_interne = StratifiedKFold(n_splits=n_internes, shuffle=True,
                                         random_state=GRAINE)
            p_a = cross_val_predict(fabrique(), X_a, y_a, cv=vc_interne,
                                    method="predict_proba", n_jobs=n_jobs)[:, 1]
        else:
            # ancienne version : probabilités en interne, pour comparaison
            m = fabrique()
            m.fit(X_a, y_a)
            p_a = _proba(m, X_a)
        seuil, _ = meilleur_seuil(y_a, p_a)

        # --- Modèle final du pli, entraîné sur tout X_a ------------------
        modele = fabrique()
        modele.fit(X_a, y_a)
        p_e = _proba(modele, X_e)
        pred = (p_e >= seuil).astype(int)

        vp = int(((pred == 1) & (y_e == 1)).sum())
        fp = int(((pred == 1) & (y_e == 0)).sum())
        fn = int(((pred == 0) & (y_e == 1)).sum())
        vn = int(((pred == 0) & (y_e == 0)).sum())

        lignes.append({
            "modele": nom, "pli": i,
            "cout": cout_scania(y_e, pred),
            "rappel": vp / (vp + fn) if vp + fn else np.nan,
            "precision": vp / (vp + fp) if vp + fp else np.nan,
            "auc": roc_auc_score(y_e, p_e),
            "auc_pr": average_precision_score(y_e, p_e),
            "VP": vp, "FP": fp, "FN": fn, "VN": vn,
            "seuil": seuil,
            "seuil_depondere": float(depondere(seuil)),
        })

    return pd.DataFrame(lignes)


def resume(resultats: pd.DataFrame) -> pd.DataFrame:
    """Mean and standard deviation across folds, as the protocol requires."""
    cols = ["cout", "rappel", "precision", "auc", "auc_pr",
            "VP", "FP", "FN", "seuil", "seuil_depondere"]
    return pd.DataFrame({"moyenne": resultats[cols].mean(),
                         "ecart_type": resultats[cols].std()}).round(4)


def affiche(resultats: pd.DataFrame, nom: str = "") -> None:
    """Print the arbitration criterion first, the details after."""
    moy, ect = resultats["cout"].mean(), resultats["cout"].std()
    print("=" * 58)
    print(f"  {nom or resultats['modele'].iloc[0]}")
    print("=" * 58)
    print(f"  COÛT MOYEN : {moy:>10,.0f}  ±  {ect:,.0f}")
    print("=" * 58)
    print(f"  échelle d'un pli : 9 600 lignes, ~160 pannes")
    print(f"  règle naïve sur un pli : 80 000")
    print(f"  seuil dépondéré moyen : "
          f"{resultats['seuil_depondere'].mean():.4f}  (repère 0,0196)\n")
    print(resume(resultats).to_string())

def evalue_repete(fabrique, X, y, nom: str = "", n_repetitions: int = 6,
                  n_plis: int = N_PLIS, n_internes: int = N_PLIS_INTERNES,
                  n_jobs: int = -1):
    """Repeat the whole cross-validation with different fold partitions.

    Each repetition uses a different seed for the outer split, so the paired
    comparison rests on n_repetitions * n_plis measurements instead of n_plis.
    The standard error on a paired difference falls as the square root of the
    number of repetitions, which is what makes small effects detectable.
    """
    import pandas as pd

    morceaux = []
    for repetition in range(n_repetitions):
        graine = GRAINE + repetition
        vc = StratifiedKFold(n_splits=n_plis, shuffle=True, random_state=graine)
        r = _evalue_avec_vc(fabrique, X, y, vc, nom, n_internes, n_jobs, graine)
        r["repetition"] = repetition
        morceaux.append(r)
    return pd.concat(morceaux, ignore_index=True)

