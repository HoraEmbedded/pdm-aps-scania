"""Model factories for the benchmark.

Class weighting is 50:1 throughout, taken from the cost matrix (decision D-11).
"""

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier

from src.config import CLASS_WEIGHT, COST_RATIO, SEED


def logistic_regression(C: float = 0.01):
    return LogisticRegression(C=C, solver="liblinear", max_iter=2000,
                              class_weight=CLASS_WEIGHT, random_state=SEED)


def random_forest(n_trees: int = 300, max_depth=None,
                  min_samples_leaf: int = 1):
    return RandomForestClassifier(
        n_estimators=n_trees, max_depth=max_depth,
        min_samples_leaf=min_samples_leaf, class_weight=CLASS_WEIGHT,
        random_state=SEED, n_jobs=-1)


def gradient_boosting(max_depth: int = 6, learning_rate: float = 0.1,
                      n_trees: int = 300):
    # scale_pos_weight applies the same 50:1 ratio to the gradient.
    return XGBClassifier(
        n_estimators=n_trees, max_depth=max_depth, learning_rate=learning_rate,
        scale_pos_weight=COST_RATIO, tree_method="hist", eval_metric="aucpr",
        random_state=SEED, n_jobs=-1)


def linear_svm(C: float = 0.01):
    # LinearSVC exposes no predict_proba, hence the Platt calibration wrapper.
    return CalibratedClassifierCV(
        LinearSVC(C=C, class_weight=CLASS_WEIGHT, dual="auto", max_iter=5000,
                  random_state=SEED),
        method="sigmoid", cv=3)


class KerasPerceptron(BaseEstimator, ClassifierMixin):
    """Keras MLP behind the scikit-learn interface, so evaluate can run it.

    loss: "standard" is weighted binary cross-entropy, the benchmark
        configuration. Any other value must be a callable returning a Keras
        loss, as produced by src.losses.
    weighted: must be False when the loss already carries the cost matrix,
        otherwise the ratio enters the chain twice (decision D-11).
    """

    def __init__(self, units=(64, 32), dropout=0.3, learning_rate=1e-3,
                 epochs=20, batch_size=512, loss="standard", weighted=True):
        self.units = units
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.loss = loss
        self.weighted = weighted

    def fit(self, X, y):
        from tensorflow import keras
        keras.utils.set_random_seed(SEED)

        X = np.asarray(X, dtype="float32")
        y = np.asarray(y).astype("float32")
        self.classes_ = np.array([0, 1])

        network = keras.Sequential([keras.Input(shape=(X.shape[1],))])
        for size in self.units:
            network.add(keras.layers.Dense(size, activation="relu"))
            network.add(keras.layers.Dropout(self.dropout))

        # Output bias initialised at the log odds of the positive class, so
        # training starts from the base rate instead of 0.5.
        bias = float(np.log(y.sum() / (len(y) - y.sum())))
        network.add(keras.layers.Dense(
            1, activation="sigmoid",
            bias_initializer=keras.initializers.Constant(bias)))

        loss = "binary_crossentropy" if self.loss == "standard" else self.loss
        network.compile(optimizer=keras.optimizers.Adam(self.learning_rate),
                        loss=loss)
        network.fit(X, y, epochs=self.epochs, batch_size=self.batch_size,
                    class_weight=CLASS_WEIGHT if self.weighted else None,
                    verbose=0)
        self.network_ = network
        return self

    def predict_proba(self, X):
        p = self.network_.predict(np.asarray(X, dtype="float32"),
                                  batch_size=1024, verbose=0).ravel()
        return np.c_[1 - p, p]

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)
