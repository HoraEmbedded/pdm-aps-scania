"""Missingness as signal (decision D-09).

Every figure here is one printed by scripts/build_dataset.py.
"""

import pytest

pytestmark = pytest.mark.needs_raw

GROUP_1 = ["bk_000", "bl_000", "bm_000", "bn_000", "bo_000", "bp_000",
           "bq_000", "br_000"]


def test_the_three_groups_partition_the_columns(groups, fitting):
    X_fit, _ = fitting
    assert len(groups["group1"]) == 8
    assert len(groups["group2"]) == 56
    assert len(groups["mute"]) == 106
    total = sum(len(groups[k]) for k in ("group1", "group2", "mute"))
    assert total == X_fit.shape[1] == 170


def test_group_1_is_the_eight_emptiest_columns(groups):
    assert sorted(groups["group1"]) == GROUP_1


def test_the_two_groups_have_opposite_signs(groups, fitting):
    """Group 1 is absent mostly among non-APS failures, group 2 mostly among
    APS failures. If absence were a random sensor fault both gaps would sit
    at zero."""
    from src.missingness import per_class_missing_rate
    rates = per_class_missing_rate(*fitting)
    gap = rates["rate_other"] - rates["rate_aps"]
    assert (gap[groups["group1"]] > 0.10).all()
    assert (gap[groups["group2"]] < -0.10).all()
    assert (gap[groups["mute"]].abs() <= 0.10).all()


def test_the_group_1_threshold_falls_inside_a_real_break(fitting):
    """The 0.10 threshold was written down before the computation it selects
    on, which is discipline rather than evidence. On the group 1 side it also
    happens to fall in a gap of more than a factor ten, so its exact value
    changes nothing."""
    from src.missingness import gap_cliff
    cliff = gap_cliff(*fitting)["group1_cliff"]
    assert cliff["last_selected"] == pytest.approx(0.323, abs=0.002)
    assert cliff["next"] == pytest.approx(0.026, abs=0.002)
    assert cliff["factor"] > 10


def test_the_group_2_threshold_has_no_such_break(fitting):
    """Stated because the opposite would be convenient: on this side the
    threshold is a declared choice and nothing more."""
    from src.missingness import gap_cliff
    cliff = gap_cliff(*fitting)["group2_cliff"]
    assert cliff["factor"] < 3


def test_group_1_absence_is_perfectly_nested(groups, fitting):
    """Once a column is absent, every column after it is absent too, which
    forbids the pattern '10'. Nine patterns is what a nested block of eight
    columns produces; the forbidden-pattern test is what proves it."""
    from src.missingness import nesting_report
    X_fit, _ = fitting
    report = nesting_report(X_fit, groups["group1"])
    assert report["n_exceptions"] == 0
    assert report["nested_share"] == 1.0
    assert report["n_patterns"] == report["n_if_nested"] == 9
    assert report["n_possible"] == 256


def test_group_2_absence_is_not_nested(groups, fitting):
    """A negative result, and the reason group 2 gets one flag per sub-block
    instead of a depth: a depth over a non-nested block collapses genuinely
    different patterns onto the same integer."""
    from src.missingness import nesting_report
    X_fit, _ = fitting
    report = nesting_report(X_fit, groups["group2"])
    assert report["n_if_nested"] == 57
    assert report["n_patterns"] == 115
    assert report["n_exceptions"] == 3860
    assert report["nested_share"] == pytest.approx(0.9196, abs=5e-4)


def test_group_2_splits_into_nine_sub_blocks(encoder):
    assert len(encoder.sub_blocks_) == 9
    assert len(encoder.flag_names_) == 9
    assert sum(len(m) for m in encoder.sub_blocks_.values()) == 56


def test_reading_one_column_per_sub_block_is_licensed_by_agreement(encoder, fitting):
    """The flag reads a single representative column. That shortcut is only
    legitimate if the block moves as one, so the agreement is measured."""
    from src.missingness import sub_block_homogeneity
    X_fit, _ = fitting
    table = sub_block_homogeneity(X_fit, encoder.sub_blocks_)
    assert (table["agreement"] > 0.995).all()
    biggest = table.sort_values("n_columns").iloc[-1]
    assert biggest["n_columns"] == 20
    assert biggest["agreement"] > 0.9998


def test_the_representative_is_chosen_by_name_not_by_arrival_order(encoder):
    for representative, (_, members) in zip(
            encoder.representatives_, sorted(encoder.sub_blocks_.items())):
        assert representative == sorted(members)[0]


def test_the_encoder_adds_exactly_ten_columns(encoder, fitting):
    X_fit, _ = fitting
    encoded = encoder.transform(X_fit)
    assert encoded.shape == (48_000, 180)
    added = [c for c in encoded.columns if c not in X_fit.columns]
    assert added == ["depth_g1"] + encoder.flag_names_


def test_the_depth_variable_is_ordinal_zero_to_eight(encoder, fitting):
    X_fit, _ = fitting
    depth = encoder.transform(X_fit)["depth_g1"]
    assert depth.min() == 0
    assert depth.max() == 8
    assert depth.dtype.kind == "i"


def test_depth_reads_as_a_usage_level(groups, fitting):
    """At full depth the median of the single complete column collapses by
    more than two orders of magnitude, at constant class. This is what
    justifies imputing group 1 with zero rather than a median (D-10)."""
    import pandas as pd
    from src.missingness import depth
    X_fit, y_fit = fitting
    table = pd.DataFrame({"depth": depth(X_fit, groups["group1"]),
                          "aa_000": X_fit["aa_000"],
                          "aps": y_fit.values})
    medians = table[table["aps"] == 0].groupby("depth")["aa_000"].median()
    assert medians.max() / max(medians.min(), 1) > 300


def test_detection_uses_the_fitting_split_only(split):
    """It once ran on all 60 000 rows, so before the split. The lists it
    produces are the same either way, which is an argument for robustness and
    not a licence to go back."""
    import pandas as pd
    from src.missingness import detect_groups
    X_fit, X_val, y_fit, y_val = split
    on_fitting = detect_groups(X_fit, y_fit)
    on_everything = detect_groups(pd.concat([X_fit, X_val]),
                                  pd.concat([y_fit, y_val]))
    assert on_fitting["group1"] == on_everything["group1"]
    assert set(on_fitting["group2"]) == set(on_everything["group2"])


def test_duplicate_absence_columns_are_reported(fitting):
    """Columns whose absence indicators correlate at exactly 1.00 carry the
    same missingness twice. Harmless when fitting, misleading when reading a
    feature importance, which will split arbitrarily between them."""
    from src.missingness import duplicate_absence_columns
    X_fit, _ = fitting
    pairs = duplicate_absence_columns(X_fit)
    assert ("ab_000", "cr_000") in pairs
    assert len(pairs) > 50
