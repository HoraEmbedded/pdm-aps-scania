# Maintenance prédictive sur le jeu de données APS Scania

Classification de pannes sensible au coût sur le système d'air comprimé de
camions Scania. Cinq familles de modèles comparées sous un protocole figé avant
le premier entraînement, puis une ouverture unique du jeu de test officiel.

Projet de quatrième année du cycle ingénieur, 10 semaines, encadré.

| | |
|---|---|
| Coût sur le jeu de test officiel | **11 370** |
| Référence de la règle constante | 156 250 |
| Économie | **92,7 %** |
| Détection | 96,0 % (360 / 375 pannes) |
| Pannes manquées / fausses alertes | 15 / 387 |

Face au podium du challenge IDA 2016, même jeu de test et même métrique :
9 920, 10 900, **11 370**, 11 480. Troisième sur quatre, avec une recherche de
paramètres volontairement sommaire.

Tous les chiffres cités dans ce dépôt existent dans `reports/`, qui fait foi.
Aucun n'est saisi à la main.

---

## Le problème

Les camions sont **déjà en panne et déjà en atelier**. La question n'est pas
« ce camion est-il en panne » mais « la panne vient-elle du système d'air
comprimé (APS) ou d'un autre organe ». Une panne APS manquée signifie que le
circuit d'air n'est jamais inspecté et que la cause réelle reste en place.

Trois propriétés commandent toutes les décisions de conception : un
déséquilibre de classes (1,67 % de positifs en apprentissage, 2,34 % en test),
des absences structurées (8,33 % de cellules vides, 8 colonnes au-delà de 65 %)
et un coût asymétrique (fausse alerte 10, panne manquée 500, rapport 50:1).

Deux conséquences contre-intuitives :

- **La référence à battre s'inverse entre les fichiers.** À un taux de positifs
  de 1,96 % les deux règles constantes coûtent la même chose. En dessous, ne
  rien signaler est moins cher ; au-dessus, tout signaler l'est. Sur le test
  officiel, la référence est donc 156 250, obtenue en signalant toute la
  flotte. Un chiffre de référence ne veut rien dire sans le fichier qui le
  porte.
- **L'objectif contractuel accepte un modèle dont 94,6 % des alertes seraient
  fausses.** C'est un plancher de recevabilité, pas une cible. Trois niveaux
  ont été adoptés : plancher 78 125, objectif de travail 20 000, excellence
  10 000.

---

## La démarche

Trois mesures, dans l'ordre prescrit par le protocole. Aucune mesure postérieure
n'a informé une mesure antérieure.

1. **Banc d'essai, 5 plis sur 48 000 lignes d'apprentissage.** Les familles
   arbres battent les familles linéaires de 2 725 unités, au-delà de la marge de
   départage de 2 000 fixée à l'avance. Les deux premiers modèles, eux, sont
   séparés de 372 unités : non départageables à ce stade.
2. **Validation croisée répétée, 6 partitions, 30 mesures appariées.** Cette
   étape **désigne les deux finalistes**, elle ne les arbitre pas.
3. **Arbitrage sur 12 000 lignes réservées, ouvertes une seule fois.** Le coût
   ne les départage pas et les pannes manquées sont à égalité ; le gradient
   boosting est retenu sur les mesures répétées et sa dispersion plus faible.

Deux décisions, deux fichiers, deux marges : `reports/finalists.csv` désigne,
`reports/arbitration.csv` arbitre. Les confondre attribuerait une décision au
mauvais jeu de données.

Trois points portent le travail d'ingénierie : **l'absence traitée comme un
signal** (deux groupes de colonnes de sens opposé, variables construites avant
l'imputation qui détruirait le motif) ; **le rapport de coût qui n'entre qu'une
seule fois** dans la chaîne (la pondération porte le coût, le seuil est mesuré,
pas déduit — sinon le rapport serait appliqué deux fois, pour un effectif de
2 501:1) ; **le seuil réglé hors échantillon** (le régler sur les lignes
d'entraînement du pli faisait passer le coût de 6 926 à 41 050).

Détail : `docs/technical_decisions.md`, `docs/evaluation_protocol.md`.

### Ce que les expériences n'ont pas montré

Rapporté parce qu'elles ont été conduites, et qu'un résultat nul est un
résultat. L'ablation des variables d'absence (six comparaisons appariées) ne
produit **aucun gain mesurable**, et quatre fonctions de perte sur le
perceptron ne se départagent pas. Le travail de préparation qui constitue le
cœur intellectuel du projet ne paie pas — l'effet est plus petit que le bruit,
ou les arbres retrouvent l'information seuls.

---

## Difficultés rencontrées

Treize difficultés recensées, dont sept erreurs de méthode. **Aucune n'était
visible dans le résultat produit** : un document biaisé, un critère construit à
l'envers ou une contradiction interne se lisent comme un travail abouti. Les
obstacles techniques, eux, ont tous été résolus le jour même.

- **Une grille construite pour favoriser un candidat.** La première version
  récompensait un jeu de données dégradé, au motif que le nettoyer démontrerait
  des compétences. Ce n'était pas un critère de qualité mais une justification
  après coup. → *Une méthode d'évaluation se construit avant de connaître les
  candidats, et se teste en vérifiant qu'un autre que le favori peut l'emporter
  sur au moins un critère.*
- **Un raisonnement juste, non appliqué à sa propre recommandation.** Un
  document expliquait pourquoi rééquilibrer déforme les probabilités, puis
  recommandait deux sections plus loin d'appliquer deux corrections
  simultanées, comptant deux fois l'asymétrie. → *La cohérence se vérifie en
  confrontant les passages d'un même sujet, pas en relisant dans l'ordre.*
- **Une inversion recopiée depuis une source officielle.** Les scores du
  concours 2016 notés avec les deux types d'erreurs inversés : 199 150 au lieu
  des 11 480 annoncés. → *Quand une source fournit un total et son détail,
  refaire le calcul.*
- **Incompatibilité Python / TensorFlow.** Ubuntu 26.04 livre Python 3.14,
  TensorFlow s'arrête à 3.13. Sans détection, le blocage survenait en semaine 6,
  après deux mois de travail.
- **Un fichier lu sans erreur mais mal lu.** Des absences écrites `na` en texte
  auraient fait traiter toutes les colonnes comme du texte et renvoyer zéro
  absence partout. → *Une lecture qui réussit n'est pas nécessairement une
  lecture correcte.*
- **Une moyenne qui masquait la réalité.** 8,3 % d'absences en moyenne suggère
  un jeu propre ; colonne par colonne, huit dépassent 65 %. → *Devant un
  indicateur agrégé, regarder la distribution qui se cache derrière.*

Détail complet et règles de travail dans `docs/notes_de_methode.md`.

---

## Perspectives

**Pistes techniques.** Les 7 groupes de variables histogramme (70 colonnes) ne
sont pas traités, et sont aussi les moins touchés par l'absence — en dériver des
variables de forme est la première piste. Les variables d'absence ne produisent
aucun gain mesurable : rejouer le plan sur un modèle linéaire testerait
l'hypothèse de récupération par les arbres. Une seule grille d'hyperparamètres a
été conservée, aucun script ne la rejoue.

**Limites.** Le seuil figé n'est pas le moins cher sur le test (11 370 contre
10 060 au seuil que le recul préfère) ; le seuil figé est le résultat, l'autre
un diagnostic. Et une réserve à porter au rapport : les réponses du test étant
publiques depuis 2016, les scores publiés s'améliorent régulièrement sur ce
même jeu fixe (10 140 en 2018, 6 050 en 2019, 3 440 en 2024). Le projet, qui
s'impose une ouverture unique, compare donc un résultat honnête à des résultats
dont l'indépendance n'est pas garantie.

---

## Organisation et exécution

```
src/         bibliothèque importable, un seul niveau
scripts/     points d'entrée (téléchargement, vérification, bancs d'essai)
notebooks/   00 à 06, dans l'ordre du protocole
tests/       40 tests sur 5 modules
app/         le démonstrateur Streamlit
docs/        protocole, décisions, journal, notes de méthode, bibliographie
reports/     résultats et figures — font foi
data/ models/  non versionnés, régénérés par script
```

TensorFlow ne prend pas en charge Python 3.14, la version 3.13 est requise.

```bash
python3.13 -m venv .venv
./.venv/bin/pip install -r requirements.txt

./scripts/download_data.sh                          # récupère data/raw
./.venv/bin/python scripts/check_cost_function.py   # vérifier la métrique d'abord
./.venv/bin/python scripts/build_dataset.py         # écrit data/processed
./.venv/bin/python -m pytest                        # 40 tests
./.venv/bin/python scripts/verify.py                # 23 vérifications
```

`check_cost_function.py` reconstitue le score publié du vainqueur 2016 depuis
le détail de ses erreurs, ce qui rend les coûts comparables à la littérature.
`build_dataset.py` vérifie dimensions, effectifs, groupes et absence de fuite,
puis imprime une somme de contrôle (313 696) : toute modification silencieuse
de la chaîne le fait échouer.

## Sources

APS Failure at Scania Trucks, Scania CV AB, 2016, UCI Machine Learning
Repository, GPLv3. Fiche : `docs/dataset_scania.md`. Bibliographie :
`docs/references.bib`, méthode de sélection dans
`docs/bibliography_protocol.md`.


Si tu veux encore plus court, on peut descendre à ~50 lignes en supprimant les difficultés détaillées et en ne gardant qu'un renvoi vers `docs/`. Tu veux que je te fasse cette version minimale ?
