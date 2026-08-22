"""Replay the full preparation chain and check it against known figures.

Run: ./.venv/bin/python scripts/preparer.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src.absences import (ExtracteurAbsences, detecte_groupes,  # noqa: E402
                          test_emboitement)
from src.config import PREPARE  # noqa: E402
from src.cout import couts_naifs  # noqa: E402
from src.donnees import charge, decoupe  # noqa: E402
from src.graines import set_seed  # noqa: E402
from src.preparation import Preparateur, sauvegarde  # noqa: E402


def main() -> None:
    set_seed()

    # --- 1. Découpage, AVANT toute préparation --------------------------
    X_app, X_val, y_app, y_val = decoupe()
    print(f"Apprentissage : {X_app.shape}, {int(y_app.sum())} pannes "
          f"({y_app.mean():.4%})")
    print(f"Validation    : {X_val.shape}, {int(y_val.sum())} pannes "
          f"({y_val.mean():.4%})")
    assert X_app.shape == (48000, 170) and X_val.shape == (12000, 170)
    assert int(y_app.sum()) == 800 and int(y_val.sum()) == 200

    # --- 2. Détection des groupes, sur l'apprentissage seul --------------
    g = detecte_groupes(X_app, y_app)
    print(f"\nGroupe 1 : {len(g['groupe1'])} colonnes -> {g['groupe1']}")
    print(f"Groupe 2 : {len(g['groupe2'])} colonnes")
    print(f"Muettes  : {len(g['muettes'])} colonnes")
    assert len(g["groupe1"]) + len(g["groupe2"]) + len(g["muettes"]) == 170

    # --- 3. L'emboîtement du groupe 1 ------------------------------------
    emb = test_emboitement(X_app, g["groupe1"])
    print(f"\nGroupe 1 : {emb['n_motifs']} motifs sur {emb['n_possibles']}, "
          f"{emb['part_emboitee']:.2%} de lignes emboîtées")

    # --- 4. Extraction des variables d'absence ---------------------------
    extracteur = ExtracteurAbsences().fit(X_app, y_app)
    print(f"\nSous-blocs du groupe 2 : {len(extracteur.sous_blocs_)}")
    for taux, membres in sorted(extracteur.sous_blocs_.items()):
        print(f"  palier {taux:.3f} : {len(membres):>2} colonnes")

    X_app_v1 = extracteur.transform(X_app)
    X_val_v1 = extracteur.transform(X_val)
    print(f"\nAprès extraction : {X_app_v1.shape} et {X_val_v1.shape}")

    # --- 5. Imputation et normalisation ----------------------------------
    non_normalisees = ["profondeur_g1"] + extracteur.noms_indicatrices_
    prep = Preparateur(groupe1=extracteur.groupe1_,
                       non_normalisees=non_normalisees).fit(X_app_v1)

    X_app_final = prep.transform(X_app_v1)
    X_val_final = prep.transform(X_val_v1)
    assert X_app_final.isna().sum().sum() == 0
    assert X_val_final.isna().sum().sum() == 0

    # --- 6. Les preuves d'absence de fuite -------------------------------
    med_globale = pd.concat([X_app_v1, X_val_v1])[prep.autres_].median()
    n_diff = int((prep.medianes_ != med_globale).sum())
    print(f"\nMédianes différentes de la médiane globale : {n_diff} colonnes")
    print("  (si c'était 0, la validation aurait participé au calcul)")

    a_norm = prep.a_normaliser_
    print(f"\nApprentissage : moyenne {X_app_final[a_norm].mean().mean():.2e}, "
          f"écart type {X_app_final[a_norm].std().mean():.4f}")
    print(f"Validation    : moyenne {X_val_final[a_norm].mean().mean():.4f}, "
          f"écart type {X_val_final[a_norm].std().mean():.4f}")
    print("  (l'écart sur la validation EST la preuve : à 0 et 1 exactement,")
    print("   il y aurait fuite)")

    # --- 7. Diagnostics ---------------------------------------------------
    constantes = [c for c in a_norm if X_app_final[c].std() == 0]
    print(f"\nColonnes constantes : {constantes}")
    for c in constantes:
        avant = X_app_v1[c].dropna()
        print(f"  {c} : {avant.nunique()} valeur(s) avant imputation, "
              f"valeur {avant.iloc[0]:,.0f}")

    print("\nRègles naïves sur la validation :", couts_naifs(y_val))

    # --- 8. Sauvegarde ----------------------------------------------------
    PREPARE.mkdir(parents=True, exist_ok=True)
    X_app_final.to_csv(PREPARE / "X_app_final.csv", index=True)
    X_val_final.to_csv(PREPARE / "X_val_final.csv", index=True)
    y_app.to_csv(PREPARE / "y_app.csv", index=True)
    y_val.to_csv(PREPARE / "y_val.csv", index=True)
    sauvegarde(extracteur, "extracteur_absences.joblib")
    sauvegarde(prep, "preparateur.joblib")

    print(f"\nDimensions finales : {X_app_final.shape} et {X_val_final.shape}")
    print(f"Somme de contrôle  : {X_app_final.values.sum():,.2f}")


if __name__ == "__main__":
    main()
