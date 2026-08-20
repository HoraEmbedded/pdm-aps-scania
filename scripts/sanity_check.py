"""S1 sanity check: does the dataset match what the specification claims?

Run from the project root:  ./.venv/bin/python scripts/sanity_check.py
Writes a text report in reports/s1_sanity_check.txt so the result can be
quoted in the final report and shown to the supervisor.
"""

import sys
from pathlib import Path

# Make the project root importable when the script is run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from src.config import REPORTS_DIR, TARGET  # noqa: E402
from src.data.load_aps import load_aps, split_xy  # noqa: E402
from src.evaluation.cost import baseline_costs, optimal_threshold  # noqa: E402
from src.utils.seeds import set_seed  # noqa: E402

lines = []


def log(message: str = "") -> None:
    print(message)
    lines.append(message)


def describe(frame, name: str) -> None:
    features, target = split_xy(frame)
    n_rows, n_cols = frame.shape
    positives = int(target.sum())

    log(f"--- {name} ---")
    log(f"Lignes                 : {n_rows}")
    log(f"Colonnes (dont cible)  : {n_cols}")
    log(f"Classe positive        : {positives} ({positives / n_rows:.2%})")
    log(f"Classe negative        : {n_rows - positives}")

    missing_ratio = features.isna().mean()
    log(
        f"Valeurs manquantes     : {features.isna().sum().sum()} "
        f"({features.isna().to_numpy().mean():.2%} des cellules)"
    )
    log(f"Colonnes > 50% de NaN  : {(missing_ratio > 0.5).sum()}")
    log(f"Colonnes sans NaN      : {(missing_ratio == 0).sum()}")
    log("Top 5 colonnes les plus trouees :")
    for col, ratio in missing_ratio.sort_values(ascending=False).head(5).items():
        log(f"    {col:<10} {ratio:.1%}")
    log(
        f"Colonnes constantes    : {(features.nunique(dropna=True) <= 1).sum()}"
    )
    log("")


def main() -> None:
    set_seed()
    log("SANITY CHECK S1 - APS Failure at Scania Trucks")
    log("=" * 60)

    train = load_aps("train")
    test = load_aps("test")

    describe(train, "TRAIN")
    describe(test, "TEST")

    log("--- Coherence des schemas ---")
    same_columns = list(train.columns) == list(test.columns)
    log(f"Memes colonnes train/test : {same_columns}")
    log(
        f"Cible                     : '{TARGET}' encodee en {sorted(train[TARGET].unique())}"
    )
    log("")

    log("--- Metrique de cout Scania ---")
    base = baseline_costs(test[TARGET])
    log(f"Regle naive 'ne rien signaler' : {base['always_negative']:>8} unites")
    log(f"Regle naive 'tout inspecter'   : {base['always_positive']:>8} unites")
    log(f"Reference a battre             : {min(base.values()):>8} unites")
    log(f"Seuil de decision theorique    : {optimal_threshold():.4f}")
    log("")
    log("[OK] Sanity check termine.")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "s1_sanity_check.txt").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(f"\nRapport ecrit dans {REPORTS_DIR / 's1_sanity_check.txt'}")


if __name__ == "__main__":
    main()
