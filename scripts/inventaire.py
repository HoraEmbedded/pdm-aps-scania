"""Repository inventory: what exists, what is missing, and the key figures.

Run at any time to know where the project stands:
    ./.venv/bin/python scripts/inventaire.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

RACINE = Path(__file__).resolve().parents[1]

# Each entry: path, what it is, which step produced it
ATTENDUS = [
    ("src/config.py",            "Constantes, chemins, matrice de coût",      "Migration"),
    ("src/graines.py",           "Graine aléatoire globale",                  "S1"),
    ("src/cout.py",              "cout_scania, meilleur_seuil, dépondération","4.1"),
    ("src/donnees.py",           "Chargement et découpage stratifié",         "3.2"),
    ("src/absences.py",          "Détection des groupes, profondeur, flags",  "3.1-3.3"),
    ("src/preparation.py",       "Imputation différenciée et normalisation",  "3.5-3.6"),
    ("src/evaluation.py",        "Protocole de validation croisée",           "4.2"),
    ("src/modeles.py",           "Les cinq modèles du benchmark",             "4.3"),
    ("scripts/download_data.sh", "Téléchargement du jeu Scania",              "S1"),
    ("scripts/verifier_cout.py", "Les six tests de la fonction de coût",      "4.1"),
    ("scripts/preparer.py",      "Rejoue toute la chaîne de préparation",     "3.6"),
    ("data/raw/aps_failure_training_set.csv", "Fichier brut d'entraînement",  "S1"),
    ("data/raw/aps_failure_test_set.csv",     "Fichier brut de test, scellé", "S1"),
    ("data/processed/X_app_final.csv",  "48000 x 180, apprentissage préparé", "3.6"),
    ("data/processed/X_val_final.csv",  "12000 x 180, validation préparée",   "3.6"),
    ("data/processed/y_app.csv",        "Étiquettes d'apprentissage",         "3.6"),
    ("data/processed/y_val.csv",        "Étiquettes de validation",           "3.6"),
    ("data/processed/extracteur_absences.joblib", "Objet rejouable D-09",     "3.6"),
    ("data/processed/preparateur.joblib",         "Objet rejouable D-10",     "3.6"),
    ("docs/D2_note_etat_de_lart.md",    "Livrable D2, état de l'art",         "S2"),
    ("docs/protocole_evaluation.md",    "Protocole figé",                     "4.2"),
    ("docs/JOURNAL.md",                 "Journal de bord chronologique",      "continu"),
    ("docs/CARTE.md",                   "Carte du dépôt",                     "Reprise"),
    ("notebooks/01_exploration.ipynb",  "Carnet d'analyse des données",       "3.x"),
    ("notebooks/02_benchmark.ipynb",    "Carnet de comparaison des modèles",  "4.x"),
    ("reports/benchmark.csv",           "Tableau comparatif des modèles",     "4.x"),
]


def main() -> None:
    print("=" * 78)
    print("  INVENTAIRE DU DEPOT")
    print("=" * 78)

    manquants = []
    for chemin, role, etape in ATTENDUS:
        existe = (RACINE / chemin).exists()
        marque = "OK " if existe else "-- "
        if not existe:
            manquants.append(chemin)
        print(f"[{marque}] {chemin:<44} {etape:<10} {role}")

    print("\n" + "-" * 78)
    print(f"Présents : {len(ATTENDUS) - len(manquants)} / {len(ATTENDUS)}")
    if manquants:
        print("Manquants :")
        for m in manquants:
            print(f"   {m}")

    # --- Chiffres de contrôle, si les données préparées existent ----------
    prepare = RACINE / "data" / "processed" / "X_app_final.csv"
    if prepare.exists():
        import pandas as pd
        X = pd.read_csv(prepare, index_col=0)
        y = pd.read_csv(RACINE / "data/processed/y_app.csv", index_col=0).squeeze()
        print("\n" + "-" * 78)
        print("CHIFFRES DE CONTROLE")
        print(f"  Apprentissage      : {X.shape[0]} x {X.shape[1]}")
        print(f"  Pannes             : {int(y.sum())} ({y.mean():.4%})")
        print(f"  Somme de contrôle  : {X.values.sum():,.2f}")
        print(f"  Cases vides        : {int(X.isna().sum().sum())}")
        construites = [c for c in X.columns
                       if c == "profondeur_g1" or c.startswith("absent_sb")]
        print(f"  Variables d'absence: {len(construites)}")

    # --- Modèles sérialisés ----------------------------------------------
    modeles = sorted((RACINE / "models").glob("*")) if (RACINE / "models").exists() else []
    modeles = [m for m in modeles if m.name != ".gitkeep"]
    print("\n" + "-" * 78)
    print(f"MODELES SERIALISES : {len(modeles)}")
    for m in modeles:
        print(f"   {m.name}  ({m.stat().st_size / 1024:.0f} Ko)")

    print("\n" + "=" * 78)


if __name__ == "__main__":
    main()
