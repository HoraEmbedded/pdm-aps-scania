"""Rebuild experiments.csv from the fold-level measurements.

The summary table drifted from the runs it summarises. Regenerating it from
runs/ makes that impossible: the file is derived, never typed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src.config import ROOT  # noqa: E402

RUNS = ROOT / "reports" / "runs"


def main() -> None:
    frames = [pd.read_csv(path) for path in sorted(RUNS.glob("*_r6.csv"))]
    measurements = pd.concat(frames, ignore_index=True)

    summary = measurements.groupby("model").agg(
        cost=("cost", "mean"),
        dispersion=("cost", "std"),
        recall=("recall", "mean"),
        missed_failures=("FN", "mean"),
        false_alarms=("FP", "mean"),
        auc_pr=("auc_pr", "mean"),
        measurements=("cost", "count"),
    ).sort_values("cost")

    summary.to_csv(ROOT / "reports" / "experiments.csv")
    print(summary.round(2).to_string())


if __name__ == "__main__":
    main()


