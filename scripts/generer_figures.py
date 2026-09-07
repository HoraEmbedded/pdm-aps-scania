#!/usr/bin/env python3
"""Produit les onze figures manquantes ou perimees du rapport.

A copier n'importe ou dans le depot pdm-aps-scania (racine ou scripts/),
puis :

    ./.venv/bin/python generer_figures.py
    ./.venv/bin/python generer_figures.py --sortie /chemin/vers/rapport/figures
    ./.venv/bin/python generer_figures.py --seulement 09_ablation

La racine du depot est retrouvee en remontant les repertoires parents jusqu'a
celui qui contient a la fois reports/ et src/ ; elle est aussi ajoutee au
chemin d'import Python pour que 05_absence_par_classe trouve le module src.

Dix des onze figures ne lisent que des fichiers de reports/ : aucun
entrainement, quelques secondes. La onzieme, 05_absence_par_classe, relit le
fichier brut d'apprentissage et prend une dizaine de secondes.

Une figure dont le fichier d'entree manque est signalee et sautee : le script
ne s'interrompt pas.
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def _trouver_racine():
    """Remonte les parents jusqu'au repertoire qui contient reports/ et src/."""
    depart = Path(__file__).resolve().parent
    for candidat in (depart, *depart.parents):
        if (candidat / "reports").is_dir() and (candidat / "src").is_dir():
            return candidat
    for candidat in (depart, *depart.parents):
        if (candidat / "reports").is_dir():
            return candidat
    return depart


RACINE = _trouver_racine()
REPORTS = RACINE / "reports"
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

# ------------------------------------------------------------------ style ----
# Regles de PLAN_FIGURES.md : lisible en niveaux de gris, pas de couleur
# porteuse d'information, distinction par trait, marqueur ou hachure.
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.grid": True,
    "grid.color": "0.85",
    "grid.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "image.cmap": "Greys",
})
GRIS = ["0.15", "0.40", "0.60", "0.75"]
TRAITS = ["-", "--", "-.", ":"]
HACHURES = ["", "///", "...", "xxx"]

COUT_FP, COUT_FN = 10, 500
MARGE_DEPARTAGE = 2000


def _enregistrer(fig, nom, sortie):
    chemin = sortie / f"{nom}.png"
    fig.savefig(chemin)
    plt.close(fig)
    print(f"  ecrit  {chemin}")


def _lire_csv(nom, **kwargs):
    chemin = REPORTS / nom
    if not chemin.exists():
        raise FileNotFoundError(chemin)
    return pd.read_csv(chemin, **kwargs)


# ================================================== chapitre 2, figure 2.1 ===
def regles_constantes(sortie):
    """Cout des deux regles constantes selon le taux de positifs du fichier."""
    n = 16000
    taux = np.linspace(0, 0.06, 400)
    rien = taux * n * COUT_FN
    tout = (1 - taux) * n * COUT_FP
    equilibre = COUT_FP / (COUT_FP + COUT_FN)

    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    ax.plot(taux * 100, rien, color=GRIS[0], ls=TRAITS[0], lw=1.3,
            label="ne rien signaler")
    ax.plot(taux * 100, tout, color=GRIS[1], ls=TRAITS[1], lw=1.3,
            label="tout signaler")
    ax.axvline(equilibre * 100, color="0.65", ls=":", lw=1)
    ax.annotate(f"taux d'equilibre {equilibre * 100:.2f} %",
                xy=(equilibre * 100 + 0.12, 0.72 * rien.max()), fontsize=8)

    for t, nom in [(0.0167, "donnees reservees"), (0.0234, "test officiel")]:
        y = min(t * n * COUT_FN, (1 - t) * n * COUT_FP)
        ax.plot(t * 100, y, marker="o", color=GRIS[0], ms=5)
        ax.annotate(nom, xy=(t * 100 + 0.1, y * 1.06), fontsize=8)

    ax.set_xlabel("taux de pannes du circuit d'air comprime, en pour cent")
    ax.set_ylabel("cout total, base 16 000 vehicules")
    ax.legend(frameon=False)
    _enregistrer(fig, "02_regles_constantes", sortie)


# ================================================== chapitre 3, figure 3.1 ===
def panorama_publie(sortie):
    """Les quinze resultats connus sur le jeu de test officiel."""
    posterieurs = [(2023, 69270), (2020, 31570), (2020, 20190), (2022, 16290),
                   (2019, 12210), (2018, 10140), (2023, 9080), (2019, 6050),
                   (2019, 5550), (2024, 4000), (2024, 3440)]
    concours = [(2016, 9920), (2016, 10900), (2016, 11480)]

    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    for a, c in concours:
        ax.plot(a, c, marker="s", color=GRIS[0], ms=6.5, ls="none")
    for a, c in posterieurs:
        ax.plot(a, c, marker="o", mfc="none", mec=GRIS[0], ms=6.5, ls="none")
    ax.plot(2026, 11370, marker="D", color=GRIS[0], ms=8, ls="none")
    ax.annotate("travail present", xy=(2026, 11370), xytext=(2021.0, 17000),
                fontsize=8,
                arrowprops=dict(arrowstyle="-", color="0.5", lw=0.7))

    ax.set_yscale("log")
    ax.set_xlabel("annee de publication")
    ax.set_ylabel("cout sur le jeu de test officiel")
    ax.plot([], [], marker="s", color=GRIS[0], ls="none",
            label="concours 2016, a l'aveugle")
    ax.plot([], [], marker="o", mfc="none", mec=GRIS[0], ls="none",
            label="posterieurs, etiquettes publiques")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    _enregistrer(fig, "03_panorama_publie", sortie)


# ================================================== chapitre 5, figure 5.1 ===
def absence_par_classe(sortie):
    """Taux d'absence par colonne et par classe, sur les 48 000 lignes.

    Seule figure du script qui relit le fichier brut. Le calcul porte sur la
    partie d'apprentissage seule, jamais sur les 60 000 lignes : c'est la
    correction de protocole consignee au chapitre 7.
    """
    sys.path.insert(0, str(RACINE))
    from src.data import train_validation_split
    from src.missingness import per_class_missing_rate, detect_groups

    X_fit, _, y_fit, _ = train_validation_split()
    taux = per_class_missing_rate(X_fit, y_fit)
    taux = taux.assign(ecart=taux["rate_other"] - taux["rate_aps"])
    taux = taux.sort_values("ecart", ascending=False)

    groupes = detect_groups(X_fit, y_fit)
    n1, n2 = len(groupes["group1"]), len(groupes["group2"])
    total = len(taux)

    x = np.arange(total)
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.axvspan(-0.5, n1 - 0.5, color="0.90", zorder=0)
    ax.axvspan(total - n2 - 0.5, total - 0.5, color="0.90", zorder=0)
    ax.plot(x, taux["rate_other"] * 100, color=GRIS[0], ls=TRAITS[0], lw=1.2,
            label="pannes d'un autre organe")
    ax.plot(x, taux["rate_aps"] * 100, color=GRIS[2], ls=TRAITS[1], lw=1.2,
            label="pannes du circuit d'air")

    haut = 96
    ax.annotate(f"premier groupe\n{n1} colonnes", xy=(n1 / 2, haut),
                fontsize=8, ha="center", va="top")
    ax.annotate(f"second groupe\n{n2} colonnes", xy=(total - n2 / 2, haut),
                fontsize=8, ha="center", va="top")

    ax.set_xlim(-0.5, total - 0.5)
    ax.set_ylim(0, 100)
    ax.set_xlabel("colonnes, triees par ecart de taux d'absence decroissant")
    ax.set_ylabel("taux d'absence, en pour cent")
    ax.legend(frameon=False, fontsize=8, loc="center right")
    _enregistrer(fig, "05_absence_par_classe", sortie)
    print(f"     controle : {n1} et {n2} colonnes retenues, attendu 8 et 56")


# ================================================== chapitre 8, figure 8.1 ===
def classement_modeles(sortie):
    """Cout des cinq modeles avec la dispersion entre plis."""
    frame = _lire_csv("benchmark.csv", index_col=0)
    frame = frame[frame.index != "constant control"].sort_values("cost")

    noms = {
        "Gradient boosting 8/0.1": "gradient boosting",
        "Random forest 300/None/1": "foret aleatoire",
        "Perceptron (64, 32)": "perceptron (64, 32)",
        "Linear SVM C=0.001": "SVM lineaire",
        "Logistic regression C=0.001": "regression logistique",
    }
    etiquettes = [noms.get(i, i) for i in frame.index]

    y = np.arange(len(frame))[::-1]
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.barh(y, frame["cost"], xerr=frame["dispersion"], height=0.62,
            color="0.78", edgecolor=GRIS[0], linewidth=0.8,
            error_kw=dict(ecolor=GRIS[0], capsize=3, lw=0.9))
    for yi, cout in zip(y, frame["cost"]):
        ax.text(cout + 120, yi, f"{cout:,.0f}".replace(",", " "),
                va="center", fontsize=8)

    ax.set_yticks(y, etiquettes)
    ax.set_xlabel("cout total, moyenne sur cinq plis, dispersion entre plis")
    ax.set_xlim(0, frame["cost"].max() * 1.28)
    ax.grid(axis="y", visible=False)
    _enregistrer(fig, "08_classement_modeles", sortie)


# ================================================== chapitre 8, figure 8.5 ===
def seuil_en_echantillon(sortie, en_echantillon=41050, hors_echantillon=6714):
    """Effet du reglage du seuil en echantillon, sur la foret aleatoire.

    Les deux valeurs par defaut sont la paire mesuree au moment de la
    correction, celle que le rapport cite. Les remesurer demande de rejouer
    evaluate(..., out_of_sample_threshold=False) sur les donnees preparees,
    ce que fait le carnet 02 ; le rapport indique explicitement que c'est la
    paire mesuree qui est rapportee, non une recomposition.
    """
    tout_signaler = 9440 * COUT_FP  # regle constante a l'echelle d'un pli

    x = np.arange(2)
    fig, ax = plt.subplots(figsize=(4.8, 3.3))
    ax.bar(x, [en_echantillon, hors_echantillon], width=0.52,
           color=["0.80", "0.42"], edgecolor=GRIS[0], linewidth=0.9,
           hatch=[HACHURES[1], HACHURES[0]])
    ax.axhline(tout_signaler, color=GRIS[0], ls=TRAITS[2], lw=1.1)
    ax.annotate(f"regle << tout signaler >> a l'echelle d'un pli, "
                f"{tout_signaler:,.0f}".replace(",", " "),
                xy=(-0.42, tout_signaler * 1.12), fontsize=7.5)

    facteur = en_echantillon / hors_echantillon
    ax.annotate(f"facteur {facteur:.1f}", xy=(0.5, en_echantillon * 0.5),
                ha="center", fontsize=9)

    ax.set_yscale("log")
    ax.set_xticks(x, ["seuil regle\nen echantillon",
                      "seuil regle\nhors echantillon"])
    ax.set_ylabel("cout total, foret aleatoire")
    _enregistrer(fig, "08_seuil_en_echantillon", sortie)


# ---------------------------------------------- lecture des 30 mesures -------
def _conditions_r6():
    frame = _lire_csv("runs/ablation_r6.csv")
    return frame.groupby("model")["cost"].agg(["mean", "std", "count"])


def _planchers():
    """Plancher de detection par comparaison, depuis paired_comparisons.csv."""
    try:
        frame = _lire_csv("paired_comparisons.csv")
    except FileNotFoundError:
        return {}
    return dict(zip(frame["comparison"], frame["detection_floor"]))


# ================================================== chapitre 9, figure 9.1 ===
def ablation(sortie):
    """Cout des trois traitements de la manquance, sur 30 mesures."""
    stats = _conditions_r6()
    ordre = ["V0", "V1", "V2"]
    etiquettes = ["V0\n142 colonnes", "V1, retenue\n180 colonnes",
                  "V2\n234 colonnes"]
    moyennes = [stats.loc[c, "mean"] for c in ordre]
    erreurs = [stats.loc[c, "std"] / np.sqrt(stats.loc[c, "count"])
               for c in ordre]

    planchers = _planchers()
    plancher = planchers.get("V1 vs V0", 267)
    base = min(moyennes)

    x = np.arange(len(ordre))
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.bar(x, moyennes, yerr=erreurs, width=0.5, color="0.78",
           edgecolor=GRIS[0], linewidth=0.9,
           error_kw=dict(ecolor=GRIS[0], capsize=4, lw=0.9))
    ax.axhspan(base - plancher, base + plancher, color="0.92", zorder=0)
    ax.annotate(f"plancher de detection, +/- {plancher:.0f} unites autour de V0",
                xy=(-0.44, base + plancher * 1.15), fontsize=7.5)

    for xi, m in zip(x, moyennes):
        ax.text(xi, m + erreurs[0] * 1.4, f"{m:,.0f}".replace(",", " "),
                ha="center", fontsize=8)

    ax.set_xticks(x, etiquettes)
    ax.set_ylim(base - plancher * 2.4, max(moyennes) + plancher * 2.0)
    ax.set_ylabel("cout total, moyenne sur 30 mesures appariees")
    _enregistrer(fig, "09_ablation", sortie)


# ================================================== chapitre 9, figure 9.2 ===
def plan_factoriel(sortie):
    """Les quatre conditions du plan : profondeur x indicatrices.

    Attention au nommage du depot : V1_no_counter retire les neuf
    indicatrices de sous-bloc, pas le compteur d'usage aa_000, qui est
    present dans les quatre conditions.
    """
    stats = _conditions_r6()
    conditions = [
        ("V1_base", "ni profondeur\nni indicatrices", 170),
        ("V1_no_counter", "profondeur\nseule", 171),
        ("V1_no_depth", "indicatrices\nseules", 179),
        ("V1", "les deux,\nsoit V1", 180),
    ]
    moyennes = [stats.loc[c, "mean"] for c, _, _ in conditions]
    erreurs = [stats.loc[c, "std"] / np.sqrt(stats.loc[c, "count"])
               for c, _, _ in conditions]
    planchers = _planchers()
    plancher = max(planchers.get("Profondeur avec compteur", 285),
                   planchers.get("Profondeur sans compteur", 242))

    x = np.arange(4)
    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    ax.bar(x, moyennes, yerr=erreurs, width=0.52,
           color=["0.88", "0.76", "0.62", "0.44"],
           edgecolor=GRIS[0], linewidth=0.9,
           error_kw=dict(ecolor=GRIS[0], capsize=4, lw=0.9))
    for xi, m in zip(x, moyennes):
        ax.text(xi, m + erreurs[0] * 1.5, f"{m:,.0f}".replace(",", " "),
                ha="center", fontsize=8)

    centre = np.mean(moyennes)
    ax.axhspan(centre - plancher, centre + plancher, color="0.93", zorder=0)
    ax.annotate(f"plancher de detection, +/- {plancher:.0f} unites",
                xy=(-0.46, centre + plancher * 1.1), fontsize=7.5)

    ax.set_xticks(x, [e for _, e, _ in conditions])
    ax.set_ylim(centre - plancher * 1.9, centre + plancher * 1.9)
    ax.set_ylabel("cout total, moyenne sur 30 mesures appariees")
    _enregistrer(fig, "09_plan_factoriel", sortie)


# ================================================== chapitre 9, figure 9.3 ===
def fonctions_perte(sortie):
    """Les quatre variantes d'objectif du perceptron, une partition.

    Aucune indication de dispersion : le rapport de variances entre A et D
    vaut 2,77 sur quatre degres de liberte, soit une probabilite de l'ordre
    de 0,34. L'observation n'est pas rapportable.
    """
    frame = _lire_csv("loss_functions.csv", index_col=0).sort_values("cost")
    noms = {
        "B, weighted cross-entropy": "B, entropie croisee\nponderee par les couts",
        "A, reference": "A, reference,\nretenue",
        "D, weighted focal loss": "D, focale\nponderee",
        "C, focal loss": "C, focale",
    }
    etiquettes = [noms.get(i, i) for i in frame.index]

    y = np.arange(len(frame))[::-1]
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    ax.barh(y, frame["cost"], height=0.58, color="0.78",
            edgecolor=GRIS[0], linewidth=0.9)
    for yi, cout in zip(y, frame["cost"]):
        ax.text(cout + 40, yi, f"{cout:,.0f}".replace(",", " "),
                va="center", fontsize=8)

    ax.set_yticks(y, etiquettes)
    ax.set_xlim(8000, frame["cost"].max() * 1.06)
    ax.set_xlabel("cout total, moyenne sur les cinq plis d'une partition")
    ax.grid(axis="y", visible=False)
    _enregistrer(fig, "09_fonctions_perte", sortie)


# ================================================= chapitre 10, figure 10.2 ==
def matrice_confusion(sortie):
    """Matrice de confusion sur le jeu de test, avec le cout de chaque case."""
    chemin = REPORTS / "test_result.json"
    if not chemin.exists():
        raise FileNotFoundError(chemin)
    r = json.loads(chemin.read_text(encoding="utf-8"))

    effectifs = np.array([[r["TN"], r["FP"]], [r["FN"], r["TP"]]])
    couts = np.array([[0, COUT_FP], [COUT_FN, 0]])
    contributions = effectifs * couts

    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    ax.imshow(np.log1p(contributions), cmap="Greys", vmin=0,
              vmax=np.log1p(contributions.max()) * 1.35)
    for i in range(2):
        for j in range(2):
            contribution = contributions[i, j]
            texte = f"{effectifs[i, j]:,}".replace(",", " ")
            if contribution:
                texte += f"\n{contribution:,} unites".replace(",", " ")
            else:
                texte += "\nsans cout"
            ax.text(j, i, texte, ha="center", va="center", fontsize=9,
                    color="white" if contribution > 5000 else "black")

    ax.set_xticks([0, 1], ["predit sain", "predit defaillant"])
    ax.set_yticks([0, 1], ["autre organe", "circuit d'air"])
    ax.set_title(f"cout total {r['cost']:,}".replace(",", " "), fontsize=9)
    ax.grid(False)
    _enregistrer(fig, "10_matrice_confusion", sortie)


# ================================================= chapitre 11, figure 11.4 ==
def latence(sortie):
    """Distribution du temps de notation d'un vehicule, sur 200 tirages."""
    t = _lire_csv("latency_single.csv")["latency_ms"].to_numpy()

    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    ax.hist(t, bins=24, color="0.78", edgecolor=GRIS[0], linewidth=0.6)
    for valeur, trait, etiquette in [
        (np.median(t), TRAITS[0], "mediane"),
        (np.percentile(t, 90), TRAITS[1], "neuvieme decile"),
    ]:
        ax.axvline(valeur, color=GRIS[0], ls=trait, lw=1.2,
                   label=f"{etiquette} : {valeur:.1f} ms")

    ax.set_xlabel("temps de notation d'un vehicule, en millisecondes")
    ax.set_ylabel("nombre de tirages")
    ax.legend(frameon=False, fontsize=8)
    _enregistrer(fig, "11_latence", sortie)
    print(f"     controle : mediane {np.median(t):.1f}, "
          f"d9 {np.percentile(t, 90):.1f}, "
          f"c95 {np.percentile(t, 95):.1f}, max {t.max():.1f}")


# ======================================================= annexe D, fig. A.2 ==
def grille_logistique(sortie):
    """La seule grille dont les resultats intermediaires sont conserves.

    Les quatre points de la grille enregistree sont pleins ; C = 0,001, qui
    lui est posterieur et hors grille, est creux et annote comme tel. C'est
    la distinction que PLAN_FIGURES.md demande de trancher.
    """
    C = [0.01, 0.1, 1.0, 10.0]
    cout = [9608, 10164, 10296, 10916]
    dispersion = [1428, 492, 193, 398]

    fig, ax = plt.subplots(figsize=(5.0, 3.1))
    ax.errorbar(C, cout, yerr=dispersion, fmt="o-", color=GRIS[0],
                ecolor="0.6", capsize=3, ms=5, lw=1.2,
                label="grille enregistree")
    ax.errorbar([0.001], [9596], yerr=[1222], fmt="o", mfc="none",
                mec=GRIS[0], ecolor="0.6", capsize=3, ms=6, lw=1.2,
                label="prolongement posterieur, retenu")
    ax.annotate("C = 0,001, hors grille initiale", xy=(0.001, 9596),
                xytext=(0.0016, 10450), fontsize=8,
                arrowprops=dict(arrowstyle="-", color="0.5", lw=0.7))

    ax.set_xscale("log")
    ax.set_xlabel("parametre de regularisation C")
    ax.set_ylabel("cout moyen sur cinq plis")
    ax.legend(frameon=False, fontsize=8)
    _enregistrer(fig, "A_grille_logistique", sortie)


# --------------------------------------------------------------- pilotage ----
FIGURES = {
    "02_regles_constantes": regles_constantes,
    "03_panorama_publie": panorama_publie,
    "05_absence_par_classe": absence_par_classe,
    "08_classement_modeles": classement_modeles,
    "08_seuil_en_echantillon": seuil_en_echantillon,
    "09_ablation": ablation,
    "09_plan_factoriel": plan_factoriel,
    "09_fonctions_perte": fonctions_perte,
    "10_matrice_confusion": matrice_confusion,
    "11_latence": latence,
    "A_grille_logistique": grille_logistique,
}


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--sortie", default=str(REPORTS / "report_figures"),
                           help="repertoire de destination des PNG")
    analyseur.add_argument("--seulement", action="append", default=None,
                           choices=sorted(FIGURES),
                           help="ne produire que cette figure, repetable")
    arguments = analyseur.parse_args()

    sortie = Path(arguments.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    print(f"racine du depot : {RACINE}")
    print(f"lecture des mesures : {REPORTS}\n")
    demandees = arguments.seulement or list(FIGURES)

    faites, sautees = 0, []
    for nom in demandees:
        print(f"{nom} :")
        try:
            FIGURES[nom](sortie)
            faites += 1
        except FileNotFoundError as absent:
            print(f"  saute, fichier d'entree absent : {absent}")
            sautees.append(nom)
        except Exception as erreur:            # noqa: BLE001
            print(f"  saute, erreur : {type(erreur).__name__} : {erreur}")
            sautees.append(nom)

    print(f"\n{faites} figure(s) ecrite(s) dans {sortie}")
    if sautees:
        print("sautees : " + ", ".join(sautees))
    return 1 if sautees else 0


if __name__ == "__main__":
    sys.exit(main())
