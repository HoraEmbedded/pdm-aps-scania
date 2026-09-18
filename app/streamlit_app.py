"""Streamlit demonstrator, bilingual.

Run: streamlit run app/streamlit_app.py

The interface exists in French and English behind one implementation. A second
file would have meant every fix applied twice, and the two copies drifting
apart, which is the exact failure this project has spent its time avoiding.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import streamlit as st

from src.config import BAYES_THRESHOLD, COST_FN, COST_FP, MODELS_DIR
from src.data import load
from src.inference import Predictor

# =========================================================================
# Labels
#
# One dictionary rather than a translated copy of the file. Adding a language
# means adding a column here; changing a behaviour means changing it once.
# =========================================================================

T = {
    "fr": {
        "page_title": "Triage des pannes du circuit d'air comprimé",
        "title": "Triage des pannes du circuit d'air comprimé",
        "subtitle": ("Modèle : {model}. Seuil figé : {threshold}. "
                     "Entraîné sur 48 000 dossiers d'atelier."),
        "language": "Langue",

        "operating_point": "Point de fonctionnement",
        "threshold": "Seuil de décision",
        "threshold_help": ("Probabilité au-delà de laquelle le véhicule est "
                           "envoyé en inspection."),
        "cost_matrix": "Ce que coûte une erreur",
        "cost_fp": "Inspection inutile",
        "cost_fn": "Panne non détectée",
        "cost_ratio": ("Rater une panne coûte **{ratio} fois** plus cher "
                       "qu'une inspection inutile. C'est ce rapport qui "
                       "gouverne toutes les décisions du système."),
        "bayes": "Seuil théorique sur une probabilité calibrée",
        "frozen": "Seuil figé, retenu",
        "threshold_note": ("Baisser le seuil attrape plus de pannes, au prix "
                           "de plus de fausses alertes. La valeur figée est "
                           "celle qui minimisait le coût sur des données que "
                           "le modèle n'avait jamais vues."),
        "reset": "Revenir au seuil figé",

        "tab_fleet": "Une flotte",
        "tab_single": "Un véhicule",
        "tab_model": "Le modèle",
        "tab_api": "Par le réseau",

        "fleet_header": "Noter une flotte de véhicules",
        "upload": "Fichier CSV de relevés capteurs",
        "load_sample": "Charger un échantillon de démonstration",
        "m_vehicles": "Véhicules",
        "m_inspect": "À inspecter",
        "m_rate": "Taux d'alerte",
        "m_time": "Temps de notation",
        "expected_cost": (
            "**Coût attendu à ce seuil : {cost} unités.** Il est calculé "
            "à partir des probabilités du modèle lui-même. Il augmente quand "
            "le seuil baisse sur cet échantillon, et c'est normal : le seuil "
            "figé minimise le coût sur une population d'atelier comportant "
            "1,67 % de pannes du circuit d'air, pas sur 300 véhicules qui n'en "
            "comptent qu'une."),
        "col_vehicle": "Véhicule",
        "col_probability": "Probabilité",
        "col_verdict": "Verdict",
        "inspect": "À INSPECTER",
        "clear": "Écarté",
        "download": "Télécharger les verdicts",
        "missing_cols": ("{n} colonnes attendues sont absentes et ont été "
                         "traitées comme des relevés manquants."),
        "extra_cols": "{n} colonnes inconnues ont été ignorées.",

        "curve_title": "Le coût selon le seuil, sur cette flotte",
        "curve_x": "seuil de décision, échelle logarithmique",
        "curve_y": "coût attendu",
        "curve_current": "seuil courant, {v}",
        "curve_frozen": "seuil figé, {v}",

        "single_header": "Noter un véhicule",
        "single_note": ("Les {shown} premiers relevés sur {total} sont "
                        "affichés. Un champ laissé vide est traité comme un "
                        "relevé manquant, ce que le modèle sait gérer : "
                        "l'absence de mesure est elle-même une information."),
        "predict": "Prédire",
        "m_probability": "Probabilité de panne",
        "m_band": "Niveau de risque",
        "verdict_inspect": "Inspecter le circuit d'air comprimé.",
        "verdict_clear": "Aucune anomalie au point de fonctionnement actuel.",
        "band_high": "ÉLEVÉ",
        "band_moderate": "MODÉRÉ",
        "band_low": "FAIBLE",

        "model_header": "Le modèle figé",
        "model_note": ("Le seuil a été réglé par validation croisée interne "
                       "sur les données d'apprentissage, jamais sur celles qui "
                       "servent à rapporter un résultat. Le jeu de test "
                       "officiel a été ouvert une seule fois, sur ce modèle, "
                       "après son gel."),

        "api_header": "Client externe, démonstration réseau",
        "api_note": ("Cet onglet n'importe pas le modèle : il envoie une "
                     "requête HTTP à {url}/predict, comme le ferait un poste "
                     "d'atelier ou une passerelle embarquée qui n'aurait ni "
                     "bibliothèque d'apprentissage ni fichier de modèle. La "
                     "latence mesurée ici inclut le transport réseau."),
        "api_ok": "Service disponible sur {url}, modèle chargé : {model}",
        "api_ko": ("Service injoignable sur {url}. Le démarrer avec "
                   "`uvicorn src.api:app --host 0.0.0.0 --port 8000`, ou "
                   "`docker compose up`. Détail : {error}"),
        "api_predict": "Prédire par le réseau",
        "m_latency": "Latence réseau",
        "api_compare": ("À comparer au temps de calcul de l'onglet « Une "
                        "flotte ». L'écart entre les deux est le coût du "
                        "transport, pas celui du modèle."),
        "api_alignment": ("Colonnes attendues : {expected}. Manquantes : "
                          "{missing}. Inconnues : {unknown}."),
        "api_error": "Le service a répondu {code} : {text}",
    },
    "en": {
        "page_title": "Air pressure system failure triage",
        "title": "Air pressure system failure triage",
        "subtitle": ("Model: {model}. Frozen threshold: {threshold}. "
                     "Trained on 48 000 workshop records."),
        "language": "Language",

        "operating_point": "Operating point",
        "threshold": "Decision threshold",
        "threshold_help": ("Probability above which a vehicle is sent for "
                           "inspection."),
        "cost_matrix": "What an error costs",
        "cost_fp": "Useless inspection",
        "cost_fn": "Missed failure",
        "cost_ratio": ("Missing a failure costs **{ratio} times** more than a "
                       "useless inspection. That ratio governs every decision "
                       "the system makes."),
        "bayes": "Theoretical threshold on a calibrated probability",
        "frozen": "Frozen threshold, in use",
        "threshold_note": ("Lowering the threshold catches more failures at "
                           "the price of more false alarms. The frozen value "
                           "is the one that minimised cost on data the model "
                           "never saw."),
        "reset": "Reset to the frozen threshold",

        "tab_fleet": "A fleet",
        "tab_single": "One vehicle",
        "tab_model": "The model",
        "tab_api": "Over the network",

        "fleet_header": "Score a fleet",
        "upload": "CSV of sensor readings",
        "load_sample": "Load a demonstration sample",
        "m_vehicles": "Vehicles",
        "m_inspect": "To inspect",
        "m_rate": "Alert rate",
        "m_time": "Scoring time",
        "expected_cost": (
            "**Expected cost at this threshold: {cost} units.** It is "
            "computed from the model's own probabilities. It rises as the "
            "threshold falls on this sample, and that is expected: the frozen "
            "threshold minimises cost on a workshop population carrying 1.67% "
            "APS failures, not on 300 vehicles carrying one."),
        "col_vehicle": "Vehicle",
        "col_probability": "Probability",
        "col_verdict": "Verdict",
        "inspect": "INSPECT",
        "clear": "Cleared",
        "download": "Download the verdicts",
        "missing_cols": ("{n} expected columns are absent and were treated as "
                         "missing readings."),
        "extra_cols": "{n} unknown columns were ignored.",

        "curve_title": "Cost against threshold, on this fleet",
        "curve_x": "decision threshold, log scale",
        "curve_y": "expected cost",
        "curve_current": "current threshold, {v}",
        "curve_frozen": "frozen threshold, {v}",

        "single_header": "Score one vehicle",
        "single_note": ("The first {shown} of {total} readings are shown. A "
                        "field left blank is treated as a missing reading, "
                        "which the model handles: the absence pattern is "
                        "itself an input."),
        "predict": "Predict",
        "m_probability": "Failure probability",
        "m_band": "Risk band",
        "verdict_inspect": "Inspect the air pressure system.",
        "verdict_clear": "No anomaly at the current operating point.",
        "band_high": "HIGH",
        "band_moderate": "MODERATE",
        "band_low": "LOW",

        "model_header": "The frozen model",
        "model_note": ("The threshold was tuned by inner cross-validation on "
                       "the fitting rows, never on the data used to report a "
                       "result. The official test set was opened once, on this "
                       "model, after it was frozen."),

        "api_header": "External client, network demonstration",
        "api_note": ("This tab does not import the model: it sends an HTTP "
                     "request to {url}/predict, as a workshop terminal or an "
                     "embedded gateway would, having neither the learning "
                     "library nor the model file. The latency measured here "
                     "includes network transport."),
        "api_ok": "Service reachable at {url}, model loaded: {model}",
        "api_ko": ("Service unreachable at {url}. Start it with "
                   "`uvicorn src.api:app --host 0.0.0.0 --port 8000`, or "
                   "`docker compose up`. Detail: {error}"),
        "api_predict": "Predict over the network",
        "m_latency": "Network latency",
        "api_compare": ("Compare with the scoring time on the fleet tab. The "
                        "gap between the two is the cost of transport, not of "
                        "the model."),
        "api_alignment": ("Expected columns: {expected}. Missing: {missing}. "
                          "Unknown: {unknown}."),
        "api_error": "The service answered {code}: {text}",
    },
}

ROUGE = "#c0392b"
VERT = "#1e7a48"
BLEU = "#2c7fb8"

st.set_page_config(page_title="Triage APS", layout="wide")

# The "over the network" tab talks to src/api.py over HTTP instead of the
# in-process Predictor. Defaults to localhost for a bare `streamlit run`;
# docker-compose overrides it with the api service's internal hostname.
API_URL = os.environ.get("API_URL", "http://localhost:8000")


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

# --- Language, first thing in the sidebar --------------------------------
langue = st.sidebar.radio(
    "Langue / Language", options=["fr", "en"],
    format_func=lambda code: {"fr": "Français", "en": "English"}[code],
    horizontal=True)
t = T[langue]


def nombre(valeur, decimales=0):
    """Écrit un nombre selon la langue : 0,00237 et 1 234 en français,
    0.00237 et 1,234 en anglais, comme le rapport qui accompagne l'outil."""
    texte = f"{valeur:,.{decimales}f}"
    if langue == "fr":
        texte = texte.replace(",", "\u00a0").replace(".", ",")
    return texte


def pourcentage(part, decimales=1):
    """Une part (0,02) écrite en pourcentage : 2,0 % en français, 2.0% en anglais."""
    espace = "\u00a0" if langue == "fr" else ""
    return f"{nombre(100 * part, decimales)}{espace}%"

st.title(t["title"])
st.caption(t["subtitle"].format(model=predictor.name,
                                threshold=nombre(predictor.threshold, 5)))

# =========================================================================
# Sidebar: the economic trade-off, made visible
#
# The threshold slider and the cost matrix are the heart of the project, and
# they used to sit in the sidebar with no more emphasis than anything else.
# =========================================================================

st.sidebar.divider()
st.sidebar.subheader(t["operating_point"])

# The frozen threshold is 0.0023719..., which a linear slider with a 0.0001
# step cannot represent: Streamlit snaps it away and the demonstrator opens on
# the wrong operating point. A log-spaced grid containing the exact value fixes
# it, and matches how the threshold actually behaves, over three decades.
grid = sorted({round(v, 6) for v in np.logspace(-4, -0.3, 60)}
              | {round(predictor.threshold, 6)})

threshold = st.sidebar.select_slider(
    t["threshold"], options=grid,
    value=round(predictor.threshold, 6),
    format_func=lambda v: nombre(v, 5),
    help=t["threshold_help"])

if st.sidebar.button(t["reset"], use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader(t["cost_matrix"])

# Two metrics rather than a bullet list: the ratio between them is the single
# most important number of the project, and a reader should see it without
# reading a sentence.
sc1, sc2 = st.sidebar.columns(2)
sc1.metric(t["cost_fp"], COST_FP)
sc2.metric(t["cost_fn"], COST_FN)
st.sidebar.markdown(t["cost_ratio"].format(ratio=COST_FN // COST_FP))

st.sidebar.divider()
st.sidebar.markdown(
    f"{t['bayes']} : **{nombre(BAYES_THRESHOLD, 4)}**  \n"
    f"{t['frozen']} : **{nombre(predictor.threshold, 5)}**")
st.sidebar.caption(t["threshold_note"])

tab_file, tab_manual, tab_model, tab_api = st.tabs(
    [t["tab_fleet"], t["tab_single"], t["tab_model"], t["tab_api"]])


def colorer_verdict(valeur):
    """Colour the verdict column: red for inspect, green for cleared.

    Black text in a grey table is what a spreadsheet looks like. The one thing
    a reader should see at a glance is which vehicles need attention.
    """
    if valeur in (T["fr"]["inspect"], T["en"]["inspect"]):
        return f"color: {ROUGE}; font-weight: 700"
    return f"color: {VERT}"


# =========================================================================
# Tab 1: a fleet at a time
# =========================================================================
with tab_file:
    st.subheader(t["fleet_header"])

    uc1, uc2 = st.columns([3, 1])
    with uc1:
        uploaded = st.file_uploader(t["upload"], type="csv")
    with uc2:
        st.write("")
        st.write("")
        if st.button(t["load_sample"], use_container_width=True):
            st.session_state["sample"] = (
                load("test").drop(columns=["class"]).head(300))

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
            st.warning(t["missing_cols"].format(n=len(report["missing"])))
        if report["extra"]:
            st.info(t["extra_cols"].format(n=len(report["extra"])))

        flagged = probability >= threshold
        economics = predictor.expected_cost(probability, threshold)

        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t["m_vehicles"], f"{len(frame)}")
        col2.metric(t["m_inspect"], f"{int(flagged.sum())}")
        col3.metric(t["m_rate"], pourcentage(flagged.mean()))
        col4.metric(t["m_time"], f"{elapsed:.0f} ms")

        st.info(t["expected_cost"].format(cost=nombre(economics["expected_cost"])))

        resultats = pd.DataFrame({
            t["col_vehicle"]: range(1, len(frame) + 1),
            t["col_probability"]: probability.round(5),
            t["col_verdict"]: np.where(flagged, t["inspect"], t["clear"]),
        }).sort_values(t["col_probability"], ascending=False)

        st.dataframe(
            resultats.style
            .map(colorer_verdict, subset=[t["col_verdict"]])
            .format({t["col_probability"]: "{:.5f}"},
                    decimal="," if langue == "fr" else "."),
            use_container_width=True, height=320, hide_index=True)

        st.download_button(t["download"],
                           resultats.to_csv(index=False).encode("utf-8"),
                           "verdicts.csv", "text/csv")

        # The ranked-probability bar chart showed nothing on a linear scale
        # when almost every vehicle sits near zero. The cost curve is what the
        # slider actually moves along, so it is the useful visual here.
        st.divider()
        st.markdown(f"**{t['curve_title']}**")

        sweep = np.unique(np.quantile(probability, np.linspace(0.5, 1.0, 200)))
        costs = [predictor.expected_cost(probability, v)["expected_cost"]
                 for v in sweep]

        fig, ax = plt.subplots(figsize=(9, 3.2))
        ax.plot(sweep, costs, color=BLEU, lw=2)
        ax.axvline(threshold, color=ROUGE, ls="--", lw=1.6,
                   label=t["curve_current"].format(v=nombre(threshold, 5)))
        ax.axvline(predictor.threshold, color=VERT, ls=":", lw=1.6,
                   label=t["curve_frozen"].format(v=nombre(predictor.threshold, 5)))
        ax.set_xscale("log")
        ax.set_xlabel(t["curve_x"], fontsize=9)
        ax.set_ylabel(t["curve_y"], fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(fontsize=8, frameon=False)
        ax.grid(alpha=0.2)
        fig.tight_layout()
        st.pyplot(fig)

# =========================================================================
# Tab 2: one vehicle, typed in
# =========================================================================
with tab_manual:
    st.subheader(t["single_header"])
    st.caption(t["single_note"].format(shown=12,
                                        total=len(predictor.raw_columns)))

    shown = predictor.raw_columns[:12]
    values = {}
    columns = st.columns(4)
    for index, name in enumerate(shown):
        with columns[index % 4]:
            entry = st.text_input(name, value="", key=f"field_{name}")
            values[name] = float(entry) if entry.strip() else None

    if st.button(t["predict"], type="primary"):
        row = pd.DataFrame([values])
        prediction = predictor.predict(row, threshold=threshold)[0]

        bande = {"high": t["band_high"], "moderate": t["band_moderate"],
                 "low": t["band_low"]}[prediction.risk_band]

        st.divider()
        col1, col2 = st.columns(2)
        col1.metric(t["m_probability"], nombre(prediction.probability, 5))
        col2.metric(t["m_band"], bande)

        if prediction.flagged:
            st.error(t["verdict_inspect"])
        else:
            st.success(t["verdict_clear"])

        st.progress(min(prediction.probability / (threshold * 5), 1.0))

# =========================================================================
# Tab 3: what the model is
# =========================================================================
with tab_model:
    st.subheader(t["model_header"])
    st.json({k: v for k, v in manifest.items() if k != "columns"})
    st.caption(t["model_note"])

# =========================================================================
# Tab 4: the same model, called over HTTP
# =========================================================================
with tab_api:
    st.subheader(t["api_header"])
    st.caption(t["api_note"].format(url=API_URL))

    try:
        api_health = requests.get(f"{API_URL}/health", timeout=2).json()
        st.success(t["api_ok"].format(url=API_URL, model=api_health["model"]))
        api_reachable = True
    except requests.RequestException as exc:
        st.error(t["api_ko"].format(url=API_URL, error=exc))
        api_reachable = False

    if api_reachable:
        shown = predictor.raw_columns[:12]
        values = {}
        columns = st.columns(4)
        for index, name in enumerate(shown):
            with columns[index % 4]:
                entry = st.text_input(name, value="", key=f"api_field_{name}")
                values[name] = float(entry) if entry.strip() else None

        if st.button(t["api_predict"], type="primary"):
            start = time.perf_counter()
            response = requests.post(
                f"{API_URL}/predict",
                json={"readings": values, "threshold": threshold},
                timeout=5)
            elapsed = (time.perf_counter() - start) * 1000

            if response.status_code != 200:
                st.error(t["api_error"].format(code=response.status_code,
                                               text=response.text))
            else:
                result = response.json()
                st.divider()
                col1, col2, col3 = st.columns(3)
                col1.metric(t["m_probability"],
                            nombre(result['probability'], 5))
                col2.metric(t["col_verdict"],
                            t["inspect"] if result["flagged"] else t["clear"])
                col3.metric(t["m_latency"], f"{elapsed:.0f} ms")

                # The service reports how many columns it expected, missed and
                # ignored. A client sending the wrong payload would otherwise
                # get a plausible probability with no warning at all.
                if "n_expected_columns" in result:
                    st.caption(t["api_alignment"].format(
                        expected=result["n_expected_columns"],
                        missing=result["n_missing_columns"],
                        unknown=result["n_unknown_columns"]))

                st.caption(t["api_compare"])
