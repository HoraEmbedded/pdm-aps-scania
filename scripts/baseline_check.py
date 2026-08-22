"""End-to-end smoke test of the preprocessing pipeline (EF02).

Not a benchmark: a single logistic regression, to prove the chain runs from
raw CSV to a cost figure without manual intervention.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (average_precision_score, classification_report,  # noqa: E402
                             confusion_matrix, roc_auc_score)

from src.data.split import get_train_val  # noqa: E402
from src.evaluation.cost import best_threshold, optimal_threshold, total_cost  # noqa: E402
from src.features.pipeline import build_pipeline  # noqa: E402
from src.utils.seeds import set_seed  # noqa: E402


def main() -> None:
    set_seed()
    X_fit, X_val, y_fit, y_val = get_train_val()
    print(f"Apprentissage : {X_fit.shape} | Validation : {X_val.shape}")

    pipeline = build_pipeline(
        LogisticRegression(
            max_iter=2000,
            class_weight="balanced",   # compensates the 1 to 59 imbalance
            n_jobs=-1,
        ),
        imputation="median",
        log_transform=True,
        scale=True,
        resampling=None,               # class_weight already handles it
    )

    start = time.time()
    pipeline.fit(X_fit, y_fit)
    print(f"Entrainement termine en {time.time() - start:.1f} s")

    proba = pipeline.predict_proba(X_val)[:, 1]

    print("\n--- Seuil par defaut 0.50 ---")
    predicted = (proba >= 0.50).astype(int)
    print(confusion_matrix(y_val, predicted))
    print(classification_report(y_val, predicted, digits=3))
    print(f"Cout : {total_cost(y_val, predicted)}")

    theoretical = optimal_threshold()
    print(f"\n--- Seuil theorique {theoretical:.4f} ---")
    predicted = (proba >= theoretical).astype(int)
    print(confusion_matrix(y_val, predicted))
    print(f"Cout : {total_cost(y_val, predicted)}")

    empirical, cost = best_threshold(y_val, proba)
    print(f"\n--- Seuil empirique optimal {empirical:.4f} ---")
    print(f"Cout : {cost}")

    print(f"\nAUC-ROC : {roc_auc_score(y_val, proba):.4f}")
    print(f"AUC-PR  : {average_precision_score(y_val, proba):.4f}")


if __name__ == "__main__":
    main()