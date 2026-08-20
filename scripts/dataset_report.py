"""Produce the figures quoted in the state-of-the-art note (D2).

Run from the project root:  ./.venv/bin/python scripts/dataset_report.py
Writes reports/s2_dataset_report.txt
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import REPORTS_DIR, TARGET  # noqa: E402
from src.data.load_aps import load_aps, split_xy  # noqa: E402
from src.data.schema import histogram_groups, single_counters  # noqa: E402
from src.evaluation.cost import baseline_costs, optimal_threshold  # noqa: E402
from src.utils.seeds import set_seed  # noqa: E402

lines = []


def log(message: str = "") -> None:
    print(message)
    lines.append(message)


def main() -> None:
    set_seed()
    train = load_aps("train")
    test = load_aps("test")
    features, target = split_xy(train)

    log("RAPPORT DATASET POUR LA NOTE D2")
    log("=" * 60)

    # --- Volumetry ------------------------------------------------------
    log("\n[1] Volumetrie")
    log(f"Train : {train.shape[0]} lignes x {train.shape[1]} colonnes")
    log(f"Test  : {test.shape[0]} lignes x {test.shape[1]} colonnes")
    log(f"Positifs train : {int(target.sum())} ({target.mean():.2%})")
    log(f"Positifs test  : {int(test[TARGET].sum())} ({test[TARGET].mean():.2%})")
    log(f"Ratio de desequilibre : 1 pour {int((1 - target.mean()) / target.mean())}")

    # --- Structural analysis of the feature space -----------------------
    log("\n[2] Structure de l'espace de variables")
    hists = histogram_groups(features.columns)
    counters = single_counters(features.columns)
    log(f"Groupes d'histogrammes detectes : {len(hists)}")
    log(f"Colonnes appartenant a un histogramme : {sum(len(c) for c in hists.values())}")
    log(f"Compteurs isoles : {len(counters)}")
    log("Prefixes des histogrammes : " + ", ".join(sorted(hists)))
    
    # --- Missing values -------------------------------------------------
    log("\n[3] Valeurs manquantes")
    ratio = features.isna().mean()
    log(f"Taux global : {features.isna().to_numpy().mean():.2%} des cellules")
    log(f"Colonnes sans aucune valeur manquante : {(ratio == 0).sum()}")
    log(f"Colonnes > 20% manquantes : {(ratio > 0.20).sum()}")
    log(f"Colonnes > 50% manquantes : {(ratio > 0.50).sum()}")
    log(f"Colonnes > 70% manquantes : {(ratio > 0.70).sum()}")
    log("Les 5 plus trouees :")
    for col, value in ratio.sort_values(ascending=False).head(5).items():
        log(f"    {col:<10} {value:.1%}")

    # Do histogram columns suffer more from missingness than counters?
    hist_cols = [c for cols in hists.values() for c in cols]
    log(f"\nTaux moyen de NaN, colonnes d'histogrammes : "
        f"{ratio[hist_cols].mean():.2%}")
    log(f"Taux moyen de NaN, compteurs isoles         : "
        f"{ratio[counters].mean():.2%}")

    # --- Business metric ------------------------------------------------
    log("\n[4] Metrique de cout Scania sur le jeu de test")
    base = baseline_costs(test[TARGET])
    log(f"Ne rien signaler : {base['always_negative']}")
    log(f"Tout inspecter   : {base['always_positive']}")
    log(f"Reference a battre : {min(base.values())}")
    log(f"Seuil theorique optimal : {optimal_threshold():.4f}")
    log(f"Repere challenge IDA 2016 (1er) : 9920")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "s2_dataset_report.txt").write_text("\n".join(lines),
                                                       encoding="utf-8")
    print(f"\nEcrit dans {REPORTS_DIR / 's2_dataset_report.txt'}")


if __name__ == "__main__":
    main()
