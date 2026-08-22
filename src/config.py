"""Central configuration: paths, seeds, cost matrix, protocol constants.

Every module imports from here. No hard-coded value anywhere else.
"""

from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

# --- Chemins ---------------------------------------------------------------
BRUT = RACINE / "data" / "raw"
PREPARE = RACINE / "data" / "processed"
FIGURES = RACINE / "reports" / "figures"
MODELES = RACINE / "models"

FICHIER_TRAIN = BRUT / "aps_failure_training_set.csv"
FICHIER_TEST = BRUT / "aps_failure_test_set.csv"

# --- Reproductibilité ------------------------------------------------------
GRAINE = 42

# --- Matrice de coût Scania ------------------------------------------------
COUT_FP = 10       # inspection inutile à l'atelier
COUT_FN = 500      # panne non détectée

# Rapport de coût. C'est LUI qui fixe la pondération des classes (D-11),
# et non les fréquences observées qui donneraient 59:1.
RAPPORT_COUT = COUT_FN / COUT_FP                 # 50.0
PONDERATION = {0: 1, 1: RAPPORT_COUT}

# Seuil de Bayes sur une probabilité calibrée. Sert de DIAGNOSTIC, jamais de
# point de fonctionnement (D-11 §4).
SEUIL_BAYES = COUT_FP / (COUT_FP + COUT_FN)      # 0.019608

# --- Protocole d'évaluation (figé) ----------------------------------------
PART_VALIDATION = 0.20
N_PLIS = 5
N_PLIS_INTERNES = 3        # pour le réglage du seuil, correction 1

# --- Colonnes --------------------------------------------------------------
CIBLE = "class"
ETIQUETTE_POSITIVE = "pos"
JETON_ABSENT = "na"

# Seuil de sélection des colonnes informatives, écrit avant le calcul (D-09 §7).
SEUIL_ECART = 0.10
