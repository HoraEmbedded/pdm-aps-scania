"""Differentiated imputation and scaling (decisions D-10 and step 3.6).

Written by hand rather than with ColumnTransformer, which reorders columns
and is a classic source of silent misalignment.
"""

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.config import PREPARE


class Preparateur:
    """Impute, then scale. Everything is learned on the fitting split only.

    Group 1 is imputed with zero, not the median. Its columns are absent for
    the least-used trucks, so the median of the 18% that do have a value is
    the median of a heavily-used population, not of the general one. Filling
    82% of the column with a large constant states the opposite of the truth.
    Zero already exists legitimately in the file, so the value is not
    artificial (step 3.6).

    profondeur_g1 and the sub-block flags are not scaled: their amplitude is
    already of the right order, and scaling would make them unreadable when
    interpreting coefficients.
    """

    def __init__(self, groupe1, non_normalisees):
        self.groupe1 = list(groupe1)
        self.non_normalisees = list(non_normalisees)

    def fit(self, X):
        self.colonnes_ = list(X.columns)
        self.autres_ = [c for c in X.columns if c not in self.groupe1]
        self.medianes_ = X[self.autres_].median()          # fitting split only

        self.a_normaliser_ = [c for c in X.columns
                              if c not in self.non_normalisees]
        X_impute = self._impute(X)
        self.echelle_ = StandardScaler().fit(X_impute[self.a_normaliser_])
        return self

    def _impute(self, X):
        X = X.copy()
        X[self.groupe1] = X[self.groupe1].fillna(0.0)
        X[self.autres_] = X[self.autres_].fillna(self.medianes_)
        return X

    def transform(self, X):
        X = self._impute(X)[self.colonnes_]
        X[self.a_normaliser_] = self.echelle_.transform(X[self.a_normaliser_])
        return X

    def fit_transform(self, X):
        return self.fit(X).transform(X)


def sauvegarde(objet, nom: str):
    PREPARE.mkdir(parents=True, exist_ok=True)
    joblib.dump(objet, PREPARE / nom)


def recharge(nom: str):
    return joblib.load(PREPARE / nom)
