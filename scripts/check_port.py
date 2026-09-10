"""Verify that the board predicts what the development machine predicts.

Run on the board after setup_pi.sh. A mismatch here means the deployed model
is not the evaluated one, and no latency figure is worth taking until it is
resolved.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.config import ROOT  # noqa: E402
from src.inference import Predictor  # noqa: E402

TOLERANCE = 1e-9


def main() -> None:
    chemin = ROOT / "reports" / "portage_reference.json"
    with open(chemin, encoding="utf-8") as handle:
        reference = json.load(handle)

    predictor = Predictor.load()

    print("=== identité du modèle ===")
    for cle in ("model", "threshold", "n_columns"):
        attendu = reference[cle]
        obtenu = {"model": predictor.name,
                  "threshold": predictor.threshold,
                  "n_columns": len(predictor.raw_columns)}[cle]
        etat = "ok  " if obtenu == attendu else "ÉCART"
        print(f"  [{etat}] {cle:<12} attendu {attendu}, obtenu {obtenu}")

    print("\n=== prédictions ===")
    lot = pd.DataFrame(reference["vehicles"])
    obtenues = predictor.predict_proba(lot)
    attendues = np.array(reference["probabilities"])

    ecarts = np.abs(obtenues - attendues)
    print(f"  véhicules       : {len(obtenues)}")
    print(f"  écart maximal   : {ecarts.max():.2e}")
    print(f"  écart moyen     : {ecarts.mean():.2e}")
    print(f"  tolérance       : {TOLERANCE:.0e}")

    if ecarts.max() > TOLERANCE:
        print("\n  ÉCART AU-DELÀ DE LA TOLÉRANCE")
        print("  Le modèle déployé ne prédit pas comme le modèle évalué.")
        print("  Les cinq écarts les plus grands :")
        for i in np.argsort(ecarts)[-5:][::-1]:
            print(f"    véhicule {i:>3} : attendu {attendues[i]:.10f}, "
                  f"obtenu {obtenues[i]:.10f}")
        sys.exit(1)

    print("\n  portage vérifié : les prédictions sont identiques")


if __name__ == "__main__":
    main()
