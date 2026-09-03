"""Recompute the paired comparisons, and record how many measurements
each one rests on.

The standard error of a paired difference falls as the square root of the
number of measurements, so the number of repeats is not a detail: it decides
whether an effect of a few hundred units is detectable at all.

Run: ./.venv/bin/python scripts/paired_comparisons.py --repeats 6
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from src.config import PROCESSED_DIR, ROOT, SEED  # noqa: E402
from src.evaluation import evaluate_repeated, save_results  # noqa: E402
from src.missingness import MissingnessEncoder  # noqa: E402
from src.data import train_validation_split  # noqa: E402
from src.models import random_forest  # noqa: E402
from src.preprocessing import Preprocessor  # noqa: E402
from src.seeding import set_seed  # noqa: E402


def build_variant(name, X_raw, y, extractor):
    """V0 drops heavily incomplete columns and builds nothing.
    V1 is the retained decision. V2 keeps one flag per informative column."""
    X = X_raw.copy()

    if name == "V0":
        X = X.drop(columns=X.columns[X.isna().mean() > 0.10].tolist())
        group1, unscaled = [], []
    elif name == "V1":
        X = extractor.transform(X)
        group1 = extractor.group1_
        unscaled = ["depth_g1"] + extractor.flag_names_
    elif name == "V2":
        informative = extractor.group1_ + extractor.group2_
        for column in informative:
            X[f"missing_{column}"] = X[column].isna().astype(int)
        group1 = extractor.group1_
        unscaled = [f"missing_{c}" for c in informative]
    else:
        raise ValueError(name)

    return Preprocessor(group1=group1, unscaled=unscaled).fit_transform(X)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=6)
    args = parser.parse_args()

    set_seed()
    X_raw, _, y_fit, _ = train_validation_split()
    extractor = MissingnessEncoder().fit(X_raw, y_fit)

    runs = {}
    for name in ["V0", "V1"]:
        X = build_variant(name, X_raw, y_fit, extractor)
        print(f"{name}: {X.shape}, running {args.repeats} repeats")
        runs[name] = evaluate_repeated(lambda: random_forest(300), X, y_fit,
                                       name=name, n_repeats=args.repeats)
        print(f"   cost {runs[name]['cost'].mean():,.0f} "
              f"over {len(runs[name])} measurements")

    save_results(runs, f"ablation_r{args.repeats}")

    difference = runs["V1"]["cost"].values - runs["V0"]["cost"].values
    n = len(difference)
    error = difference.std(ddof=1) / np.sqrt(n)
    critical = stats.t.ppf(0.975, df=n - 1)

    print("\nV1 minus V0")
    print(f"  measurements     : {n}")
    print(f"  mean difference  : {difference.mean():+,.0f}")
    print(f"  standard error   : {error:,.0f}")
    print(f"  detection floor  : {critical * error:,.0f}")
    print(f"  significant      : "
          f"{'yes' if abs(difference.mean()) > critical * error else 'no'}")

    pd.DataFrame([{
        "comparison": "V1 vs V0", "measurements": n,
        "difference": round(difference.mean()), "standard_error": round(error),
        "detection_floor": round(critical * error),
        "significant": abs(difference.mean()) > critical * error,
    }]).to_csv(ROOT / "reports" / "paired_comparisons.csv", index=False)


if __name__ == "__main__":
    main()
