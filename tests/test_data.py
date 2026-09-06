"""Loading and splitting."""

import numpy as np
import pytest

from src.config import BAYES_THRESHOLD, TARGET

pytestmark = pytest.mark.needs_raw


def test_training_file_shape_and_class_count():
    from src.data import load
    train = load("train")
    assert train.shape == (60_000, 171)
    assert int(train[TARGET].sum()) == 1000
    assert train[TARGET].mean() == pytest.approx(0.016667, abs=1e-6)


def test_missing_values_are_parsed_as_missing():
    """The file writes absences as the text 'na'. Without na_values the read
    succeeds silently, every column comes back as text, and the missing count
    returns zero everywhere."""
    from src.data import load
    train = load("train")
    assert train.isna().sum().sum() > 0
    assert train.isna().mean().mean() == pytest.approx(0.0833, abs=5e-4)


def test_split_sizes_and_no_overlap(split):
    X_fit, X_val, y_fit, y_val = split
    assert X_fit.shape == (48_000, 170)
    assert X_val.shape == (12_000, 170)
    assert int(y_fit.sum()) == 800
    assert int(y_val.sum()) == 200
    assert not set(X_fit.index) & set(X_val.index)
    assert len(X_fit) + len(X_val) == 60_000


def test_stratification_is_exact_on_both_sides(split):
    _, _, y_fit, y_val = split
    assert y_fit.mean() == pytest.approx(y_val.mean(), abs=1e-9)
    assert y_val.mean() < BAYES_THRESHOLD


def test_the_split_is_deterministic(split):
    from src.data import train_validation_split
    _, X_val, _, _ = split
    _, again, _, _ = train_validation_split()
    assert list(X_val.index) == list(again.index)
    assert int(X_val.index.to_numpy().sum()) == 357_794_337


def test_an_unstratified_draw_can_cross_the_break_even_rate(split):
    """Why stratification is not cosmetic: over 500 unstratified draws the
    validation positive rate straddles 1.96%, which changes which constant
    rule is the reference to beat."""
    import pandas as pd
    _, _, y_fit, y_val = split
    y = pd.concat([y_fit, y_val]).to_numpy()
    rng = np.random.default_rng(42)
    rates = np.array([y[rng.permutation(len(y))[:12_000]].mean()
                      for _ in range(500)])
    assert rates.min() < BAYES_THRESHOLD < rates.max()


def test_the_sealed_test_file_is_never_touched_by_the_split(split):
    """train_validation_split must read the training file only."""
    from src.config import TEST_FILE
    from src.data import load_sealed_test
    assert TEST_FILE.exists()
    X_test, y_test = load_sealed_test()
    assert X_test.shape == (16_000, 170)
    assert int(y_test.sum()) == 375
    _, X_val, _, _ = split
    assert not set(X_val.index) & set(X_test.index[:0])
