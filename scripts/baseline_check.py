"""End-to-end smoke test of the preprocessing pipeline (EF02)."""

import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

warnings.filterwarnings("ignore", category=RuntimeWarning)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, average_precision_score

from src.data.split import get_train_val
from src.evaluation.cost import total_cost, optimal_threshold, best_threshold
from src.features.pipeline import build_pipeline
from src.utils.seeds import set_seed


def main() -> None:
    set_seed()
    X_fit, X_val, y_fit, y_val = get_train_val()
    print(f"Apprentissage : {X_fit.shape} | Validation : {X_val.shape}")

    pipeline = build_pipeline(
        LogisticRegression(max_iter=2000, class_weight="balanced", n_jobs=-1),
        imputation="median",
        log_transform=True,
        scale=True,
        resampling=None,
    )

    start = time.time()
    pipeline.fit(X_fit, y_fit)
    print(f"Entraînement terminé en {time.time() - start:.1f} s")

    proba = pipeline.predict_proba(X_val)[:, 1]

    print("\n--- Seuil par défaut 0.50 ---")
    predicted = (proba >= 0.50).astype(int)
    print(confusion_matrix(y_val, predicted))
    print(f"Coût : {total_cost(y_val, predicted)}")

    theoretical = optimal_threshold()
    print(f"\n--- Seuil théorique {theoretical:.4f} ---")
    predicted = (proba >= theoretical).astype(int)
    print(confusion_matrix(y_val, predicted))
    print(f"Coût : {total_cost(y_val, predicted)}")

    empirical, cost = best_threshold(y_val, proba)
    print(f"\n--- Seuil empirique optimal {empirical:.4f} ---")
    print(f"Coût : {cost}")

    print(f"\nAUC-ROC : {roc_auc_score(y_val, proba):.4f}")
    print(f"AUC-PR  : {average_precision_score(y_val, proba):.4f}")


if __name__ == "__main__":
    main()
