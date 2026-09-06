"""The results files must agree with each other.

Six inconsistencies in this project came from documents written against
result files that no longer existed. These tests make the same drift between
two result files impossible.
"""

import json

import pandas as pd
import pytest

from src.config import COST_FN, COST_FP, ROOT

REPORTS = ROOT / "reports"


def read(name):
    path = REPORTS / name
    if not path.exists():
        pytest.skip(f"{name} absent")
    return path


def test_every_benchmark_cost_reconstructs_from_its_error_counts():
    table = pd.read_csv(read("benchmark.csv"), index_col=0)
    for name, row in table.iterrows():
        expected = COST_FP * row["FP"] + COST_FN * row["FN"]
        assert row["cost"] == pytest.approx(expected, abs=1.0), name


def test_every_arbitration_cost_reconstructs():
    table = pd.read_csv(read("arbitration.csv"), index_col=0)
    for name, row in table.iterrows():
        expected = COST_FP * row["FP"] + COST_FN * row["FN"]
        assert row["cost"] == pytest.approx(expected, abs=1.0), name


def test_arbitration_confusion_counts_sum_to_the_reserved_rows():
    table = pd.read_csv(read("arbitration.csv"), index_col=0)
    for name, row in table.iterrows():
        assert row[["TP", "FP", "FN", "TN"]].sum() == 12_000, name
        assert row["TP"] + row["FN"] == 200, name


def test_the_test_result_reconstructs_and_saves_what_it_claims():
    with open(read("test_result.json"), encoding="utf-8") as handle:
        result = json.load(handle)
    assert COST_FP * result["FP"] + COST_FN * result["FN"] == result["cost"]
    assert result["TP"] + result["FN"] == 375
    assert sum(result[k] for k in ("TP", "FP", "FN", "TN")) == 16_000
    assert result["reference"] == 156_250
    saving = 100 * (1 - result["cost"] / result["reference"])
    assert result["saving_pct"] == pytest.approx(saving, abs=0.01)
    assert result["recall"] == pytest.approx(result["TP"] / 375)


def test_the_frozen_threshold_is_not_the_best_possible_on_the_test_set():
    """Reported rather than hidden: the threshold was frozen before the file
    was opened, so a cheaper one exists in hindsight. Quoting that cheaper
    figure as the result would be reporting a tuned threshold."""
    with open(read("test_result.json"), encoding="utf-8") as handle:
        result = json.load(handle)
    assert result["diagnostic_cost_at_that_threshold"] < result["cost"]
    assert result["diagnostic_optimal_threshold"] != result["threshold"]


def test_the_finalists_verdict_matches_its_own_numbers():
    table = pd.read_csv(read("finalists.csv"))
    row = table.iloc[0]
    assert row["measurements"] == 30
    assert bool(row["separable"]) == (abs(row["difference"]) > row["detection_floor"])
    assert bool(row["separable"]) is True


def test_no_paired_comparison_clears_its_detection_floor():
    """The ablation and the factorial plan, at 30 measurements each. All six
    are non-significant, including the ones that would have flattered the
    feature engineering."""
    table = pd.read_csv(read("paired_comparisons.csv"))
    assert len(table) == 6
    assert (table["measurements"] == 30).all()
    for _, row in table.iterrows():
        significant = abs(row["difference"]) > row["detection_floor"]
        assert bool(row["significant"]) == significant, row["comparison"]
    assert not table["significant"].any()


def test_the_overfitting_gap_is_expected_over_the_fold_ratio():
    """12 000 reserved rows against a 9 600-row fold, so the cross-validated
    cost is rescaled by 1.25 before the two are compared."""
    table = pd.read_csv(read("overfitting.csv"), index_col=0)
    for name, row in table.iterrows():
        assert row["expected"] == pytest.approx(row["repeated_cv"] * 1.25), name
        assert row["gap"] == pytest.approx(row["observed"] - row["expected"]), name
        assert row["gap"] < 0, name


def test_calibration_mean_probability_tracks_the_base_rate():
    table = pd.read_csv(read("calibration.csv"), index_col=0)
    assert (table["actual_rate"] == pytest.approx(0.016667, abs=1e-5)).all()
    best = table["brier"].idxmin()
    assert best == "gradient boosting"


def test_single_prediction_latency_satisfies_the_requirement():
    """ENF06, one truck at a time, under one second."""
    single = pd.read_csv(read("latency_single.csv"))
    assert len(single) == 200
    assert single["latency_ms"].max() < 1000


def test_the_missingness_variables_carry_almost_no_permutation_importance():
    """Coherent with the null ablation, and worth asserting because the two
    measurements are independent: if the flags mattered, one of the two would
    have said so."""
    table = pd.read_csv(read("variable_importance.csv"), index_col=0)
    built = [c for c in table.index
             if c.startswith("missing_sb") or c == "depth_g1"]
    assert len(built) == 10
    assert table.loc[built, "0"].abs().max() < 0.001
    assert table["0"].idxmax() == "aa_000"
    assert table.loc["cd_000", "0"] == 0.0
