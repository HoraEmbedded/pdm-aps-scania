"""The preparation chain, and the evidence that it does not leak.

The checksum is the tripwire: any silent change to the chain moves it.
"""

import pandas as pd
import pytest

from tests.conftest import CHECKSUM

pytestmark = pytest.mark.needs_prepared


def test_prepared_table_shape_and_completeness(prepared):
    X, y = prepared
    assert X.shape == (48_000, 180)
    assert int(X.isna().sum().sum()) == 0
    assert int(y.sum()) == 800


def test_checksum(prepared):
    """Written down so that a change to the chain cannot pass unnoticed. It
    has moved before, each time for a reason recorded in the journal."""
    X, _ = prepared
    assert X.values.sum() == pytest.approx(CHECKSUM, abs=1.0)


def test_the_validation_part_keeps_its_own_scale(prepared):
    """Scaling is fitted on the fitting rows only, so the validation standard
    deviation must not be exactly 1. Equality would be the signature of a
    scaler fitted on everything."""
    from src.config import PROCESSED_DIR
    X_val = pd.read_csv(PROCESSED_DIR / "X_val.csv", index_col=0)
    flags = [c for c in X_val.columns if c.startswith("missing_sb")]
    scaled = [c for c in X_val.columns if c not in flags + ["depth_g1"]]
    observed = X_val[scaled].std().mean()
    assert observed == pytest.approx(0.897, abs=0.01)
    assert observed != pytest.approx(1.0, abs=0.05)


def test_the_fitting_part_is_centred_and_scaled(prepared):
    X, _ = prepared
    flags = [c for c in X.columns if c.startswith("missing_sb")]
    scaled = [c for c in X.columns if c not in flags + ["depth_g1"]]
    assert X[scaled].mean().mean() == pytest.approx(0.0, abs=1e-9)
    assert X[scaled].std().mean() == pytest.approx(0.994, abs=0.01)


def test_the_flags_and_the_depth_are_left_unscaled(prepared):
    X, _ = prepared
    flags = [c for c in X.columns if c.startswith("missing_sb")]
    for column in flags:
        assert set(X[column].unique()) <= {0, 1}
    assert X["depth_g1"].min() == 0
    assert X["depth_g1"].max() == 8


def test_the_constant_column_survives_as_constant(prepared):
    """cd_000 carries one distinct value in the whole file. Named here so
    that its zero standard deviation is a known fact rather than a surprise
    divide-by-zero later. Its permutation importance is exactly 0."""
    X, _ = prepared
    assert X["cd_000"].std() == 0


@pytest.mark.needs_raw
def test_the_fitted_medians_are_not_the_pooled_medians(split, encoder):
    """Leakage evidence, taken the other way round: if the medians learned on
    the fitting rows equalled the medians of both parts pooled, the
    validation part would have contributed to them."""
    from src.preprocessing import Preprocessor
    X_fit, X_val, y_fit, _ = split
    fit_encoded = encoder.transform(X_fit)
    val_encoded = encoder.transform(X_val)
    unscaled = ["depth_g1"] + encoder.flag_names_
    pre = Preprocessor(group1=encoder.group1_, unscaled=unscaled).fit(fit_encoded)
    pooled = pd.concat([fit_encoded, val_encoded])[pre.others_].median()
    assert int((pre.medians_ != pooled).sum()) == 85


@pytest.mark.needs_raw
def test_group_1_is_imputed_with_zero_not_the_median(split, encoder):
    """Its columns are absent for the least used trucks, so the median of the
    18% that carry a value is the median of a heavily used population."""
    from src.preprocessing import Preprocessor
    X_fit, _, _, _ = split
    encoded = encoder.transform(X_fit)
    unscaled = ["depth_g1"] + encoder.flag_names_
    pre = Preprocessor(group1=encoder.group1_, unscaled=unscaled).fit(encoded)
    imputed = pre._impute(encoded)
    for column in encoder.group1_:
        was_absent = encoded[column].isna()
        assert (imputed.loc[was_absent, column] == 0.0).all()


@pytest.mark.needs_raw
def test_the_chain_preserves_column_order_and_index(split, encoder):
    """Written by hand rather than with ColumnTransformer, which returns a
    bare array and emits its columns in transformer order."""
    from src.preprocessing import Preprocessor
    X_fit, _, _, _ = split
    encoded = encoder.transform(X_fit)
    unscaled = ["depth_g1"] + encoder.flag_names_
    pre = Preprocessor(group1=encoder.group1_, unscaled=unscaled).fit(encoded)
    out = pre.transform(encoded)
    assert list(out.columns) == list(encoded.columns)
    assert list(out.index) == list(encoded.index)
