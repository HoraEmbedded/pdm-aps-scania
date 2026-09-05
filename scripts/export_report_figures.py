"""Export every figure the report cites, as files under reports/.

The report must not quote a number typed by hand. build_dataset.py prints
these on the console and they are lost when it closes; the report needs them
as files it can be checked against.

Run: ./.venv/bin/python scripts/export_report_figures.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src.config import PROCESSED_DIR, ROOT  # noqa: E402
from src.data import train_validation_split  # noqa: E402
from src.missingness import (MissingnessEncoder, depth,  # noqa: E402
                             detect_groups, duplicate_absence_columns,
                             gap_cliff, nesting_report, sub_block_homogeneity)
from src.seeding import set_seed  # noqa: E402

OUT = ROOT / "reports" / "report_figures"
HISTOGRAM_PREFIXES = {"ag", "ay", "az", "ba", "cn", "cs", "ee"}
EXPECTED_CHECKSUM = 313_696.0


def main() -> None:
    set_seed()
    OUT.mkdir(parents=True, exist_ok=True)

    X_fit, _, y_fit, _ = train_validation_split()
    groups = detect_groups(X_fit, y_fit)
    encoder = MissingnessEncoder().fit(X_fit, y_fit)

    cliff = gap_cliff(X_fit, y_fit)
    pd.DataFrame({k: cliff[k] for k in ("group1_cliff", "group2_cliff")
                  if cliff[k]}).T.to_csv(OUT / "gap_cliff.csv")

    sub_block_homogeneity(X_fit, encoder.sub_blocks_).to_csv(
        OUT / "sub_blocks.csv", index=False)

    nesting = []
    for name in ("group1", "group2"):
        report = nesting_report(X_fit, groups[name])
        nesting.append({"group": name,
                        **{k: v for k, v in report.items()
                           if k not in ("counts", "exceptions")}})
    pd.DataFrame(nesting).to_csv(OUT / "nesting.csv", index=False)

    # The usage table behind the factor 329. Read among non-APS failures only,
    # so the relation is not a reflection of the label.
    levels = depth(X_fit, groups["group1"])
    other = y_fit == 0
    usage = pd.DataFrame({
        "median_aa_000": X_fit.loc[other, "aa_000"].groupby(levels[other]).median(),
        "rows": levels[other].value_counts().sort_index(),
    })
    usage.index.name = "depth"
    usage.to_csv(OUT / "depth_vs_usage.csv")

    is_histogram = [c.split("_")[0] in HISTOGRAM_PREFIXES for c in X_fit.columns]
    rate = X_fit.isna().mean()
    pd.DataFrame([
        {"family": "histogram columns", "columns": sum(is_histogram),
         "mean_missing": rate[is_histogram].mean()},
        {"family": "isolated counters", "columns": len(rate) - sum(is_histogram),
         "mean_missing": rate[[not h for h in is_histogram]].mean()},
    ]).to_csv(OUT / "missingness_by_family.csv", index=False)

    pairs = duplicate_absence_columns(X_fit)
    pd.DataFrame(pairs, columns=["left", "right"]).to_csv(
        OUT / "duplicate_absence_pairs.csv", index=False)

    X = pd.read_csv(PROCESSED_DIR / "X_fit.csv", index_col=0)
    built = ["depth_g1"] + encoder.flag_names_
    odd = [c for c in X.columns
           if c not in built and len(c.split("_")[-1]) != 3]

    summary = {
        "checksum": round(float(X.values.sum()), 2),
        "shape": list(X.shape),
        "group1": len(groups["group1"]),
        "group2": len(groups["group2"]),
        "mute": len(groups["mute"]),
        "sub_blocks": len(encoder.sub_blocks_),
        "usage_factor": round(float(usage["median_aa_000"].max()
                                    / max(usage["median_aa_000"].min(), 1))),
        "duplicate_absence_pairs": len(pairs),
        "naming_anomalies": odd,
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nseven files written to {OUT.relative_to(ROOT)}")

    if abs(summary["checksum"] - EXPECTED_CHECKSUM) > 1.0:
        print(f"\nSTOP: checksum {summary['checksum']:,.2f} is not "
              f"{EXPECTED_CHECKSUM:,.2f}. The preparation chain has moved, so "
              f"every result has to be recomputed before anything is written.")
        sys.exit(1)


if __name__ == "__main__":
    main()
