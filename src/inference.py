"""Production inference artefact (EF07, EF08).

Bundles the frozen model, its threshold and the preparation chain behind one
interface, so the demonstrator never needs to know which model family sits
underneath.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.config import COST_FN, COST_FP, MODELS_DIR
from src.preprocessing import load as load_artifact

MANIFEST = MODELS_DIR / "final_model.json"


@dataclass
class Prediction:
    """One truck's verdict."""

    probability: float
    flagged: bool
    threshold: float

    @property
    def risk_band(self) -> str:
        """Three bands, for readability only. Not a modelling decision."""
        if self.probability >= self.threshold * 5:
            return "high"
        if self.probability >= self.threshold:
            return "moderate"
        return "low"


class Predictor:
    """Load once, predict many times."""

    def __init__(self, model, threshold, name, encoder, preprocessor,
                 raw_columns):
        self.model = model
        self.threshold = threshold
        self.name = name
        self.encoder = encoder
        self.preprocessor = preprocessor
        self.raw_columns = raw_columns

    @classmethod
    def load(cls, manifest_path: Path = MANIFEST) -> "Predictor":
        """Rebuild the predictor from the manifest written at freeze time."""
        with open(manifest_path, encoding="utf-8") as handle:
            manifest = json.load(handle)

        name = manifest["model"]
        stem = name.replace(" ", "_")

        joblib_path = MODELS_DIR / f"{stem}.joblib"
        if joblib_path.exists():
            model = joblib.load(joblib_path)
        else:
            from tensorflow import keras
            model = keras.models.load_model(MODELS_DIR / f"{stem}.keras",
                                            compile=False)

        encoder = load_artifact("missingness_encoder.joblib")
        preprocessor = load_artifact("preprocessor.joblib")

        # The raw columns the chain expects, before any variable is built
        prepared = manifest["columns"]
        built = ["depth_g1"] + [c for c in prepared if c.startswith("missing_sb")]
        raw_columns = [c for c in prepared if c not in built]

        return cls(model, manifest["threshold"], name, encoder, preprocessor,
                   raw_columns)

    def _align(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Reorder and complete columns to match training.

        A file whose columns arrive in a different order, or which is missing
        some, would otherwise produce nonsense with no error at all. That is the
        most dangerous failure mode of a demonstrator, because it is silent.
        """
        frame = frame.copy()
        if "class" in frame.columns:
            frame = frame.drop(columns=["class"])

        missing = [c for c in self.raw_columns if c not in frame.columns]
        extra = [c for c in frame.columns if c not in self.raw_columns]

        aligned = frame.reindex(columns=self.raw_columns)
        aligned = aligned.apply(pd.to_numeric, errors="coerce")

        self.last_alignment_ = {"missing": missing, "extra": extra,
                                "rows": len(frame)}
        return aligned

    def prepare(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Replay the exact preparation chain used on the training data."""
        aligned = self._align(frame)
        return self.preprocessor.transform(self.encoder.transform(aligned))

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        prepared = self.prepare(frame)
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(prepared)[:, 1]
        return self.model.predict(np.asarray(prepared, dtype="float32"),
                                  batch_size=1024, verbose=0).ravel()

    def predict(self, frame: pd.DataFrame, threshold: float = None) -> list:
        """One Prediction per row. threshold overrides the frozen one."""
        applied = self.threshold if threshold is None else threshold
        return [Prediction(float(p), bool(p >= applied), applied)
                for p in self.predict_proba(frame)]

    def expected_cost(self, probabilities, threshold: float) -> dict:
        """Expected cost of a fleet at a given threshold.

        Each truck contributes (1 - p) * COST_FP if flagged, p * COST_FN if not.
        This is an expectation under the model's own probabilities, so it is
        only as trustworthy as the model's calibration.
        """
        p = np.asarray(probabilities)
        flagged = p >= threshold
        return {
            "flagged": int(flagged.sum()),
            "expected_cost": float(((1 - p[flagged]) * COST_FP).sum()
                                   + (p[~flagged] * COST_FN).sum()),
        }
