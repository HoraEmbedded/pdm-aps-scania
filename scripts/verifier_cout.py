"""Verify the cost function before any use. Run from the project root."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from src.config import SEUIL_BAYES  # noqa: E402
from src.cout import (couts_naifs, cout_scania, depondere,  # noqa: E402
                      meilleur_seuil, seuil_bayes_pondere)

# --- Test 1 : reconstituer le résultat publié du vainqueur IDA 2016 --------
y_v = np.r_[np.ones(375, int), np.zeros(15625, int)]
y_p = np.r_[np.ones(366, int), np.zeros(9, int),
            np.ones(542, int), np.zeros(15083, int)]
assert cout_scania(y_v, y_p) == 9920
print("Test 1, vainqueur IDA 2016 (542 FP, 9 FN) :", cout_scania(y_v, y_p))

# --- Test 2 et 3 : les deux règles naïves sur le jeu de test ---------------
naifs = couts_naifs(y_v)
assert naifs["toujours_sain"] == 187_500
assert naifs["toujours_panne"] == 156_250
print("Test 2, toujours sain sur le test  :", naifs["toujours_sain"])
print("Test 3, toujours panne sur le test :", naifs["toujours_panne"])

# --- Test 4 : cas séparable, vérifie l'inégalité >= -----------------------
s, c = meilleur_seuil([0, 0, 1, 1], [0.01, 0.02, 0.60, 0.90])
assert c == 0 and abs(s - 0.60) < 1e-9
print(f"Test 4, cas séparable : seuil {s:.2f}, coût {c}")

# --- Test 5 : le seuil de Bayes tombe exactement sur 0,5 après pondération -
assert abs(seuil_bayes_pondere() - 0.5) < 1e-12
assert abs(depondere(0.5) - SEUIL_BAYES) < 1e-12
print(f"Test 5, seuil de Bayes pondéré : {seuil_bayes_pondere():.15f}")

# --- Test 6 : la version vectorisée égale la version naïve ----------------
rng = np.random.default_rng(0)
for _ in range(200):
    n = int(rng.integers(50, 400))
    y = (rng.random(n) < 0.02).astype(int)
    p = np.round(rng.random(n), 3)
    _, c_vect = meilleur_seuil(y, p)
    c_naif = min(cout_scania(y, (p >= s).astype(int)) for s in np.unique(p))
    assert c_vect <= c_naif, (c_vect, c_naif)
print("Test 6, vectorisée <= boucle naïve sur 200 tirages : OK")

print("\nLes six tests passent.")
