"""Extract the information carried by missing values (decision D-09).

Two groups emerge from the per-class absence rates:
  group 1: 8 nested columns, summed into one ordinal variable
  group 2: 56 columns forming sub-blocks by absence rate, one flag each
Detection runs on the fitting split only.
"""

import numpy as np
import pandas as pd

from src.config import SEUIL_ECART


def taux_par_classe(X, y):
    """Absence rate of each column, within each class."""
    absences = X.isna().astype(int)
    return pd.DataFrame({
        "taux_aps": absences[y == 1].mean(),
        "taux_autres": absences[y == 0].mean(),
    })


def detecte_groupes(X, y, seuil: float = SEUIL_ECART):
    """Split columns into group 1, group 2 and mute columns.

    Group 1: absent far more often among non-APS failures.
    Group 2: absent far more often among APS failures.
    The threshold is a declared choice, not a natural cut: the sorted gaps
    form a continuum with no gap (D-09 §7). It was written before the
    computation, which is discipline rather than robustness.
    """
    t = taux_par_classe(X, y)
    ecart = t["taux_autres"] - t["taux_aps"]

    groupe1 = ecart[ecart > seuil].index.tolist()
    groupe2 = ecart[ecart < -seuil].index.tolist()
    muettes = ecart[ecart.abs() <= seuil].index.tolist()

    # Order by increasing absence rate: required by the nesting test
    absences = X.isna()
    groupe1 = absences[groupe1].mean().sort_values().index.tolist()
    groupe2 = absences[groupe2].mean().sort_values().index.tolist()

    return {"groupe1": groupe1, "groupe2": groupe2, "muettes": muettes,
            "ecart": ecart.sort_values(ascending=False)}


def test_emboitement(X, colonnes):
    """Is absence nested along these columns, taken in the given order?

    Nesting means: once a column is absent, every column after it is too.
    In the 0/1 string of a row, that forbids the pattern "10".

    Counting distinct patterns is NOT a proof: 9 patterns out of 256 is what
    nesting produces, but any 9 patterns give the same count.
    """
    motifs = X[colonnes].isna().astype(int).astype(str).agg("".join, axis=1)
    emboites = motifs.map(lambda m: "10" not in m)
    return {
        "n_motifs": int(motifs.nunique()),
        "n_possibles": 2 ** len(colonnes),
        "part_emboitee": float(emboites.mean()),
        "effectifs": motifs.value_counts(),
    }


def sous_blocs(X, colonnes, decimales: int = 3) -> dict:
    """Group columns by rounded absence rate: these are the sub-blocks."""
    taux = X[colonnes].isna().mean().round(decimales)
    return {t: sorted(taux[taux == t].index.tolist())
            for t in sorted(taux.unique())}


def profondeur(X, colonnes) -> pd.Series:
    """Number of absent columns in the block. Ordinal, 0 to len(colonnes)."""
    return X[colonnes].isna().sum(axis=1).astype(int)


class ExtracteurAbsences:
    """Turn absence patterns into variables, before imputation destroys them.

    Fitted on the fitting split; the column lists it learns are then applied
    unchanged to validation and test.
    """

    def __init__(self, seuil: float = SEUIL_ECART):
        self.seuil = seuil

    def fit(self, X, y):
        g = detecte_groupes(X, y, self.seuil)
        self.groupe1_ = g["groupe1"]
        self.groupe2_ = g["groupe2"]
        self.muettes_ = g["muettes"]
        self.sous_blocs_ = sous_blocs(X, self.groupe2_)
        self.noms_indicatrices_ = [f"absent_sb{i}"
                                   for i in range(1, len(self.sous_blocs_) + 1)]
        return self

    def transform(self, X):
        X = X.copy()
        X["profondeur_g1"] = profondeur(X, self.groupe1_)
        for nom, (_, membres) in zip(self.noms_indicatrices_,
                                     sorted(self.sous_blocs_.items())):
            # One flag per sub-block: the first member represents it, the
            # block being homogeneous or near-homogeneous by construction
            X[nom] = X[membres[0]].isna().astype(int)
        return X

    def fit_transform(self, X, y):
        return self.fit(X, y).transform(X)
