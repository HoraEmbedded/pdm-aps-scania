"""Full classical ML benchmark (EF03, EF05, EF06)."""

import argparse
import json
import sys
import warnings
from pathlib import Path

# Silence runtime warnings from NaN slices in histograms
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd

from src.config import MODELS_DIR, REPORTS_DIR
from src.data.split import get_train_val
from src.evaluation.report import evaluate, get_scores, to_table
from src.models.registry import get_registry
from src.models.search import run_search
from src.utils.seeds import set_seed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true", help="reduced search, for a first dry run")
    parser.add_argument("--n-iter", type=int, default=20)
    parser.add_argument("--only", type=str, default=None, help="run a single model by name")
    args = parser.parse_args()

    set_seed()
    X_fit, X_val, y_fit, y_val = get_train_val()
    print(f"Apprentissage {X_fit.shape} | Validation {X_val.shape}")
    print(f"Positifs : {int(y_fit.sum())} en apprentissage, {int(y_val.sum())} en validation\n")

    registry = get_registry(fast=args.fast)
    if args.only:
        registry = {args.only: registry[args.only]}

    n_iter = 2 if args.fast else args.n_iter
    results, cv_frames = [], []

    for name, spec in registry.items():
        print("=" * 70)
        print(f"MODELE : {name}")
        print("=" * 70)

        search, elapsed = run_search(name, spec, X_fit, y_fit, n_iter=n_iter)

        y_score, is_proba = get_scores(search.best_estimator_, X_val)
        metrics = evaluate(y_val, y_score, is_probability=is_proba, model_name=name, fit_seconds=elapsed)
        metrics["best_params"] = json.dumps({k: str(v) for k, v in search.best_params_.items()})
        metrics["cv_pr_auc"] = round(search.best_score_, 4)
        results.append(metrics)

        print(f"  Cout sur validation : {metrics['cost_best']} (naif {metrics['naive_cost']}, ratio {metrics['cost_ratio']})")
        print(f"  Rappel {metrics['recall']:.3f} | Precision {metrics['precision']:.3f} | Pannes ratees {metrics['fn']}\n")

        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(search.best_estimator_, MODELS_DIR / f"{name}.joblib")

        trace = pd.DataFrame(search.cv_results_)
        trace["model"] = name
        cv_frames.append(trace)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    table = to_table(results)
    table.to_csv(REPORTS_DIR / "benchmark_ml.csv", index=False)
    pd.concat(cv_frames).to_csv(REPORTS_DIR / "cv_results_ml.csv", index=False)

    columns = ["model", "cv_pr_auc", "pr_auc", "roc_auc", "recall", "precision", "fn", "fp", "cost_best", "cost_ratio", "threshold_best", "fit_seconds"]
    print("\n" + "=" * 70)
    print("BENCHMARK ML CLASSIQUE, jeu de validation")
    print("=" * 70)
    print(table[columns].to_string(index=False))
    print(f"\nEcrit dans {REPORTS_DIR / 'benchmark_ml.csv'}")


if __name__ == "__main__":
    main()
