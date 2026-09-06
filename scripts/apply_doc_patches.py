"""Apply the exact text corrections to the three long documents.

Full rewrites of evaluation_protocol.md, technical_decisions.md and
dataset_scania.md would discard whatever was edited in them since. These are
targeted replacements instead: each one asserts that the text it replaces is
present, so the script fails loudly rather than silently doing nothing.

Run from the project root:
    ./.venv/bin/python scripts/apply_doc_patches.py           # apply
    ./.venv/bin/python scripts/apply_doc_patches.py --check   # report only
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# file -> list of (old, new). An empty new deletes the passage.
PATCHES = {
    "docs/evaluation_protocol.md": [
        (
            "Somme de contrôle du tableau final : 313 695,00.",
            "Somme de contrôle du tableau final : 313 696,00, vérifiée par\n"
            "`scripts/verify.py` et par `tests/test_pipeline.py`.",
        ),
        (
            "## 4. Traitement du coût asymétrique\n\n\n\n- pondération",
            "## 4. Traitement du coût asymétrique\n\n"
            "Conformément à la décision D-11, le rapport de coût n'entre qu'une\n"
            "seule fois dans la chaîne, par deux composantes et deux seulement :\n\n"
            "- pondération",
        ),
        (
            "L'écart type n'est pas décoratif. Avec environ 900 unités de bruit sur la\n"
            "moyenne, **deux modèles séparés de moins de 2 000 unités ne sont pas\n"
            "départageables.** Cette marge est fixée avant toute mesure.",
            "L'écart type n'est pas décoratif. Avec environ 900 unités de bruit sur la\n"
            "moyenne, **deux modèles séparés de moins de 2 000 unités ne sont pas\n"
            "départageables sur cinq plis.** Cette marge est fixée avant toute mesure.\n\n"
            "Elle porte sur la comparaison à cinq plis. Deux modèles que cinq plis ne\n"
            "départagent pas peuvent l'être par la validation croisée répétée de la\n"
            "section 3, dont le plancher de détection est mesuré et non fixé : c'est ce\n"
            "qui s'est produit pour les deux premiers modèles du banc d'essai, séparés\n"
            "de 372 unités à cinq plis et de 396 unités pour un plancher de 354 sur\n"
            "trente mesures (`reports/finalists.csv`).",
        ),
        (
            "Aucune de ces trois corrections ne modifie une prescription du protocole. Toutes\n"
            "les trois précèdent les résultats rapportés dans `reports/`.",
            "Aucune de ces trois corrections ne modifie une prescription du protocole. Toutes\n"
            "les trois précèdent les résultats rapportés dans `reports/`.\n\n"
            "**9.4. Validation croisée répétée sur les comparaisons appariées.** Elles\n"
            "reposaient sur une partition unique, soit cinq mesures. Elles reposent\n"
            "désormais sur six partitions, soit trente mesures, ce qui divise l'erreur type\n"
            "par la racine de six. Les six verdicts sont inchangés, mais l'écart de la\n"
            "comparaison principale passe de moins 220 unités à plus 35, pour une erreur\n"
            "type ramenée de 329 à 131 : le premier chiffre était un artefact de la\n"
            "partition retenue. Script `scripts/paired_comparisons.py`, mesures dans\n"
            "`reports/runs/ablation_r6.csv`.\n\n"
            "## 10. Ouvertures des données réservées\n\n"
            "Les deux ouvertures prévues par le protocole ont eu lieu, dans l'ordre, et\n"
            "chacune une seule fois.\n\n"
            "**10.1. Les 12 000 lignes réservées**, pour arbitrer entre les finalistes et\n"
            "mesurer le surajustement à l'estimation de sélection\n"
            "(`reports/arbitration.csv`, `reports/overfitting.csv`). Les deux finalistes\n"
            "avaient été désignés au préalable sur trente mesures, sans toucher à cette\n"
            "partie.\n\n"
            "L'arbitrage lui-même n'a pas départagé : 6 410 contre 7 310, soit 900 unités,\n"
            "sous la marge de 2 000 fixée par la section 5, et le nombre de pannes manquées\n"
            "est à égalité. Le gradient boosting a été retenu sur les mesures répétées de\n"
            "la désignation et sur sa dispersion plus faible entre partitions, 1 203 contre\n"
            "1 307.\n\n"
            "**La section 5 ne prévoyait pas ce cas.** Elle désigne le coût comme critère\n"
            "d'arbitrage et le seul, sans critère subsidiaire. Le choix est défendable mais\n"
            "il n'applique pas une règle écrite à l'avance, et il est consigné ici comme\n"
            "tel plutôt que présenté comme l'exécution du protocole.\n\n"
            "**10.2. Le jeu de test officiel**, sur le modèle figé au préalable et son\n"
            "manifeste `models/final_model.json` (`reports/test_result.json`). Coût\n"
            "11 370 contre une référence de 156 250.\n\n"
            "Le seuil figé n'est pas le moins cher sur ce fichier : le seuil que le recul\n"
            "préfère aurait donné 10 060. Les deux valeurs sont consignées dans le même\n"
            "fichier, la première comme résultat et la seconde comme diagnostic. Citer la\n"
            "seconde comme résultat serait rapporter un seuil ajusté sur le jeu de test.",
        ),
    ],
    "docs/technical_decisions.md": [
        (
            "**Le groupe 2 n'est pas emboîté, et c'est pour cela qu'il est traité\n"
            "autrement.** Le même test appliqué à ses 56 colonnes échoue : 119 motifs\n"
            "observés là où un bloc emboîté en produirait 57, et 8 % des lignes violent la\n"
            "règle.",
            "**Le groupe 2 n'est pas emboîté, et c'est pour cela qu'il est traité\n"
            "autrement.** Le même test appliqué à ses 56 colonnes échoue : 115 motifs\n"
            "observés là où un bloc emboîté en produirait 57, et 3 860 lignes sur 48 000,\n"
            "soit 8,04 %, violent la règle.",
        ),
        (
            "l'accord dépasse 99,9 %.",
            "l'accord vaut 0,99985, et le palier le moins homogène des neuf reste au-dessus\n"
            "de 0,9959.",
        ),
        (
            "**Deux colonnes sont des doublons d'absence.** `ab_000` et `cr_000` ont des\n"
            "indicateurs d'absence corrélés à exactement 1,00 : elles portent deux fois la\n"
            "même information de manque. Sans effet sur l'ajustement, mais à connaître avant\n"
            "de lire une importance de variable, qui se répartira arbitrairement entre les\n"
            "deux. `missingness.duplicate_absence_columns` les détecte.",
            "**Les doublons d'absence sont nombreux, pas exceptionnels.**\n"
            "`missingness.duplicate_absence_columns` relève plus de cinquante paires de\n"
            "colonnes dont les indicateurs d'absence sont corrélés à exactement 1,00, dont\n"
            "`ab_000` et `cr_000`, et dont les dix colonnes du groupe `ag` entre elles.\n"
            "Deux colonnes d'une même paire portent deux fois la même information de\n"
            "manque. Sans effet sur l'ajustement, mais déterminant pour la lecture d'une\n"
            "importance de variable, qui se répartira arbitrairement à l'intérieur de\n"
            "chaque paire. C'est une raison de plus de ne pas surinterpréter le classement\n"
            "de `reports/variable_importance.csv`.",
        ),
        (
            "ont une médiane d'apprentissage différente de la médiane calculée sur les deux\n"
            "parties réunies, et l'écart type mesuré sur la validation vaut 0,897 et non 1.",
            "ont une médiane d'apprentissage différente de la médiane calculée sur les deux\n"
            "parties réunies, et l'écart type mesuré sur la validation vaut 0,897 et non 1\n"
            "(85 colonnes sur 180, mesure de `build_dataset.py`).",
        ),
        (
            "**Une colonne est constante après préparation.** `cd_000` ne porte qu'une seule\n"
            "valeur distincte dans tout le fichier d'apprentissage, 1 209 600, sur les 98,9 %\n"
            "de lignes où elle est renseignée.",
            "**Une colonne est constante après préparation.** `cd_000` ne porte qu'une seule\n"
            "valeur distincte dans tout le fichier d'apprentissage, 1 209 600, sur les 98,9 %\n"
            "de lignes où elle est renseignée. Son importance par permutation vaut exactement\n"
            "zéro, ce qui est le contrôle de cohérence attendu.",
        ),
        (
            "**Sur la forêt aléatoire**, dont le seuil ne dégénérait pas complètement, le\n"
            "coût passe de 41 050 à 6 714, soit le facteur 6,1.",
            "**Sur la forêt aléatoire**, dont le seuil ne dégénérait pas complètement, le\n"
            "coût passe de 41 050 à 6 926, soit un facteur 5,9.",
        ),
        (
            "**L'écart entre familles de modèles est mesurable.** Moyenne des deux modèles à\n"
            "base d'arbres, 6 645, contre moyenne des deux modèles linéaires, 9 462 : 2 817\n"
            "unités.",
            "**L'écart entre familles de modèles est mesurable.** Moyenne des deux modèles à\n"
            "base d'arbres, 6 740, contre moyenne des deux modèles linéaires, 9 465 : 2 725\n"
            "unités.",
        ),
        (
            "**L'écart apporté par la préparation n'est pas mesurable.** La comparaison\n"
            "appariée V1 contre V0 donne 220 unités pour une erreur type de 329. Elle est\n"
            "déclarée non significative, comme les cinq autres.",
            "**L'écart apporté par la préparation n'est pas mesurable.** La comparaison\n"
            "appariée V1 contre V0 donne 35 unités pour une erreur type de 131 et un\n"
            "plancher de détection de 267. Elle est déclarée non significative, comme les\n"
            "cinq autres, dont les écarts vont de 3 à 111 unités\n"
            "(`reports/paired_comparisons.csv`).\n\n"
            "Une seconde mesure, indépendante de la première, concorde : les dix variables\n"
            "construites portent une importance par permutation inférieure à 0,001 en valeur\n"
            "absolue, quand `aa_000` seule en porte 0,057\n"
            "(`reports/variable_importance.csv`). Deux méthodes différentes ne détectent\n"
            "rien, ce qui est un argument plus solide qu'une seule.",
        ),
        (
            "**Le rapport entre les deux n'existe donc pas.** Écrire que la préparation pèse\n"
            "treize fois moins que le choix du modèle, 2 817 contre 220, traite un nombre non\n"
            "significatif comme une quantité. Le 220 n'est pas un petit effet mesuré, c'est\n"
            "un effet dont la mesure ne permet pas de dire s'il est positif, nul ou négatif.",
            "**Le rapport entre les deux n'existe donc pas.** Diviser le second dans le\n"
            "premier pour annoncer que la préparation pèse un nombre de fois donné de moins\n"
            "que le choix du modèle traiterait un nombre non significatif comme une\n"
            "quantité. Ce n'est pas un petit effet mesuré, c'est un effet dont la mesure ne\n"
            "permet pas de dire s'il est positif, nul ou négatif.",
        ),
        (
            "**Le seuil de Bayes reste un diagnostic.** Il n'est jamais utilisé comme point\n"
            "de fonctionnement. Un seuil mesuré très éloigné de 0,5 sur l'échelle pondérée\n"
            "signale un défaut de calibration, ce qui est une information utile, mais pas une\n"
            "consigne. Sur la régression logistique, les seuils retenus par pli valent 0,331\n"
            "à 0,544 pour une moyenne de 0,439, soit 0,0154 après dépondération contre 0,0196\n"
            "attendu : le modèle est légèrement sous-confiant, sans plus.",
            "**Le seuil de Bayes reste un diagnostic, mais pas par la dépondération.** Il\n"
            "n'est jamais utilisé comme point de fonctionnement.\n\n"
            "La dépondération suppose que la pondération a effectivement multiplié les cotes\n"
            "par cinquante. La mesure montre que ce n'est le cas que pour deux modèles sur\n"
            "cinq. En comparant la probabilité moyenne prédite au taux réel de 1,667 %\n"
            "(`reports/calibration.csv`) :\n\n"
            "| Modèle | Probabilité moyenne | Score de Brier |\n"
            "|---|---|---|\n"
            "| Gradient boosting | 0,0165 | 0,0052 |\n"
            "| Forêt aléatoire | 0,0148 | 0,0064 |\n"
            "| SVM linéaire | 0,0167 | 0,0076 |\n"
            "| Perceptron | 0,0596 | 0,0201 |\n"
            "| Régression logistique | 0,0982 | 0,0290 |\n\n"
            "Trois modèles restent centrés sur le taux de base, deux le dépassent d'un\n"
            "facteur trois à six. Appliquer la formule inverse aux trois premiers fabrique\n"
            "un artefact : le gradient boosting, le mieux calibré des cinq au sens du score\n"
            "de Brier, ressortirait à 456 fois le repère analytique. La colonne\n"
            "`ratio_to_bayes` du fichier de calibration ne doit donc pas être citée.\n\n"
            "Le diagnostic retenu est la probabilité moyenne prédite comparée au taux réel,\n"
            "et le score de Brier : ni l'un ni l'autre ne dépend d'une hypothèse sur l'effet\n"
            "de la pondération.\n\n"
            "La conséquence pour la décision D-11 est plus forte que l'argument initial. Il\n"
            "ne s'agit pas de dire que certains modèles sont mal calibrés, mais que la\n"
            "pondération déplace les probabilités d'une manière qui dépend du modèle et\n"
            "n'est pas prévisible a priori. Aucun seuil analytique unique ne s'applique donc\n"
            "aux cinq modèles évalués sous protocole commun, et c'est ce qui impose de le\n"
            "mesurer.",
        ),
        (
            "Résultat mesuré : les quatre variantes s'étalent de 8 368 à 9 210 pour des\n"
            "écarts types de 690 à 1 840. Aucun écart ne franchit le bruit. La configuration\n"
            "de référence a été conservée par principe de simplicité\n"
            "(`reports/loss_functions.csv`).",
            "Résultat mesuré : les quatre variantes s'étalent de 8 454 à 9 124. Aucun écart\n"
            "ne franchit le bruit. La configuration de référence a été conservée par\n"
            "principe de simplicité (`reports/loss_functions.csv`).\n\n"
            "Rien n'est affirmé sur leurs dispersions. Le rapport de variances entre la\n"
            "référence et la perte focale pondérée vaut 2,77 sur quatre degrés de liberté,\n"
            "pour une probabilité de 0,34.",
        ),
    ],
    "docs/dataset_scania.md": [
        (
            "Sept groupes de colonnes sont des variables histogramme, c'est-à-dire des\n"
            "comptages répartis en classes de valeurs. Ils totalisent 70 colonnes, de\n"
            "préfixes `ag`, `ay`, `az`, `ba`, `cn`, `cs` et `ee`. Les 100 autres colonnes\n"
            "sont des compteurs isolés.",
            "Sept groupes de colonnes sont des variables histogramme, c'est-à-dire des\n"
            "comptages répartis en classes de valeurs. Ils totalisent 70 colonnes, de\n"
            "préfixes `ag`, `ay`, `az`, `ba`, `cn`, `cs` et `ee`. Les 100 autres colonnes\n"
            "sont des compteurs isolés.\n\n"
            "Deux noms s'écartent de la convention à trois chiffres, `am_0` et `ec_00`.\n"
            "Conservés tels quels : les renommer briserait la correspondance avec le jeu de\n"
            "données publié.",
        ),
        (
            "Huit colonnes dépassent 50 % d'absences, 24 dépassent 20 %, et une seule colonne\n"
            "est complète. Le profil est presque identique entre entraînement et test, ce qui\n"
            "indique une collecte homogène.",
            "Huit colonnes dépassent 50 % d'absences, 24 dépassent 20 %, et une seule colonne\n"
            "est complète. Le profil est presque identique entre entraînement et test, ce qui\n"
            "indique une collecte homogène.\n\n"
            "L'absence ne se répartit pas non plus uniformément entre les deux natures de\n"
            "colonnes (`reports/dataset_report.txt`) :\n\n"
            "| Nature | Colonnes | Taux moyen d'absence |\n"
            "|---|---|---|\n"
            "| Colonnes d'histogramme | 70 | 1,13 % |\n"
            "| Compteurs isolés | 100 | 13,38 % |\n\n"
            "Les colonnes d'histogramme sont donc presque complètes, et la totalité de la\n"
            "manquance se concentre dans les compteurs isolés, d'un facteur douze. C'est\n"
            "cohérent avec la lecture retenue de compteurs qui se remplissent avec l'usage,\n"
            "et cela explique aussi pourquoi le travail sur les absences n'a jamais atteint\n"
            "les variables histogramme.",
        ),
        (
            "Références complètes dans `references.bib`.",
            "Références complètes dans `references.bib`.\n\n"
            "Onze résultats publiés entre 2018 et 2024, compilés par Beikmohammadi et al.\n"
            "(arXiv:2402.08611), sont consignés avec les trois du challenge dans\n"
            "`reports/published_results.csv`. Chaque total y est recalculé depuis son\n"
            "décompte d'erreurs et chaque précision publiée depuis les effectifs du jeu de\n"
            "test : les quatorze totaux et les onze précisions se reconstituent.\n\n"
            "Le fichier porte une colonne de niveau de confiance. Les réponses du jeu de\n"
            "test sont publiques depuis 2016, donc les onze résultats postérieurs n'ont pas\n"
            "été obtenus à l'aveugle, contrairement aux trois du challenge. La trajectoire\n"
            "des coûts sur ce jeu fixe, 10 140 en 2018, 6 050 en 2019, 3 440 en 2024, est la\n"
            "signature d'un ajustement progressif de la communauté au jeu de test.",
        ),
    ],
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="report without writing")
    args = parser.parse_args()

    applied = missing = 0

    for relative, replacements in PATCHES.items():
        path = ROOT / relative
        if not path.exists():
            print(f"[absent] {relative}")
            missing += len(replacements)
            continue

        text = original = path.read_text(encoding="utf-8")
        for index, (old, new) in enumerate(replacements, start=1):
            count = text.count(old)
            if count == 0:
                if new and new in text:
                    print(f"[already] {relative} #{index}")
                else:
                    print(f"[NOT FOUND] {relative} #{index}: "
                          f"{old.splitlines()[0][:60]}...")
                    missing += 1
                continue
            if count > 1:
                print(f"[AMBIGUOUS] {relative} #{index}: {count} occurrences")
                missing += 1
                continue
            text = text.replace(old, new)
            applied += 1

        if text != original and not args.check:
            path.write_text(text, encoding="utf-8")
            print(f"[written] {relative}")

    print(f"\n{applied} replacements applied, {missing} not applied")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
