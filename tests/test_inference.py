"""The frozen model behind the demonstrator (EF07, EF08).

The alignment tests are the ones that matter: a file whose columns arrive in
a different order produces nonsense with no error at all, which is the most
dangerous failure mode a demonstrator has.
"""

import json

import numpy as np
import pytest

from src.config import MODELS_DIR

pytestmark = [pytest.mark.needs_model, pytest.mark.needs_prepared]


@pytest.fixture(scope="module")
def manifest():
    with open(MODELS_DIR / "final_model.json", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="module")
def predictor():
    from src.inference import Predictor
    return Predictor.load()


def test_the_manifest_records_what_was_frozen(manifest):
    assert manifest["model"] == "gradient boosting"
    assert manifest["deciding_criterion"]
    assert manifest["fitted_on"] == "48 000 fitting rows"
    assert len(manifest["columns"]) == 180
    assert 0 < manifest["threshold"] < 0.5


def test_the_manifest_agrees_with_the_reserved_measurement(manifest):
    import pandas as pd
    from src.config import ROOT
    arbitration = pd.read_csv(ROOT / "reports" / "arbitration.csv", index_col=0)
    row = arbitration.loc["gradient boosting"]
    assert manifest["reserved_cost"] == pytest.approx(row["cost"])
    assert manifest["reserved_recall"] == pytest.approx(row["recall"])
    assert manifest["reserved_missed"] == pytest.approx(row["FN"])
    assert manifest["reserved_false_alarms"] == pytest.approx(row["FP"])
    assert manifest["threshold"] == pytest.approx(row["threshold"])


def test_the_predictor_loads_the_frozen_threshold(predictor, manifest):
    assert predictor.name == manifest["model"]
    assert predictor.threshold == pytest.approx(manifest["threshold"])
    assert len(predictor.raw_columns) == 170


def test_probabilities_are_in_range(predictor, prepared):
    from src.config import PROCESSED_DIR
    import pandas as pd
    raw = pd.read_csv(PROCESSED_DIR / "X_fit.csv", index_col=0).head(50)
    del raw
    from src.data import load
    frame = load("train").head(50).drop(columns=["class"])
    p = predictor.predict_proba(frame)
    assert p.shape == (50,)
    assert ((p >= 0) & (p <= 1)).all()


def test_shuffled_columns_give_the_same_answer(predictor):
    """The alignment step exists for this. Without it the prediction would
    change silently."""
    from src.data import load
    frame = load("train").head(20).drop(columns=["class"])
    shuffled = frame[list(reversed(frame.columns))]
    assert predictor.predict_proba(frame) == pytest.approx(
        predictor.predict_proba(shuffled))


def test_a_missing_column_is_reported_not_ignored(predictor):
    from src.data import load
    frame = load("train").head(20).drop(columns=["class", "aa_000"])
    predictor.predict_proba(frame)
    assert "aa_000" in predictor.last_alignment_["missing"]


def test_an_extra_column_is_reported_and_dropped(predictor):
    from src.data import load
    frame = load("train").head(20).drop(columns=["class"])
    frame = frame.assign(not_a_sensor=1.0)
    predictor.predict_proba(frame)
    assert "not_a_sensor" in predictor.last_alignment_["extra"]


def test_the_verdict_follows_the_threshold(predictor):
    from src.data import load
    frame = load("train").head(30).drop(columns=["class"])
    predictions = predictor.predict(frame)
    for prediction in predictions:
        assert prediction.flagged == (prediction.probability >= predictor.threshold)
        assert prediction.risk_band in {"low", "moderate", "high"}


def test_expected_cost_brackets_the_two_constant_rules(predictor):
    """At threshold 0 everything is flagged, at threshold 1 nothing is."""
    from src.data import load
    frame = load("train").head(500).drop(columns=["class"])
    p = predictor.predict_proba(frame)
    everything = predictor.expected_cost(p, 0.0)
    nothing = predictor.expected_cost(p, 1.1)
    assert everything["flagged"] == 500
    assert nothing["flagged"] == 0
    at_threshold = predictor.expected_cost(p, predictor.threshold)
    assert at_threshold["expected_cost"] <= max(everything["expected_cost"],
                                                nothing["expected_cost"])
