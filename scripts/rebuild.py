"""Rebuild experiments.csv from the fold-level measurements.

The summary table drifted from the runs it summarises. Regenerating it makes
that impossible: the file is derived, never typed.

Only the ablation runs feed experiments.csv. Globbing every *_r6.csv also
pulled in finalists_r6.csv, which put the two benchmark models in a table of
feature-engineering variants and, because V1 is the full feature set, listed
the random forest twice under two names.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src.config import ROOT  # noqa: E402

RUNS = ROOT / "reports" / "runs"
SOURCES = {"experiments.csv": "ablation_r*.csv",
           "finalists_summary.csv": "finalists_r*.csv"}


def summarise(paths):
    measurements = pd.concat([pd.read_csv(p) for p in paths],
                             ignore_index=True)
    return measurements.groupby("model").agg(
        cost=("cost", "mean"),
        dispersion=("cost", "std"),
        recall=("recall", "mean"),
        missed_failures=("FN", "mean"),
        false_alarms=("FP", "mean"),
        auc_pr=("auc_pr", "mean"),
        measurements=("cost", "count"),
    ).sort_values("cost")


def main() -> None:
    for output, pattern in SOURCES.items():
        paths = sorted(RUNS.glob(pattern))
        if not paths:
            print(f"[skip] {output}: no {pattern} in {RUNS}")
            continue
        table = summarise(paths)
        table.to_csv(ROOT / "reports" / output)
        print(f"== {output}, from {', '.join(p.name for p in paths)}")
        print(table.round(2).to_string())
        print()


if __name__ == "__main__":
    main()
