"""HTTP inference service (extension: client-server boundary for EF09 and
for a genuinely embedded consumer of the frozen model).

The dashboard and the notebooks import ``Predictor`` directly, in-process.
That is fine for a human clicking through a demonstrator, but it is not what
a real deployment looks like: a workshop terminal, a gateway on the truck, or
a real-time flow simulation would talk to this model over the network, never
import scikit-learn or the model file itself. This module is that boundary.

It changes nothing about the frozen model, the threshold, or the preparation
chain: ``get_predictor()`` calls the exact same ``Predictor.load()`` the
dashboard already uses (src/inference.py). This file only adds a transport.

Run directly:      uvicorn src.api:app --host 0.0.0.0 --port 8000
Run in the image:  see docker-compose.yml, service "api"
"""

from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.inference import Predictor

app = FastAPI(
    title="APS failure triage API",
    description=(
        "Frozen gradient boosting model (EF06), cost-sensitive threshold "
        "tuned out of sample (section 7.5 of the report)."
    ),
    version="1.0",
)

# Loaded once, on first request, exactly like the dashboard's
# @st.cache_resource: rebuilding the preparation chain per request would make
# the "prediction under 1s" requirement (ENF06) meaningless.
_predictor: Optional[Predictor] = None

# A client posting 100,000 vehicles would hold the request open indefinitely
# with an in-memory DataFrame that grows without bound. This is a safety cap.
MAX_FLEET = 5000


def get_predictor() -> Predictor:
    global _predictor
    if _predictor is None:
        _predictor = Predictor.load()
    return _predictor


class VehicleReadings(BaseModel):
    """Raw sensor readings for one truck, keyed by column name.

    Fields absent from ``readings`` are not an error: ``Predictor._align()``
    treats a missing column exactly as it was treated at training time,
    because absence is itself part of the signal (section 5 of the report).
    Sending an empty dict is valid and will be scored as "all missing".
    """

    readings: Dict[str, Optional[float]] = Field(default_factory=dict)
    threshold: Optional[float] = Field(
        default=None,
        description="Override the frozen threshold. Omit to use the frozen one.",
    )


class FleetReadings(BaseModel):
    vehicles: List[Dict[str, Optional[float]]]
    threshold: Optional[float] = None


class PredictionOut(BaseModel):
    probability: float
    flagged: bool
    risk_band: str
    threshold: float
    # A client sending the wrong columns would otherwise get a perfectly
    # plausible probability with no warning, which is the silent failure this
    # project has spent its time avoiding.
    n_expected_columns: int
    n_missing_columns: int
    n_unknown_columns: int


@app.get("/health")
def health():
    """Liveness/readiness probe. Also confirms the model actually loaded,
    which a bare process-alive check would not catch."""
    predictor = get_predictor()
    return {"status": "ok", "model": predictor.name}


@app.get("/model")
def model_info():
    """Same manifest fields the dashboard's 'About the model' tab reads."""
    predictor = get_predictor()
    return {
        "name": predictor.name,
        "threshold": predictor.threshold,
        "n_raw_columns": len(predictor.raw_columns),
    }


@app.post("/predict", response_model=PredictionOut)
def predict(payload: VehicleReadings):
    """Score one vehicle. Mirrors the dashboard's 'Single vehicle' tab."""
    predictor = get_predictor()
    frame = pd.DataFrame([payload.readings])

    try:
        result = predictor.predict(frame, threshold=payload.threshold)[0]
    except (KeyError, ValueError, TypeError) as exc:
        # Malformed payload: the client can fix this.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        # Anything else is ours, not theirs. Returning 422 here would send the
        # client looking for a fault in data that is fine.
        raise HTTPException(status_code=500, detail="inference failed") from exc

    alignment = predictor.last_alignment_
    return PredictionOut(
        probability=result.probability,
        flagged=result.flagged,
        risk_band=result.risk_band,
        threshold=result.threshold,
        n_expected_columns=len(predictor.raw_columns),
        n_missing_columns=len(alignment["missing"]),
        n_unknown_columns=len(alignment["extra"]),
    )


@app.post("/predict/batch")
def predict_batch(payload: FleetReadings):
    """Score a fleet. Mirrors the dashboard's 'Batch from a file' tab,
    including the expected-cost figure at the given operating point."""
    if len(payload.vehicles) > MAX_FLEET:
        raise HTTPException(
            status_code=413,
            detail=f"at most {MAX_FLEET} vehicles per request"
        )

    predictor = get_predictor()
    frame = pd.DataFrame(payload.vehicles)

    try:
        results = predictor.predict(frame, threshold=payload.threshold)
    except (KeyError, ValueError, TypeError) as exc:
        # Malformed payload: the client can fix this.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        # Anything else is ours, not theirs.
        raise HTTPException(status_code=500, detail="inference failed") from exc

    probabilities = [r.probability for r in results]
    applied_threshold = (
        results[0].threshold if results
        else (payload.threshold or predictor.threshold)
    )
    economics = predictor.expected_cost(probabilities, applied_threshold)

    return {
        "predictions": [
            {
                "probability": r.probability,
                "flagged": r.flagged,
                "risk_band": r.risk_band,
            }
            for r in results
        ],
        "fleet": economics,
    }
