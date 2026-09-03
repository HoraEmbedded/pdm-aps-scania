"""Check that a fresh clone can reproduce the project's key figures.

Run after following the README on a clean machine. Any failure here means the
repository does not satisfy the reproducibility criterion. Exits non-zero, so
it can be automated.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

checks, failures = [], 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global failures
    status = "ok   " if condition else "FAIL "
    checks.append(f"[{status}] {label}" + (f" -> {detail}" if detail else ""))
    if not condition:
        failures += 1


def main() -> None:
    # --- environment -----------------------------------------------------
    import numpy, pandas, sklearn  # noqa: E402
    check("python 3.10 or later", sys.version_info >= (3, 10),
          f"{sys.version_info.major}.{sys.version_info.minor}")
    check("numpy below 2.0", numpy.__version__.startswith("1."),
          numpy.__version__)
    check("pandas present", True, pandas.__version__)
    check("scikit-learn present", True, sklearn.__version__)

    # --- business metric, no data needed ---------------------------------
    from src.config import BAYES_THRESHOLD, COST_FN, COST_FP
    from src.cost import total_cost, weighted_bayes_threshold
    check("Bayes threshold equals 10/510",
          abs(BAYES_THRESHOLD - COST_FP / (COST_FP + COST_FN)) < 1e-12,
          f"{BAYES_THRESHOLD:.6f}")
    check("weighted Bayes threshold equals 0.5",
          abs(weighted_bayes_threshold() - 0.5) < 1e-12)
    check("a missed failure costs 500", total_cost([1, 0], [0, 0]) == 500)
    check("a false alarm costs 10", total_cost([0, 0], [1, 0]) == 10)
    check("the 2016 winner reconstructs to 9920",
          total_cost([1] * 375 + [0] * 15625,
                     [1] * 366 + [0] * 9 + [1] * 542 + [0] * 15083) == 9920)

    # --- raw data --------------------------------------------------------
    from src.config import TEST_FILE, TRAIN_FILE
    check("training file present", TRAIN_FILE.exists())
    check("test file present", TEST_FILE.exists())

    if TRAIN_FILE.exists():
        from src.data import load
        from src.missingness import detect_groups, nesting_report
        train = load("train")
        check("60 000 training rows", len(train) == 60000, str(len(train)))
        check("171 columns", train.shape[1] == 171, str(train.shape[1]))
        check("1 000 positives", int(train["class"].sum()) == 1000,
              str(int(train["class"].sum())))

        from src.data import train_validation_split
        X_fit, _, y_fit, _ = train_validation_split()
        groups = detect_groups(X_fit, y_fit)
        check("8 columns in group 1", len(groups["group1"]) == 8,
              str(len(groups["group1"])))
        check("56 columns in group 2", len(groups["group2"]) == 56,
              str(len(groups["group2"])))
        nesting = nesting_report(X_fit, groups["group1"])
        check("group 1 nests perfectly", nesting["nested_share"] == 1.0,
              f"{nesting['nested_share']:.4f}")

    # --- prepared data ---------------------------------------------------
    from src.config import PROCESSED_DIR
    prepared = PROCESSED_DIR / "X_fit.csv"
    check("prepared table present", prepared.exists())
    if prepared.exists():
        import pandas as pd
        X = pd.read_csv(prepared, index_col=0)
        check("48 000 by 180", X.shape == (48000, 180), str(X.shape))
        check("no empty cell", int(X.isna().sum().sum()) == 0)
        check("checksum 313 696", abs(X.values.sum() - 313696.0) < 1.0,
              f"{X.values.sum():,.2f}")

    # --- inference artefact ----------------------------------------------
    from src.config import MODELS_DIR
    manifest = MODELS_DIR / "final_model.json"
    check("final model manifest present", manifest.exists())
    if manifest.exists():
        try:
            from src.inference import Predictor
            predictor = Predictor.load()
            check("predictor loads", True, predictor.name)
        except Exception as error:
            check("predictor loads", False, str(error)[:70])

    print("\n".join(checks))
    print(f"\n{len(checks) - failures} of {len(checks)} checks passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
