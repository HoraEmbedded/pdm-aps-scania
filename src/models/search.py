"""Hyper-parameter search under the frozen evaluation protocol (EF03/EF05).

Selection uses a threshold-free metric on cross-validation; the decision
threshold is tuned afterwards on the held-out validation split.
"""

import time
import numpy as np
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV

from src.config import SEED
from src.data.split import get_cv
from src.evaluation.cost import optimal_threshold, total_cost
from src.features.pipeline import build_pipeline


def cost_at_fixed_threshold(y_true, y_proba) -> int:
    """Scania cost at the data-independent Bayes threshold."""
    return total_cost(y_true, (np.asarray(y_proba) >= optimal_threshold()).astype(int))


FIXED_COST_SCORER = make_scorer(
    cost_at_fixed_threshold,
    greater_is_better=False,
    response_method="predict_proba",
)


def run_search(name: str, spec: dict, X_fit, y_fit, n_iter: int = 20, verbose: int = 1):
    """Randomised search over the model's space, under the shared CV protocol."""
    pipeline = build_pipeline(spec["estimator"], **spec["pipeline"])

    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=spec["params"],
        n_iter=n_iter,
        scoring={
            "pr_auc": "average_precision",
            "roc_auc": "roc_auc",
            "fixed_cost": FIXED_COST_SCORER,
        },
        refit="pr_auc",
        cv=get_cv(),
        random_state=SEED,
        n_jobs=-1,
        verbose=verbose,
        error_score="raise",
    )

    start = time.time()
    search.fit(X_fit, y_fit)
    elapsed = time.time() - start

    print(f"[{name}] {n_iter} configurations en {elapsed / 60:.1f} min")
    print(f"[{name}] meilleure AUC-PR en CV : {search.best_score_:.4f}")
    print(f"[{name}] meilleurs parametres : {search.best_params_}")

    return search, elapsed
