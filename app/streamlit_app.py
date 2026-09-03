"""Streamlit demonstrator (D7, EF08).

Run: streamlit run app/streamlit_app.py
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import streamlit as st

from src.config import BAYES_THRESHOLD, COST_FN, COST_FP, MODELS_DIR
from src.data import load
from src.inference import Predictor

st.set_page_config(page_title="APS failure triage", layout="wide")


@st.cache_resource
def get_predictor():
    """Cached: reloading the model on every slider move would be unusable."""
    return Predictor.load()


@st.cache_data
def get_manifest():
    with open(MODELS_DIR / "final_model.json", encoding="utf-8") as handle:
        return json.load(handle)


predictor = get_predictor()
manifest = get_manifest()

st.title("Air pressure system failure triage")
st.caption(f"Model: {predictor.name}. Frozen threshold: "
           f"{predictor.threshold:.5f}. Trained on 48 000 workshop records.")

# --- Sidebar: the economic trade-off, made visible -----------------------
st.sidebar.header("Operating point")
threshold = st.sidebar.slider(
    "Decision threshold", 0.0001, 0.5000,
    value=float(predictor.threshold), step=0.0001, format="%.4f")

st.sidebar.markdown(
    f"""
**Cost matrix**

- Useless inspection: {COST_FP}
- Missed failure: {COST_FN}

Bayes threshold on a calibrated probability: {BAYES_THRESHOLD:.4f}

Frozen threshold: {predictor.threshold:.5f}

Lowering the threshold catches more failures at the price of more false alarms.
The frozen value is the one that minimised cost on data the model never saw.
"""
)

if st.sidebar.button("Reset to the frozen threshold"):
    st.rerun()

tab_file, tab_manual, tab_model = st.tabs(
    ["Batch from a file", "Single vehicle", "About the model"])

# --- Tab 1: a fleet at a time -------------------------------------------
with tab_file:
    st.subheader("Score a fleet")
    uploaded = st.file_uploader("CSV of sensor readings", type="csv")

    if st.button("Load a demonstration sample"):
        st.session_state["sample"] = load("test").drop(columns=["class"]).head(300)

    frame = None
    if uploaded is not None:
        frame = pd.read_csv(uploaded, na_values="na")
    elif "sample" in st.session_state:
        frame = st.session_state["sample"]

    if frame is not None:
        start = time.perf_counter()
        probability = predictor.predict_proba(frame)
        elapsed = (time.perf_counter() - start) * 1000

        report = predictor.last_alignment_
        if report["missing"]:
            st.warning(
                f"{len(report['missing'])} expected columns are absent and were "
                f"treated as missing readings: {report['missing'][:8]}"
                + (" and others" if len(report["missing"]) > 8 else ""))
        if report["extra"]:
            st.info(f"{len(report['extra'])} unknown columns were ignored.")

        flagged = probability >= threshold
        economics = predictor.expected_cost(probability, threshold)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Vehicles", len(frame))
        col2.metric("To inspect", int(flagged.sum()))
        col3.metric("Alert rate", f"{flagged.mean():.1%}")
        col4.metric("Scoring time", f"{elapsed:.0f} ms")

        st.caption(
            f"Expected cost at this threshold: {economics['expected_cost']:,.0f} "
            "units. This is an expectation under the model's own probabilities, "
            "so it is only as trustworthy as its calibration.")

        results = pd.DataFrame({
            "vehicle": range(1, len(frame) + 1),
            "probability": probability.round(5),
            "verdict": np.where(flagged, "INSPECT", "clear"),
        }).sort_values("probability", ascending=False)

        st.dataframe(results, use_container_width=True, height=340)
        st.download_button("Download the verdicts",
                           results.to_csv(index=False).encode("utf-8"),
                           "verdicts.csv", "text/csv")

        st.bar_chart(pd.Series(np.sort(probability)[::-1]).clip(upper=0.5),
                     height=180)
        st.caption("Predicted probability per vehicle, ranked. The flatter the "
                   "left shoulder, the more vehicles the model is unsure about.")

# --- Tab 2: one vehicle, typed in ---------------------------------------
with tab_manual:
    st.subheader("Score one vehicle")
    st.caption("Readings left blank are treated as missing, which the model "
               "handles: the absence pattern is itself an input.")

    shown = predictor.raw_columns[:12]
    values = {}
    columns = st.columns(4)
    for index, name in enumerate(shown):
        with columns[index % 4]:
            entry = st.text_input(name, value="", key=f"field_{name}")
            values[name] = float(entry) if entry.strip() else None

    if st.button("Predict", type="primary"):
        row = pd.DataFrame([values])
        prediction = predictor.predict(row, threshold=threshold)[0]

        col1, col2 = st.columns(2)
        col1.metric("Failure probability", f"{prediction.probability:.5f}")
        col2.metric("Risk band", prediction.risk_band.upper())

        if prediction.flagged:
            st.error("Inspect the air pressure system.")
        else:
            st.success("No anomaly at the current operating point.")

        st.progress(min(prediction.probability / (threshold * 5), 1.0))

# --- Tab 3: what the model is -------------------------------------------
with tab_model:
    st.subheader("The frozen model")
    st.json({k: v for k, v in manifest.items() if k != "columns"})
    st.caption(
        "The threshold was tuned by inner cross-validation on the fitting rows, "
        "never on the data used to report a result. The official test set was "
        "opened once, on this model, after it was frozen.")
