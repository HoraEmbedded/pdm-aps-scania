"""Reliability curves for the five models, on out-of-fold probabilities.

The reserved rows must stay untouched and a model's own training predictions
are optimistic, so the probabilities come from cross_val_predict on the
fitting set. Same mechanism as the threshold, same reason.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.calibration import calibration_curve  # noqa: E402
from sklearn.metrics import brier_score_loss  # noqa: E402
from sklearn.model_selection import StratifiedKFold, cross_val_predict  # noqa: E402

from src.config import (BAYES_THRESHOLD, FIGURES_DIR, N_FOLDS,  # noqa: E402
                        PROCESSED_DIR, ROOT, SEED)
from src.cost import best_threshold, unweight  # noqa: E402
from src.models import (KerasPerceptron, gradient_boosting,  # noqa: E402
                        linear_svm, logistic_regression, random_forest)
from src.seeding import set_seed  # noqa: E402

FACTORIES = {
    "gradient boosting": (lambda: gradient_boosting(8, 0.10, 300), -1),
    "random forest": (lambda: random_forest(300), -1),
    "perceptron": (lambda: KerasPerceptron(units=(64, 32), epochs=20), 1),
    "linear svm": (lambda: linear_svm(0.001), -1),
    "logistic regression": (lambda: logistic_regression(0.001), -1),
}


def main() -> None:
    set_seed()
    X = pd.read_csv(PROCESSED_DIR / "X_fit.csv", index_col=0)
    y = pd.read_csv(PROCESSED_DIR / "y_fit.csv", index_col=0).squeeze().to_numpy()

    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    rows, curves = [], {}

    for name, (factory, n_jobs) in FACTORIES.items():
        probability = cross_val_predict(factory(), X, y, cv=cv,
                                        method="predict_proba",
                                        n_jobs=n_jobs)[:, 1]
        # Equal-sized bins: uniform bins would leave almost all of them empty
        # on a problem with under 2% positives.
        fraction, mean_predicted = calibration_curve(y, probability, n_bins=12,
                                                     strategy="quantile")
        curves[name] = (mean_predicted, fraction)

        threshold, _ = best_threshold(y, probability)
        rows.append({
            "model": name,
            "brier": brier_score_loss(y, probability),
            "mean_probability": probability.mean(),
            "actual_rate": y.mean(),
            "threshold": threshold,
            "unweighted_threshold": float(unweight(threshold)),
            "ratio_to_bayes": float(BAYES_THRESHOLD / max(unweight(threshold), 1e-12)),
        })
        print(f"{name:<22} brier {rows[-1]['brier']:.5f}   "
              f"unweighted threshold {rows[-1]['unweighted_threshold']:.5f}")

    table = pd.DataFrame(rows).set_index("model").round(6)
    table.to_csv(ROOT / "reports" / "calibration.csv")
    print("\n" + table.to_string())

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    colours = plt.cm.tab10(np.linspace(0, 1, 10))

    for i, (name, (predicted, observed)) in enumerate(curves.items()):
        axes[0].plot(predicted, observed, "o-", color=colours[i], label=name,
                     lw=1.6, markersize=4)
    axes[0].plot([1e-4, 1], [1e-4, 1], "k--", lw=1, label="perfect calibration")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("mean predicted probability")
    axes[0].set_ylabel("observed failure rate")
    axes[0].set_title("Reliability curves, out-of-fold probabilities")
    axes[0].legend(fontsize=7)
    axes[0].grid(alpha=0.25)

    axes[1].bar(range(len(table)), table["ratio_to_bayes"],
                color=[colours[i] for i in range(len(table))])
    axes[1].axhline(1.0, color="black", ls="--", lw=1,
                    label="perfectly calibrated")
    axes[1].set_yscale("log")
    axes[1].set_xticks(range(len(table)))
    axes[1].set_xticklabels(table.index, rotation=30, ha="right", fontsize=7)
    axes[1].set_ylabel("Bayes threshold divided by measured threshold")
    axes[1].set_title("Distance to the theoretical operating point")
    axes[1].legend(fontsize=7)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "02_calibration.png", dpi=150)
    print(f"\nfigure written to {FIGURES_DIR / '02_calibration.png'}")


if __name__ == "__main__":
    main()
