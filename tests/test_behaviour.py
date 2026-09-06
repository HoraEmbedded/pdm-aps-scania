"""Behaviour tests on synthetic structures. No file from data/ is read.

The other modules assert against the real dataset and skip when it is absent,
which is right for a local check and wrong for continuous integration: a
skipped test is a green build that verified nothing. This module runs
everywhere, and it encodes the three defects the project's own difficulty log
calls "the defect that raises no error".

Each test names the entry it guards.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from src.config import COST_FN, COST_FP
from src.cost import best_threshold, total_cost
from src.evaluation import evaluate
from src.missingness import depth, detect_groups, nesting_report
from src.preprocessing import Preprocessor


# --------------------------------------------------------------- fixtures
@pytest.fixture
def nested_block():
    """Eight columns whose absence is perfectly nested, as group 1 is.

    Depth d means the last d columns are absent. The columns are returned in a
    scrambled order on purpose: nesting is a property of the block read by
    ascending absence rate, so anything that tests it has to sort first.
    """
    rows = []
    for level in [0, 0, 0, 1, 2, 3, 5, 8, 8, 8]:
        rows.append([1.0] * (8 - level) + [np.nan] * level)
    frame = pd.DataFrame(rows, columns=[f"c{i}" for i in range(8)])
    return frame[["c3", "c0", "c7", "c1", "c5", "c2", "c6", "c4"]]


@pytest.fixture
def informative_missingness():
    """Two columns whose absence depends on the class, two that do not."""
    rng = np.random.default_rng(0)
    n = 400
    y = pd.Series([1] * 40 + [0] * (n - 40))
    frame = pd.DataFrame({
        "informative_pos": [1.0] * 40 + [np.nan] * 360,
        "informative_neg": [np.nan] * 40 + [1.0] * 360,
        "mute": np.where(rng.random(n) < 0.3, np.nan, 1.0),
        "complete": rng.random(n) * 1000,
    })
    return frame, y


@pytest.fixture
def imbalanced():
    rng = np.random.default_rng(3)
    n = 1200
    y = (rng.random(n) < 0.05).astype(int)
    X = pd.DataFrame({"signal": y * 2 + rng.normal(0, 1, n),
                      "noise": rng.normal(0, 1, n)})
    return X, y


@pytest.fixture
def two_parts():
    """Two parts with deliberately different distributions, so that a leak
    shows up as statistics that are too good on the held-out part."""
    rng = np.random.default_rng(2)
    fit = pd.DataFrame({
        "a": rng.normal(100, 10, 500),
        "b": np.where(rng.random(500) < 0.4, np.nan, rng.normal(50, 5, 500)),
    })
    held = pd.DataFrame({
        "a": rng.normal(300, 30, 200),
        "b": np.where(rng.random(200) < 0.4, np.nan, rng.normal(200, 20, 200)),
    })
    return fit, held


# ------------------------------------------------- M-08, the silent leak
def test_the_threshold_is_not_tuned_on_memorised_rows(imbalanced):
    """Guards difficulty M-08, the defect that cost a factor of 5.9.

    A one-nearest-neighbour classifier reproduces its own training rows
    exactly. A threshold tuned on its in-sample probabilities would be chosen
    against a perfect separation that does not exist out of sample, and would
    land near 0.5 with nothing to correct. Tuned out of fold, it has to come
    down to where the rare class actually sits.

    The original defect produced no error at all: the tables still looked
    plausible.
    """
    result = evaluate(lambda: KNeighborsClassifier(n_neighbors=1),
                      imbalanced[0], imbalanced[1], name="memoriser")
    assert result["threshold"].mean() < 0.4


def test_the_leaky_path_is_still_reachable_and_still_worse(imbalanced):
    """The comparison between the two paths is a reported result, so the
    faulty one has to stay callable. It must remain the more expensive."""
    X, y = imbalanced

    def factory():
        return DecisionTreeClassifier(max_depth=None, random_state=0)

    leaky = evaluate(factory, X, y, name="leaky",
                     out_of_sample_threshold=False)
    clean = evaluate(factory, X, y, name="clean")
    assert leaky["cost"].mean() >= clean["cost"].mean()


def test_the_folds_are_reproducible(imbalanced):
    X, y = imbalanced

    def factory():
        return DecisionTreeClassifier(max_depth=3, random_state=0)

    first = evaluate(factory, X, y, name="tree")
    second = evaluate(factory, X, y, name="tree")
    assert first["cost"].tolist() == second["cost"].tolist()


# ------------------------------------------- M-06, nesting without sorting
def test_nesting_holds_when_the_block_is_read_in_the_right_order(nested_block):
    """Guards difficulty M-06. Sorted by ascending absence rate, the block is
    nested; read in the order the columns happen to arrive in, it is not.

    nesting_report does not sort: it tests the order it is given, which is
    what makes it a test of nesting along a stated ordering rather than a
    property of the set. detect_groups is what establishes that ordering, and
    this pair of assertions is the contract between the two.
    """
    scrambled = list(nested_block.columns)
    ordered = nested_block.isna().mean().sort_values().index.tolist()

    assert nesting_report(nested_block, ordered)["n_exceptions"] == 0
    assert nesting_report(nested_block, ordered)["nested_share"] == 1.0
    assert nesting_report(nested_block, scrambled)["n_exceptions"] > 0


def test_the_pattern_count_alone_proves_nothing(nested_block):
    """A nested block of eight columns yields nine patterns. So would any nine
    patterns, which is why the forbidden-pattern test exists."""
    ordered = nested_block.isna().mean().sort_values().index.tolist()
    report = nesting_report(nested_block, ordered)
    assert report["n_patterns"] == report["n_if_nested"] == 9
    assert report["n_possible"] == 256


def test_independent_absence_is_not_nested():
    rng = np.random.default_rng(1)
    frame = pd.DataFrame(np.where(rng.random((500, 8)) < 0.3, np.nan, 1.0),
                         columns=[f"c{i}" for i in range(8)])
    ordered = frame.isna().mean().sort_values().index.tolist()
    report = nesting_report(frame, ordered)
    assert report["nested_share"] < 0.5
    assert report["n_exceptions"] > 0


def test_depth_counts_absent_columns(nested_block):
    levels = depth(nested_block, list(nested_block.columns))
    assert levels.min() == 0
    assert levels.max() == 8
    assert set(levels.unique()) <= set(range(9))


# ------------------------------------------------------ group detection
def test_detection_separates_the_two_directions(informative_missingness):
    frame, y = informative_missingness
    groups = detect_groups(frame, y, threshold=0.10)
    assert "informative_pos" in groups["group1"]
    assert "informative_neg" in groups["group2"]
    assert "mute" in groups["mute"]
    assert "complete" in groups["mute"]


def test_every_column_lands_in_exactly_one_group(informative_missingness):
    frame, y = informative_missingness
    groups = detect_groups(frame, y, threshold=0.10)
    total = sum(len(groups[k]) for k in ("group1", "group2", "mute"))
    assert total == frame.shape[1]
    assert not set(groups["group1"]) & set(groups["group2"])


def test_group_one_is_ordered_by_ascending_absence(informative_missingness):
    """The ordering the nesting test depends on is established here."""
    frame, y = informative_missingness
    groups = detect_groups(frame, y, threshold=0.10)
    rates = frame.isna().mean()
    for name in ("group1", "group2"):
        ordered = [rates[c] for c in groups[name]]
        assert ordered == sorted(ordered)


# ------------------------------------------------- the leakage guarantee
def test_no_missing_value_survives_preparation(two_parts):
    fit, held = two_parts
    pre = Preprocessor(group1=[], unscaled=[]).fit(fit)
    assert pre.transform(fit).isna().sum().sum() == 0
    assert pre.transform(held).isna().sum().sum() == 0


def test_statistics_come_from_the_fitting_part_only(two_parts):
    """Mean 0 and unit variance on the fitting part, and neither on the
    held-out part. Both being centred would mean the scaler saw both."""
    fit, held = two_parts
    pre = Preprocessor(group1=[], unscaled=[]).fit(fit)
    assert pre.transform(fit)["a"].mean() == pytest.approx(0, abs=1e-10)
    assert pre.transform(fit)["a"].std() == pytest.approx(1, abs=0.01)
    assert abs(pre.transform(held)["a"].mean()) > 1.0


def test_group_one_is_imputed_with_zero(two_parts):
    fit, _ = two_parts
    pre = Preprocessor(group1=["b"], unscaled=["b"]).fit(fit)
    transformed = pre.transform(fit)
    assert (transformed.loc[fit["b"].isna(), "b"] == 0).all()


def test_unscaled_columns_keep_their_values(two_parts):
    fit, _ = two_parts
    fit = fit.assign(depth_g1=np.arange(len(fit)) % 9)
    pre = Preprocessor(group1=[], unscaled=["depth_g1"]).fit(fit)
    transformed = pre.transform(fit)
    assert transformed["depth_g1"].min() == 0
    assert transformed["depth_g1"].max() == 8


def test_column_order_and_index_are_preserved(two_parts):
    fit, held = two_parts
    pre = Preprocessor(group1=[], unscaled=[]).fit(fit)
    out = pre.transform(held)
    assert list(out.columns) == list(fit.columns)
    assert list(out.index) == list(held.index)


# ------------------------------------------------------- the cost metric
def test_the_published_2016_winner_reconstructs():
    """The strongest check available, because the figure is a third party's.
    If this fails, no cost in this repository is comparable to the literature.
    """
    truth = np.r_[np.ones(375, int), np.zeros(15_625, int)]
    predicted = np.r_[np.ones(366, int), np.zeros(9, int),
                      np.ones(542, int), np.zeros(15_083, int)]
    assert total_cost(truth, predicted) == 9920


def test_a_constant_score_still_yields_the_cheaper_rule():
    """Flagging nothing is never an observed cut point but is sometimes the
    cheapest decision. The loop this sweep replaced could not reach it."""
    truth = np.r_[np.ones(20, int), np.zeros(980, int)]
    scores = np.full(1000, 0.0167)
    _, cost = best_threshold(truth, scores)
    assert cost == min(20 * COST_FN, 980 * COST_FP)
