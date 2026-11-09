"""Rebuild the selected demonstrator from the public training data and reports."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.build_dataset import main as build_dataset  # noqa: E402
from src.config import MODELS_DIR, PROCESSED_DIR, ROOT  # noqa: E402
from src.inference import MANIFEST, Predictor  # noqa: E402
from src.models import gradient_boosting  # noqa: E402


def main():
    build_dataset()
    features = pd.read_csv(PROCESSED_DIR / "X_fit.csv", index_col=0)
    labels = pd.read_csv(PROCESSED_DIR / "y_fit.csv", index_col=0).iloc[:, 0]
    if not MANIFEST.is_file():
        reports = ROOT / "reports"
        result = json.loads((reports / "test_result.json").read_text())
        name = result["model"]
        reserved = pd.read_csv(reports / "arbitration.csv", index_col=0).loc[name]
        model = gradient_boosting(max_depth=8, learning_rate=0.10, n_trees=300)
        model.fit(features, labels)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODELS_DIR / "gradient_boosting.joblib")
        manifest = {
            "model": name,
            "threshold": result["threshold"],
            "columns": list(features.columns),
            "deciding_criterion": "Lower dispersion in repeated cross-validation; "
                                  "the reserved-set difference was below the margin.",
            "fitted_on": "48 000 fitting rows",
            "reserved_cost": float(reserved["cost"]),
            "reserved_recall": float(reserved["recall"]),
            "reserved_missed": int(reserved["FN"]),
            "reserved_false_alarms": int(reserved["FP"]),
        }
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    predictor = Predictor.load()
    print(f"Demo ready: {predictor.name}, {len(predictor.raw_columns)} raw inputs, "
          f"threshold {predictor.threshold:.10g}")
    print("To compare this build with the recorded predictions, run scripts/check_port.py.")


if __name__ == "__main__":
    main()
