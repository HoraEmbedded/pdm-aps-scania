"""The cost function. No data needed, so this module always runs.

These are the seven checks of scripts/check_cost_function.py, one assertion
per test so a failure names itself.
"""

import numpy as np
import pytest

from src.config import BAYES_THRESHOLD, COST_FN, COST_FP
from src.cost import (best_threshold, constant_rule_costs, total_cost,
                      unweight, weighted_bayes_threshold)

N_TEST, N_TEST_POSITIVE = 16_000, 375


def test_missed_failure_costs_500():
    assert total_cost([1, 0], [0, 0]) == COST_FN == 500


def test_false_alarm_costs_10():
    assert total_cost([0, 0], [1, 0]) == COST_FP == 10


def test_published_2016_winner_reconstructs():
    """542 false alarms and 9 missed failures must give the published 9 920.

    This is what makes every cost in this repository comparable to the
    literature rather than merely internally consistent.
    """
    y_true = np.r_[np.ones(N_TEST_POSITIVE, int),
                   np.zeros(N_TEST - N_TEST_POSITIVE, int)]
    predicted = np.r_[np.ones(366, int), np.zeros(9, int),
                      np.ones(542, int), np.zeros(15_083, int)]
    assert total_cost(y_true, predicted) == 9920


def test_constant_rules_on_the_official_test_set():
    y = np.r_[np.ones(375, int), np.zeros(15_625, int)]
    rules = constant_rule_costs(y)
    assert rules["never_flag"] == 187_500
    assert rules["always_flag"] == 156_250
    assert rules["cheaper"] == "always_flag"
    assert rules["reference"] == 156_250


def test_the_cheaper_constant_rule_flips_between_the_two_files():
    """Above 1.96% positives, flagging everything wins; below, flagging
    nothing does. The test file sits above and the split below, so the
    reference to beat is not a property of the problem."""
    test = constant_rule_costs(np.r_[np.ones(375, int), np.zeros(15_625, int)])
    validation = constant_rule_costs(np.r_[np.ones(200, int),
                                           np.zeros(11_800, int)])
    assert test["above_break_even"] and not validation["above_break_even"]
    assert test["cheaper"] == "always_flag"
    assert validation["cheaper"] == "never_flag"
    assert validation["never_flag"] == 100_000
    assert validation["always_flag"] == 118_000


def test_bayes_threshold_is_ten_over_five_hundred_and_ten():
    assert BAYES_THRESHOLD == pytest.approx(COST_FP / (COST_FP + COST_FN))
    assert BAYES_THRESHOLD == pytest.approx(0.0196078431372549)


def test_weighted_bayes_threshold_is_exactly_one_half():
    """Weighting at 50:1 maps the 1.96% operating point onto 0.5. Comparing a
    weighted threshold to BAYES_THRESHOLD directly would apply the cost ratio
    a second time (decision D-11)."""
    assert weighted_bayes_threshold() == pytest.approx(0.5, abs=1e-12)
    assert unweight(0.5) == pytest.approx(BAYES_THRESHOLD, abs=1e-12)


def test_unweight_inverts_the_weighting_over_the_whole_range():
    from src.config import COST_RATIO
    p = np.linspace(1e-6, 1 - 1e-6, 500)
    weighted = COST_RATIO * p / (1 + (COST_RATIO - 1) * p)
    assert unweight(weighted) == pytest.approx(p, rel=1e-9)


def test_separable_case_finds_the_zero_cost_threshold():
    threshold, cost = best_threshold([0, 0, 1, 1], [0.01, 0.02, 0.60, 0.90])
    assert cost == 0
    assert threshold == pytest.approx(0.60)


def test_degenerate_case_prefers_flagging_nothing():
    """A constant classifier offers no useful cut point. Flagging nothing is
    never an observed threshold, but it is sometimes the cheapest decision,
    and the loop this sweep replaced could not reach it."""
    y = np.r_[np.ones(2, int), np.zeros(2000, int)]
    p = np.full(len(y), 0.5)
    _, cost = best_threshold(y, p)
    assert cost == COST_FN * 2


def test_ties_are_cut_as_one_block():
    """Rows sharing a probability are flagged together, so only the last
    occurrence of a value is a valid cut point."""
    y = np.array([1, 0, 0, 0])
    p = np.array([0.5, 0.5, 0.1, 0.1])
    threshold, cost = best_threshold(y, p)
    predicted = (p >= threshold).astype(int)
    assert total_cost(y, predicted) == cost


@pytest.mark.parametrize("seed", range(20))
def test_vectorised_sweep_never_loses_to_the_naive_loop(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(50, 400))
    y = (rng.random(n) < 0.02).astype(int)
    p = np.round(rng.random(n), 3)
    _, vectorised = best_threshold(y, p)
    naive = min(total_cost(y, (p >= s).astype(int)) for s in np.unique(p))
    assert vectorised <= naive
