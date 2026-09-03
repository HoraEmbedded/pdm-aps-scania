"""Rank the two leading models on repeated cross-validation.

The 138-unit gap between them was measured on a single partition, which the
repeated ablation later showed to favour the random forest by 357 units. A gap
that small has to rest on more than five measurements before it designates a
finalist.

Run: ./.venv/bin/python scripts/finalists.py --repeats 6
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from src.config import PROCESSED_DIR, ROOT  # noqa: E402
from src.evaluation import evaluate_repeated, save_results  # noqa: E402
from src.models import gradient_boosting, random_forest  # noqa: E402
from src.seeding import set_seed  # noqa: E402

CANDIDATES = {
    "gradient boosting": lambda: gradient_boosting(8, 0.10, 300),
    "random forest": lambda: random_forest(300),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=6)
    args = parser.parse_args()

    set_seed()
    X = pd.read_csv(PROCESSED_DIR / "X_fit.csv", index_col=0)
    y = pd.read_csv(PROCESSED_DIR / "y_fit.csv", index_col=0).squeeze().to_numpy()

    runs = {}
    for name, factory in CANDIDATES.items():
        runs[name] = evaluate_repeated(factory, X, y, name=name,
                                       n_repeats=args.repeats)
        result = runs[name]
        print(f"{name:<20} cost {result['cost'].mean():>8,.0f} "
              f"+/- {result['cost'].std():>6,.0f}   "
              f"recall {result['recall'].mean():.1%}   "
              f"missed {result['FN'].mean():.1f}   "
              f"over {len(result)} measurements")

    save_results(runs, f"finalists_r{args.repeats}")

    left, right = list(CANDIDATES)
    difference = runs[left]["cost"].values - runs[right]["cost"].values
    n = len(difference)
    error = difference.std(ddof=1) / np.sqrt(n)
    critical = stats.t.ppf(0.975, df=n - 1)

    print(f"\n{left} minus {right}")
    print(f"  measurements    : {n}")
    print(f"  mean difference : {difference.mean():+,.0f}")
    print(f"  standard error  : {error:,.0f}")
    print(f"  detection floor : {critical * error:,.0f}")
    print(f"  separable       : "
          f"{'yes' if abs(difference.mean()) > critical * error else 'no'}")

    pd.DataFrame([{
        "left": left, "right": right, "measurements": n,
        "difference": round(difference.mean()),
        "standard_error": round(error),
        "detection_floor": round(critical * error),
        "separable": abs(difference.mean()) > critical * error,
    }]).to_csv(ROOT / "reports" / "finalists.csv", index=False)


if __name__ == "__main__":
    main()
