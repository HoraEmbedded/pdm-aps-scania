"""Cross-validation training and hyperparameter optimization script (EF03/EF04)."""

import argparse
import time
from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold

from src.config import DATA_DIR, METRICS_DIR, SEED
from src.evaluation.report import evaluate, get_scores, to_table
from src.features.pipeline import build_pipeline
from src.models.registry import get_registry

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)


def run_benchmark(n_iter: int = 15, fast: bool = False):
    """Train all registered models, optimize hyperparameters, and save metrics."""
    print("Loading datasets...")
    train = pd.read_parquet(DATA_DIR / "processed" / "train.parquet")
    val = pd.read_parquet(DATA_DIR / "processed" / "val.parquet")

    X_train = train.drop(columns=["target"])
    y_train = train["target"]
    X_val = val.drop(columns=["target"])
    y_val = val["target"]

    registry = get_registry(fast=fast)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    results = []

    for name, cfg in registry.items():
        print(f"\n--- Training {name} ---")
        pipeline = build_pipeline(cfg["estimator"], **cfg["pipeline"])

        search = RandomizedSearchCV(
            pipeline,
            param_distributions=cfg["params"],
            n_iter=2 if fast else n_iter,
            scoring="average_precision",
            cv=cv,
            random_state=SEED,
            n_jobs=-1,
            refit=True,
        )

        start_time = time.time()
        search.fit(X_train, y_train)
        fit_time = time.time() - start_time

        best_model = search.best_estimator_
        joblib.dump(best_model, MODELS_DIR / f"{name}_best.joblib")

        scores, is_prob = get_scores(best_model, X_val)
        metrics = evaluate(
            y_true=y_val,
            y_score=scores,
            is_probability=is_prob,
            model_name=name,
            fit_seconds=fit_time,
        )
        results.append(metrics)
        print(f"[{name}] Best cost: {metrics['cost_best']} | PR-AUC: {metrics['pr_auc']:.4f}")

    df_summary = to_table(results)
    summary_path = METRICS_DIR / "benchmark_results.csv"
    df_summary.to_csv(summary_path, index=False)
    print(f"\nBenchmark finished! Results saved to {summary_path}")
    return df_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true", help="Run fast dry-run mode with reduced iterations")
    args = parser.parse_args()
    run_benchmark(fast=args.fast)
