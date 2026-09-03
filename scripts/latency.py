"""Measure single-prediction latency (ENF06).

Batch throughput is irrelevant here: the requirement concerns one truck at a
time, which is how the demonstrator is used.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.config import ROOT  # noqa: E402
from src.data import load_sealed_test  # noqa: E402
from src.inference import Predictor  # noqa: E402

WARMUP = 10
RUNS = 200
BATCHES = [1, 10, 100, 1000]


def main() -> None:
    X, _ = load_sealed_test()
    predictor = Predictor.load()

    # First calls include lazy imports and memory allocation, and can take a
    # hundred times longer than the rest. Omitting the warm-up would suggest
    # the requirement is at risk when it is not.
    for _ in range(WARMUP):
        predictor.predict_proba(X.iloc[[0]])

    timings = []
    for index in range(RUNS):
        row = X.iloc[[index % len(X)]]
        start = time.perf_counter()
        predictor.predict_proba(row)
        timings.append((time.perf_counter() - start) * 1000)

    timings = np.array(timings)
    print(f"single prediction, {RUNS} calls after {WARMUP} warm-up calls\n")
    print(f"  mean            : {timings.mean():>8.2f} ms")
    print(f"  median          : {np.median(timings):>8.2f} ms")
    print(f"  95th percentile : {np.percentile(timings, 95):>8.2f} ms")
    print(f"  maximum         : {timings.max():>8.2f} ms")
    print(f"\nENF06, under 1000 ms : "
          f"{'satisfied' if timings.max() < 1000 else 'NOT satisfied'}")

    print("\nthroughput by batch size\n")
    print(f"{'rows':>6} {'total ms':>10} {'ms per row':>12}")
    print("-" * 30)
    rows = []
    for size in BATCHES:
        batch = X.head(size)
        predictor.predict_proba(batch)
        start = time.perf_counter()
        predictor.predict_proba(batch)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"{size:>6} {elapsed:>10.1f} {elapsed / size:>12.3f}")
        rows.append({"rows": size, "total_ms": elapsed,
                     "ms_per_row": elapsed / size})

    pd.DataFrame(rows).to_csv(ROOT / "reports" / "latency.csv", index=False)
    pd.DataFrame({"latency_ms": timings}).to_csv(
        ROOT / "reports" / "latency_single.csv", index=False)


if __name__ == "__main__":
    main()
