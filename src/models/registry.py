"""Model zoo for the classical ML benchmark (EF03)."""

from scipy.stats import loguniform, randint, uniform
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier

from src.config import SEED

POS_WEIGHT = 59.0


def get_registry(fast: bool = False) -> dict:
    n_trees = 100 if fast else 500

    return {
        "logistic_regression": {
            "estimator": LogisticRegression(
                solver="saga", max_iter=2000, class_weight="balanced",
                random_state=SEED, n_jobs=1,
            ),
            "pipeline": dict(imputation="median", log_transform=True,
                             scale=True, resampling=None),
            "params": {
                "model__C": loguniform(1e-3, 1e2),
                "model__penalty": ["l1", "l2"],
            },
        },

        "random_forest": {
            "estimator": RandomForestClassifier(
                n_estimators=n_trees, class_weight="balanced_subsample",
                random_state=SEED, n_jobs=1,
            ),
            "pipeline": dict(imputation="median", log_transform=False,
                             scale=False, resampling=None),
            "params": {
                "model__max_depth": [None, 10, 20, 30],
                "model__min_samples_leaf": randint(1, 20),
                "model__max_features": ["sqrt", "log2", 0.3],
            },
        },

        "xgboost": {
            "estimator": XGBClassifier(
                n_estimators=n_trees,
                scale_pos_weight=POS_WEIGHT,
                tree_method="hist",
                eval_metric="aucpr",
                random_state=SEED, n_jobs=1,
            ),
            "pipeline": dict(imputation=None, log_transform=False,
                             scale=False, resampling=None),
            "params": {
                "model__max_depth": randint(3, 9),
                "model__learning_rate": loguniform(0.01, 0.3),
                "model__subsample": uniform(0.6, 0.4),
                "model__colsample_bytree": uniform(0.5, 0.5),
                "model__min_child_weight": randint(1, 10),
            },
        },

        "linear_svm": {
            "estimator": CalibratedClassifierCV(
                LinearSVC(class_weight="balanced", dual="auto",
                          max_iter=5000, random_state=SEED),
                method="sigmoid", cv=3,
            ),
            "pipeline": dict(imputation="median", log_transform=True,
                             scale=True, resampling=None),
            "params": {
                "model__estimator__C": loguniform(1e-4, 1e1),
            },
        },
    }
