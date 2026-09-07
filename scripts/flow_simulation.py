"""Real-time flow simulation (EF09, reinstated -- see docs/amendment.md for
the history of EF05, its counterpart).

Replays vehicles arriving one at a time at an atelier and scores each one
through the HTTP API (src/api.py), the same boundary a real workshop
terminal or an embedded gateway would call. This is the client-side
counterpart to scripts/latency.py: that script measures the model's raw
compute time in-process, this one measures what a real client experiences
-- network round trip included -- under a stream of arrivals rather than a
tight loop.

IMPORTANT -- this is not a new measurement of model performance. It reuses
rows from the fitting rows, which are not sealed. No cost, detection rate,
or other performance figure computed here should be cited alongside
reports/test_result.json: this script answers "can the deployed system keep
up with arrivals", not "how good is the model". Mixing the two would
attribute a second, informal reading to a file the protocol says was opened
once.

Run:
    uvicorn src.api:app --host 0.0.0.0 --port 8000        # terminal 1
    python scripts/flow_simulation.py                     # terminal 2

    # Under a resource ceiling approximating an embedded target:
    docker run --cpus=0.5 --memory=256m -p 8000:8000 pdm-aps:1.0 \\
        uvicorn src.api:app --host 0.0.0.0 --port 8000
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import requests  # noqa: E402

from src.config import ROOT  # noqa: E402
from src.data import load, train_validation_split  # noqa: E402

WARMUP = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://localhost:8000",
                        help="Base URL of the running API (src/api.py).")
    parser.add_argument("--n", type=int, default=200,
                        help="Number of vehicles to replay.")
    parser.add_argument("--rate", type=float, default=2.0,
                        help="Mean arrival rate, vehicles per second.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Seed for the arrival process, not the model.")
    return parser.parse_args()


def wait_for_api(api_url: str, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            response = requests.get(f"{api_url}/health", timeout=1)
            if response.status_code == 200:
                print(f"API reachable at {api_url}, "
                     f"model: {response.json()['model']}\n")
                return
        except requests.RequestException:
            pass
        time.sleep(0.5)
    raise RuntimeError(
        f"API not reachable at {api_url} after {timeout}s. "
        "Start it with: uvicorn src.api:app --host 0.0.0.0 --port 8000")


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    wait_for_api(args.api_url)

    # The fitting rows are not sealed: they have been used throughout the
    # project. Using them as a source of realistic sensor vectors raises no
    # question at all, where the sealed test file would need a caveat about
    # not being read a second time.
    pool = load("train")
    X_fit, _, _, _ = train_validation_split()
    pool = pool.loc[X_fit.index].drop(columns=["class"])

    sample = pool.sample(n=args.n, replace=False, random_state=args.seed)

    # NaN must become None: the missingness is real and the API/Predictor is
    # meant to handle it (absence is a signal, section 5 of the report), but
    # bare NaN is not valid JSON. `DataFrame.where(..., None)` looks like the
    # fix but is not one: on a float64 column pandas coerces None straight
    # back to NaN to keep the column's dtype, so the replacement has to happen
    # per value, after the frame has already become plain Python dicts.
    vehicles = [
        {k: (None if isinstance(v, float) and np.isnan(v) else v)
         for k, v in row.items()}
        for row in sample.to_dict(orient="records")
    ]

    for row in vehicles[:WARMUP]:
        requests.post(f"{args.api_url}/predict", json={"readings": row},
                     timeout=5)

    # Arrivals are scheduled in advance, from a single origin. Deriving the
    # next arrival from the previous completion would let a slow request push
    # the schedule back, so the queue could never build: the simulation would
    # silently measure per-step lag instead of backlog.
    schedule = np.cumsum(rng.exponential(scale=1.0 / args.rate, size=args.n))
    origin = time.monotonic()

    records = []
    try:
        for index, (row, offset) in enumerate(zip(vehicles, schedule)):
            due = origin + offset
            time.sleep(max(0.0, due - time.monotonic()))

            started = time.monotonic()
            response = requests.post(f"{args.api_url}/predict",
                                     json={"readings": row}, timeout=5)
            finished = time.monotonic()
            response.raise_for_status()
            result = response.json()

            records.append({
                "vehicle": index,
                # Time this vehicle spent waiting because the server was still
                # busy with the previous one. Unlike a per-step lag, this
                # accumulates across vehicles, which is what a growing queue is.
                "queue_ms": max(0.0, (started - due) * 1000),
                "service_ms": (finished - started) * 1000,
                "sojourn_ms": (finished - due) * 1000,
                "probability": result["probability"],
                "flagged": result["flagged"],
            })
    finally:
        # A failure mid-run must not lose the measurements already collected.
        if records:
            pd.DataFrame(records).to_csv(
                ROOT / "reports" / "flow_simulation.csv", index=False)

    frame = pd.DataFrame(records)
    latency = frame["service_ms"].to_numpy()
    waiting = frame["queue_ms"].to_numpy()

    # A queue that builds shows as a positive slope of waiting time against
    # vehicle index. A count of "vehicles that waited" would not distinguish a
    # transient burst from a rate the server cannot sustain.
    slope = float(np.polyfit(frame["vehicle"], waiting, 1)[0])

    print(f"{args.n} vehicles, Poisson arrivals at {args.rate:.1f}/s "
          f"(mean gap {1000 / args.rate:.0f} ms)\n")
    print(f"  service, median          : {np.median(latency):>8.1f} ms")
    print(f"  service, 95th percentile : {np.percentile(latency, 95):>8.1f} ms")
    print(f"  queue wait, median       : {np.median(waiting):>8.1f} ms")
    print(f"  queue wait, maximum      : {waiting.max():>8.1f} ms")
    print(f"  queue growth slope       : {slope:>8.2f} ms per vehicle")

    if slope > 1.0:
        print("\n  the queue grows: this rate is NOT sustainable as-is.")
    else:
        print(f"\n  the queue does not grow: {args.rate:.1f} vehicles per "
              "second is sustainable.")

    out_path = ROOT / "reports" / "flow_simulation.csv"
    if not records:
        print(f"\nno records were collected, {out_path} not written")
    else:
        print(f"\nper-vehicle detail written to {out_path}")
    print("\nreminder: these are operational figures (throughput, latency "
         "under load), not a new reading of model performance -- see the "
         "module docstring.")


if __name__ == "__main__":
    main()
