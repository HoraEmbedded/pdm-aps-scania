"""Model zoo. Class weighting is 50:1, from the cost matrix (D-11)."""

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from xgboost import XGBClassifier

from src.config import GRAINE, PONDERATION, RAPPORT_COUT
from sklearn.linear_model import SGDClassifier


def regression_logistique(C: float = 0.01):
    return LogisticRegression(C=C, solver="liblinear", max_iter=2000,
                              class_weight=PONDERATION, random_state=GRAINE)


def foret_aleatoire(n_arbres: int = 300, profondeur_max=None,
                    min_feuille: int = 1):
    return RandomForestClassifier(
        n_estimators=n_arbres, max_depth=profondeur_max,
        min_samples_leaf=min_feuille, class_weight=PONDERATION,
        random_state=GRAINE, n_jobs=-1)


def xgboost(profondeur: int = 6, taux: float = 0.1, n_arbres: int = 300):
    # scale_pos_weight is the same 50:1 ratio, applied to the gradient
    return XGBClassifier(
        n_estimators=n_arbres, max_depth=profondeur, learning_rate=taux,
        scale_pos_weight=RAPPORT_COUT, tree_method="hist",
        eval_metric="aucpr", random_state=GRAINE, n_jobs=-1)


def svm_lineaire(C: float = 0.01):
    """LinearSVC has no predict_proba: Platt calibration wraps it."""
    return CalibratedClassifierCV(
        LinearSVC(C=C, class_weight=PONDERATION, dual="auto",
                  max_iter=5000, random_state=GRAINE),
        method="sigmoid", cv=3)


def svm_rbf(C: float = 1.0, gamma="scale"):
    """probability=True adds an internal 5-fold Platt calibration: slow."""
    return SVC(C=C, kernel="rbf", gamma=gamma, class_weight=PONDERATION,
               probability=True, random_state=GRAINE)



class PerceptronKeras(BaseEstimator, ClassifierMixin):
    """Keras MLP behind the scikit-learn interface, so evalue can use it.

    perte : "standard" uses binary cross-entropy with class weighting, which
            is the benchmark configuration. Any other value must be a callable
            returning a Keras-compatible loss.
    ponderation : whether to pass class_weight to fit. Must be False when the
            loss already carries the cost matrix, otherwise the ratio enters
            the chain twice, which is the error decision D-11 corrects.
    """

    def __init__(self, couches=(64, 32), dropout=0.3, lr=1e-3,
                 epochs=20, batch=512, perte="standard", ponderation=True):
        self.couches = couches
        self.dropout = dropout
        self.lr = lr
        self.epochs = epochs
        self.batch = batch
        self.perte = perte
        self.ponderation = ponderation

    def fit(self, X, y):
        from tensorflow import keras
        keras.utils.set_random_seed(GRAINE)

        X = np.asarray(X, dtype="float32")
        y = np.asarray(y).astype("float32")
        self.classes_ = np.array([0, 1])

        m = keras.Sequential([keras.Input(shape=(X.shape[1],))])
        for u in self.couches:
            m.add(keras.layers.Dense(u, activation="relu"))
            m.add(keras.layers.Dropout(self.dropout))

        biais = float(np.log(y.sum() / (len(y) - y.sum())))
        m.add(keras.layers.Dense(
            1, activation="sigmoid",
            bias_initializer=keras.initializers.Constant(biais)))

        perte = ("binary_crossentropy" if self.perte == "standard"
                 else self.perte)
        m.compile(optimizer=keras.optimizers.Adam(self.lr), loss=perte)

        m.fit(X, y, epochs=self.epochs, batch_size=self.batch,
              class_weight=PONDERATION if self.ponderation else None,
              verbose=0)
        self.modele_ = m
        return self

    def predict_proba(self, X):
        p = self.modele_.predict(np.asarray(X, dtype="float32"),
                                 batch_size=1024, verbose=0).ravel()
        return np.c_[1 - p, p]

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)
