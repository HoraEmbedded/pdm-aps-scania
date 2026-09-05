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
    """V0 drops heavily incomplete columns.
    V1 is the retained decision (depth + counters).
    V1_no_depth and V1_no_flags are ablations for the factorial design.
    V1_raw lacks both.
    V2 keeps one flag per informative column."""
    X = X_raw.copy()

    if name == "V0":
        X = X.drop(columns=X.columns[X.isna().mean() > 0.10].tolist())
        group1, unscaled = [], []
    elif name.startswith("V1"):
        X = extractor.transform(X)
        group1 = extractor.group1_
        unscaled = ["depth_g1"] + extractor.flag_names_

        if "no_depth" in name or name == "V1_raw":
            X = X.drop(columns=["depth_g1"])
            if "depth_g1" in unscaled:
                unscaled.remove("depth_g1")
        if "no_flags" in name or name == "V1_raw":
            X = X.drop(columns=extractor.flag_names_)
            for f in extractor.flag_names_:
                if f in unscaled:
                    unscaled.remove(f)
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

    # Définition des 6 variantes nécessaires
    
    # The plan crosses two constructed variables, the depth and the sub-block flags.
    # Column aa_000 is present in all four conditions: this plan therefore says
    # nothing about redundancy between the depth and the usage counter.
    
    variants = ["V0", "V1", "V2", "V1_no_depth", "V1_no_flags", "V1_raw"]
    runs = {}

    for name in variants:
        X = build_variant(name, X_raw, y_fit, extractor)
        print(f"{name}: {X.shape}, running {args.repeats} repeats")
        runs[name] = evaluate_repeated(lambda: random_forest(300), X, y_fit,
                                       name=name, n_repeats=args.repeats)
        print(f"   cost {runs[name]['cost'].mean():,.0f} "
              f"over {len(runs[name])} measurements")

    save_results(runs, f"ablation_r{args.repeats}")

    # Définition des 6 comparaisons appariées
    comparisons_def = [
        ("V1 vs V0", "V0", "V1"),
        ("V2 vs V1", "V1", "V2"),
        ("V2 vs V0", "V0", "V2"),
        ("depth, flags present", "V1_no_depth", "V1"),
        ("depth, flags absent", "V1_raw", "V1_no_flags"),
        ("flags alone", "V1_raw", "V1_no_depth"),
    ]

    results = []
    print("\n--- Résultats des comparaisons appariées ---")
    for label, model_a, model_b in comparisons_def:
        diff = runs[model_a]["cost"].values - runs[model_b]["cost"].values
        n = len(diff)
        error = diff.std(ddof=1) / np.sqrt(n)
        critical = stats.t.ppf(0.975, df=n - 1)
        is_significant = abs(diff.mean()) > critical * error

        print(f"\n{label} ({model_a} minus {model_b})")
        print(f"  measurements     : {n}")
        print(f"  mean difference  : {diff.mean():+,.0f}")
        print(f"  standard error   : {error:,.0f}")
        print(f"  detection floor  : {critical * error:,.0f}")
        print(f"  significant      : {'yes' if is_significant else 'no'}")

        results.append({
            "comparison": label, "measurements": n,
            "difference": round(diff.mean()), "standard_error": round(error),
            "detection_floor": round(critical * error),
            "significant": is_significant,
        })

    # Sauvegarde des 6 comparaisons dans le fichier CSV final
    pd.DataFrame(results).to_csv(ROOT / "reports" / "paired_comparisons.csv", index=False)


if __name__ == "__main__":
    main()
