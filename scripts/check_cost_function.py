"""Verify the cost function before any use.

Seven checks, run from the project root:
    ./.venv/bin/python scripts/check_cost_function.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from src.config import BAYES_THRESHOLD  # noqa: E402
from src.cost import (best_threshold, constant_rule_costs,  # noqa: E402
                      total_cost, unweight, weighted_bayes_threshold)


def main() -> None:
    # The 2016 IDA challenge winner, on the official test set: 542 FP, 9 FN.
    y_test = np.r_[np.ones(375, int), np.zeros(15625, int)]
    y_predicted = np.r_[np.ones(366, int), np.zeros(9, int),
                        np.ones(542, int), np.zeros(15083, int)]
    assert total_cost(y_test, y_predicted) == 9920
    print("1. published 2016 winner :", total_cost(y_test, y_predicted))

    test = constant_rule_costs(y_test)
    assert test["never_flag"] == 187_500
    assert test["always_flag"] == 156_250
    assert test["cheaper"] == "always_flag"
    print("2. never-flag on test    :", test["never_flag"])
    print("3. always-flag on test   :", test["always_flag"])

    # Same two rules on a sample drawn from the training file, whose positive
    # rate is 1.67%: below the break-even rate, so the cheaper rule flips.
    y_validation = np.r_[np.ones(200, int), np.zeros(11_800, int)]
    validation = constant_rule_costs(y_validation)
    assert validation["never_flag"] == 100_000
    assert validation["always_flag"] == 118_000
    assert validation["cheaper"] == "never_flag"
    assert test["above_break_even"] and not validation["above_break_even"]
    print(f"4. cheaper rule flips    : test {test['positive_rate']:.2%} -> "
          f"{test['cheaper']}, validation "
          f"{validation['positive_rate']:.2%} -> {validation['cheaper']}")

    threshold, cost = best_threshold([0, 0, 1, 1], [0.01, 0.02, 0.60, 0.90])
    assert cost == 0 and abs(threshold - 0.60) < 1e-9
    print(f"5. separable case        : threshold {threshold:.2f}, cost {cost}")

    assert abs(weighted_bayes_threshold() - 0.5) < 1e-12
    assert abs(unweight(0.5) - BAYES_THRESHOLD) < 1e-12
    print(f"6. weighted Bayes bound  : {weighted_bayes_threshold():.15f}")

    # The vectorised sweep must never be beaten by the naive loop it replaces.
    rng = np.random.default_rng(0)
    for _ in range(200):
        n = int(rng.integers(50, 400))
        y = (rng.random(n) < 0.02).astype(int)
        p = np.round(rng.random(n), 3)
        _, vectorised = best_threshold(y, p)
        naive = min(total_cost(y, (p >= s).astype(int)) for s in np.unique(p))
        assert vectorised <= naive, (vectorised, naive)
    print("7. vectorised <= naive loop over 200 draws : ok")

    print("\nAll seven checks pass.")


if __name__ == "__main__":
    main()
