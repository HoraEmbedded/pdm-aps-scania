# Maintenance prédictive sur le jeu de données APS Scania

Classification de pannes sensible au coût sur le système d'air comprimé de
camions Scania. Cinq familles de modèles comparées sous un protocole
d'évaluation figé avant le premier entraînement, puis une ouverture unique du
jeu de test officiel.

Projet de quatrième année du cycle ingénieur, 10 semaines, encadré. Version
anglaise : [README.md](README.md).

## Résultat

| | |
|---|---|
| Coût sur le jeu de test officiel | **11 370** |
| Référence de la règle constante | 156 250 |
| Économie | **92,7 %** |
| Taux de détection | 96,0 %, 360 pannes sur 375 |
| Pannes manquées | 15 |
| Fausses alertes | 387 |

Face au podium du challenge industriel IDA 2016, sur le même jeu de test et
avec la même métrique : 9 920, 10 900, **11 370**, 11 480. Troisième sur
quatre, avec une recherche de paramètres volontairement sommaire et cinq
familles comparées sous un protocole unique.

La comparaison avec la quatrième place est exacte : les mêmes 15 pannes
manquées, 387 fausses alertes contre 398. À détection égale, les 110 unités
d'écart sont entièrement des fausses alertes.

Le jeu de test a été ouvert une seule fois, sur un modèle figé au préalable.
Tous les chiffres ci-dessus sont dans
[reports/test_result.json](reports/test_result.json). Onze autres résultats
publiés, et les trois niveaux de confiance auxquels ils doivent être lus, sont
dans [reports/published_results.csv](reports/published_results.csv).

## Le problème

Les camions de ce jeu de données sont déjà immobilisés en atelier. La question
n'est pas de savoir si un camion est en panne, mais si la panne provient du
système d'air comprimé (APS) ou d'un autre organe. Une panne APS manquée
signifie que le circuit d'air n'est jamais inspecté et que la vraie cause reste
en place.

Le jeu de données contient 170 relevés de capteurs anonymisés par camion,
publiés par Scania en 2016 pour le challenge industriel IDA. Trois propriétés
commandent toutes les décisions de conception :

| Propriété | Valeur mesurée |
|---|---|
| Déséquilibre des classes | 1,67 % de positifs en apprentissage, 2,34 % en test |
| Absences structurées | 8,33 % de cellules vides, 8 colonnes au-delà de 65 %, une seule colonne complète |
| Coût asymétrique | Une fausse alerte coûte 10, une panne manquée 500, soit un rapport de 50 contre 1 |

L'exactitude n'est pas la métrique. La métrique est le coût total de la matrice
Scania, et la référence à battre est la moins chère des deux règles constantes.
Laquelle c'est dépend du fichier, car les deux coûtent la même chose à un taux
de positifs de 1,96 % :

| Fichier | Taux de positifs | Ne rien signaler | Tout signaler | Référence |
|---|---|---|---|---|
| Test officiel, 16 000 lignes | 2,34 % | 187 500 | 156 250 | tout signaler |
| Partie réservée, 12 000 lignes | 1,67 % | 100 000 | 118 000 | ne rien signaler |

La règle la moins chère s'inverse entre les deux : un chiffre de référence pour
ce jeu de données ne veut rien dire sans le fichier sur lequel il est mesuré.

## Comment le modèle a été choisi

Trois mesures, dans l'ordre prescrit par le protocole. Aucune mesure
postérieure n'a informé une mesure antérieure.

**1. Banc d'essai, 5 plis sur les 48 000 lignes d'apprentissage.** Un pli
représente environ 9 600 lignes et 160 pannes. Tableau complet dans
[reports/benchmark.csv](reports/benchmark.csv).

| Modèle | Coût | Écart type | Détection | Fiabilité |
|---|---|---|---|---|
| Gradient boosting, profondeur 8 | 6 554 | 827 | 0,954 | 0,353 |
| Forêt aléatoire, 300 arbres | 6 926 | 804 | 0,963 | 0,282 |
| Perceptron Keras (64, 32) | 8 494 | 1 780 | 0,940 | 0,294 |
| SVM linéaire | 9 334 | 1 465 | 0,920 | 0,339 |
| Régression logistique | 9 596 | 1 222 | 0,928 | 0,283 |
| Témoin constant | 80 000 | 0 | 0 | - |

La famille des arbres bat la famille linéaire de 2 725 unités, 6 740 contre
9 465 en moyennes de familles. C'est une différence de moyennes et non une
comparaison appariée, mais l'écart franchit la marge de départage de 2 000
unités fixée par le protocole d'assez loin pour conclure sur les familles
plutôt que sur cinq implémentations particulières.

Les deux premiers modèles sont séparés de 372 unités, largement dans la marge.
Cinq plis ne les départagent pas.

**2. Validation croisée répétée, 6 partitions, 30 mesures.** Toujours sur les
lignes d'apprentissage, donc sans toucher à quoi que ce soit de réservé.
Appariée pli par pli, la différence vaut 396 unités pour un plancher de
détection de 354 ([reports/finalists.csv](reports/finalists.csv)).

Cette étape désigne les deux finalistes. Elle n'arbitre pas entre eux : elle est
mesurée sur les données mêmes sur lesquelles toutes les décisions de
modélisation ont déjà été prises. Cinq plis ne les distinguaient pas du tout,
trente mesures le peuvent, et c'est ce qu'achète un plan répété.

**3. Arbitrage sur les 12 000 lignes réservées, ouvertes une seule fois.**
[reports/arbitration.csv](reports/arbitration.csv) place le gradient boosting à
6 410 et la forêt à 7 310, à détection égale, 0,97, et 6 pannes manquées de part
et d'autre. Les 900 unités d'écart sont sous la marge de 2 000 du protocole : le
coût ne les départage donc pas ici non plus, et le nombre de pannes manquées est
à égalité.

Le gradient boosting a été retenu sur la base des mesures répétées de l'étape 2
et de sa dispersion plus faible entre ces partitions, 1 203 contre 1 307.

**Deux décisions, deux fichiers, deux marges**, et elles sont faciles à
confondre puisque les deux produisent un chiffre du même ordre :

| | Désignation des finalistes | Arbitrage |
|---|---|---|
| Données | 48 000 lignes d'apprentissage | 12 000 lignes réservées |
| Méthode | validation croisée répétée, 30 mesures appariées | mesure unique |
| Fichier | `reports/finalists.csv` | `reports/arbitration.csv` |
| Écart | 396 unités | 900 unités |
| Étalon | plancher apparié mesuré de 354 | marge de 2 000 du protocole |
| Verdict | séparables | non départageables |

La différence appariée de 396 unités n'est donc pas le résultat de l'arbitrage,
et la citer comme critère de décision attribuerait une décision au mauvais jeu
de données.

La stabilité est un critère faible et elle est rapportée comme tel : la forêt a
la plus faible dispersion entre plis sur la partition unique, 804 contre 827, et
le classement s'inverse sur les 30 mesures. Les écarts sont de l'ordre de dix
pour cent, donc lequel des deux paraît le plus stable dépend de la dispersion
que l'on lit.

Cette même ouverture mesure le surajustement de la sélection à l'estimation qui
l'a produite. Remise à l'échelle par 1,25 pour le nombre de lignes, la
validation croisée prédit 8 343 et les lignes réservées ont donné 6 410, soit
un écart de −23 % ([reports/overfitting.csv](reports/overfitting.csv)). L'écart
est de signe opposé au surajustement : aucun biais optimiste n'est détectable.
Deux effets de sens contraire s'y superposent, et la mesure ne les sépare pas.

## Démarche

Trois points portent le travail d'ingénierie.

**L'absence traitée comme un signal.** Le taux d'absence par colonne est
comparé entre les deux classes. Deux groupes de sens opposés en ressortent :
8 colonnes absentes surtout chez les pannes non-APS, dont l'absence est
parfaitement emboîtée, 9 motifs sur 256 sans aucune exception, et se résume à
une variable ordinale de profondeur ; 56 colonnes absentes surtout chez les
pannes APS, regroupées en 9 sous-blocs par taux d'absence, une indicatrice par
sous-bloc. Le groupe 2 reçoit des indicatrices et non une profondeur parce
qu'il échoue au test d'emboîtement que le groupe 1 réussit : 115 motifs là où
un bloc emboîté de 56 colonnes en produirait 57, et 3 860 lignes violant la
règle. Les variables sont construites avant l'imputation, qui détruirait le
motif. Le groupe 1 est ensuite imputé à zéro et non par la médiane, parce que
ses colonnes sont absentes pour les camions les moins utilisés.

**Le rapport de coût n'entre qu'une seule fois dans la chaîne.** Pondérer les
classes à 50:1 et appliquer par ailleurs le seuil analytique de Bayes à 1,96 %
appliquerait le rapport deux fois, pour un rapport effectif de 2 501 contre 1.
La pondération porte le coût, le seuil est mesuré par balayage exhaustif, et
`src.cost.unweight` inverse la pondération lorsque le seuil mesuré doit être
comparé au repère analytique.

**Le seuil est réglé hors échantillon.** La première implémentation le réglait
sur les lignes d'entraînement du pli lui-même, où une forêt aléatoire produit
des probabilités quasi parfaites. Il est désormais réglé par validation croisée
interne dans chaque pli. La forêt passe de 41 050 à 6 926, un facteur 5,9 ;
dans sa forme la plus dégradée, le seuil fuité ramenait le modèle à la règle
« tout signaler », 94 400 par pli pour un taux de détection de 1,0, soit
exactement le coût de signaler les 9 440 camions non-APS d'un pli.

Raisonnement derrière chaque décision :
[docs/technical_decisions.md](docs/technical_decisions.md). Protocole figé avant
l'entraînement : [docs/evaluation_protocol.md](docs/evaluation_protocol.md).

## Ce que les expériences n'ont pas montré

Rapporté parce qu'elles ont été conduites, et parce qu'un résultat nul est un
résultat.

- **Ablation et plan factoriel sur les variables d'absence.** Six comparaisons
  appariées à 30 mesures chacune, aucune ne franchissant son plancher de
  détection ([reports/paired_comparisons.csv](reports/paired_comparisons.csv)).
  Les écarts vont de 3 à 111 unités pour des planchers de 223 à 285. Le travail
  de préparation qui constitue le cœur intellectuel de ce projet ne produit
  aucun gain mesurable. Une seconde mesure indépendante concorde : les dix
  variables construites ne portent presque aucune importance par permutation
  ([reports/variable_importance.csv](reports/variable_importance.csv)), quand
  `aa_000` à elle seule en porte 0,057.
- **Quatre fonctions de perte sur le perceptron.** L'étalement va de 8 454 à
  9 124, aucun écart ne franchit le bruit, et la configuration de référence a
  été conservée par simplicité
  ([reports/loss_functions.csv](reports/loss_functions.csv)). Rien n'est
  affirmé non plus sur leurs dispersions : le rapport de variances entre la
  référence et la perte focale pondérée vaut 2,77 sur quatre degrés de liberté,
  pour une probabilité de 0,34.

Ce que cela n'autorise pas : diviser le chiffre non significatif de l'ablation
dans les 2 725 significatifs pour affirmer que la préparation pèse un nombre de
fois donné de moins que le choix du modèle. Un effet est mesurable, l'autre non.

## Calibration

Courbes de fiabilité hors échantillon pour les cinq modèles, dans
[reports/calibration.csv](reports/calibration.csv). Deux quantités sont
rapportées, la probabilité moyenne prédite comparée au taux réel de 1,667 %, et
le score de Brier. Aucune des deux ne dépend d'une hypothèse sur l'effet de la
pondération sur les probabilités.

| Modèle | Probabilité moyenne | Brier |
|---|---|---|
| Gradient boosting | 0,0165 | 0,0052 |
| Forêt aléatoire | 0,0148 | 0,0064 |
| SVM linéaire | 0,0167 | 0,0076 |
| Perceptron | 0,0596 | 0,0201 |
| Régression logistique | 0,0982 | 0,0290 |

Trois modèles restent centrés sur le taux de base, deux le dépassent d'un
facteur trois à six. C'est la raison mesurée pour laquelle le seuil est mesuré
et non déduit, et c'est un argument plus fort en faveur de la décision D-11 que
l'argument initial : la pondération déplace les probabilités d'une manière qui
dépend du modèle et n'est pas prévisible a priori, si bien qu'aucun seuil
analytique unique ne s'applique à cinq modèles comparés sous un protocole
commun.

La formule de dépondération n'est donc pas utilisée comme diagnostic de
calibration. Elle suppose que la pondération a multiplié les cotes par
cinquante, ce qui vaut pour deux modèles sur cinq, et appliquée aux trois autres
elle fabrique un artefact : le gradient boosting, le mieux calibré des cinq au
sens du score de Brier, ressortirait à 457 fois le repère analytique.

## Organisation du dépôt

```
src/                     bibliothèque importable, un seul niveau, sans doublon
  config.py              chemins, graine, matrice de coût, constantes du protocole
  seeding.py             initialise Python, NumPy et TensorFlow
  cost.py                fonction de coût, balayage du seuil, dépondération
  data.py                chargement brut, découpage stratifié, jeu de test scellé
  missingness.py         détection des groupes, profondeur, indicatrices
  preprocessing.py       imputation différenciée puis normalisation
  evaluation.py          validation croisée sous protocole figé
  models.py              les cinq fabriques de modèles
  losses.py              pertes Keras sensibles au coût
  inference.py           le modèle figé, son seuil et la chaîne
scripts/
  download_data.sh       télécharge le jeu depuis sa source primaire
  fetch_models.sh        récupère les poids entraînés depuis la distribution
  check_cost_function.py sept vérifications de la fonction de coût
  build_dataset.py       rejoue la chaîne et vérifie ses chiffres
  paired_comparisons.py  l'ablation et le plan factoriel
  finalists.py           les deux premiers modèles sur 6 partitions
  calibration.py         courbes de fiabilité
  latency.py             temps de prédiction unitaire
  published_results.py   le tableau de la littérature et son contrôle arithmétique
  rebuild.py             régénère les tableaux de synthèse depuis les mesures par pli
  verify.py              23 vérifications qu'un clone neuf doit passer
tests/                   40 tests répartis en 5 modules
notebooks/
  00_dataset_selection   les trois candidats, et la métrique vérifiée
  01_exploration         l'absence comme signal, le découpage, l'imputation
  02_benchmark           les cinq modèles sous protocole figé
  03_ablation            les variables d'absence rapportent-elles
  04_cost_sensitive_losses  écrire le coût dans l'objectif
  05_arbitration         les lignes réservées, et la mesure du surajustement
  06_final_test          l'ouverture unique du jeu de test officiel
app/streamlit_app.py     le démonstrateur
docs/                    protocole, décisions, journal, fiches, bibliographie
reports/                 tableaux de résultats, mesures par pli, figures
data/                    brut et préparé, non versionnés, régénérés par script
models/                  modèles sérialisés, non versionnés, récupérés par script
```

Les données et les modèles ne sont pas versionnés ; les scripts qui les
régénèrent le sont. Les figures sont suivies volontairement, puisqu'elles
constituent un livrable.

**La règle que suit ce dépôt :** les fichiers de `reports/` font foi. Aucun
chiffre d'un document n'est saisi à la main. Tout nombre cité par un document
existe dans un fichier de résultats, et le document nomme ce fichier.

## Installation

TensorFlow ne prend pas en charge Python 3.14, la version 3.13 est donc
requise. L'image conteneur n'a besoin ni de l'un ni de l'autre.

```bash
python3.13 -m venv .venv
./.venv/bin/pip install -r requirements.txt   # ou requirements-lock.txt
```

`requirements.txt` liste les dépendances directes. `requirements-lock.txt` fige
toutes les versions transitives. `requirements-serve.txt` est le sous-ensemble
de service, avec NumPy, scikit-learn et XGBoost épinglés exactement, ces trois
paquets touchant à la sérialisation des modèles.

## Exécution

```bash
./scripts/download_data.sh                          # récupère data/raw
./.venv/bin/python scripts/check_cost_function.py   # vérifier la métrique d'abord
./.venv/bin/python scripts/build_dataset.py         # écrit data/processed
./.venv/bin/python -m pytest                        # 40 tests
./.venv/bin/python scripts/verify.py                # 23 vérifications
./.venv/bin/jupyter lab                             # carnets 00 à 06
```

`check_cost_function.py` est le point d'entrée à lancer en premier : il
reconstitue le score publié du vainqueur du challenge 2016 à partir du détail
de ses erreurs, ce qui rend les coûts de ce dépôt comparables à la littérature.
`build_dataset.py` vérifie les dimensions, les effectifs de classe, la taille
des groupes et l'absence de fuite, puis imprime une somme de contrôle du
tableau final, 313 696. Toute modification silencieuse de la chaîne le fait
échouer.

Le carnet 00 lit en plus les deux jeux candidats écartés. Ils ne sont
nécessaires à rien d'autre, et sa section 2 se saute d'elle-même en leur
absence.

### Le démonstrateur

```bash
./scripts/fetch_models.sh
docker compose up --build          # puis http://localhost:8502
```

Le fichier compose publie le port 8501 du conteneur sur le port 8502 de
l'hôte. Un `docker run -p 8501:8501` le sert sur 8501.

Les poids ne sont pas versionnés dans Git. Ils sont copiés dans l'image et
publiés dans une distribution GitHub, selon le compromis consigné dans
[docs/amendment.md](docs/amendment.md).

## Couverture des exigences

Le cahier des charges est le document contractuel du projet.

| ID | Exigence | État |
|---|---|---|
| EF01 | Chargement et analyse exploratoire | fait, carnets 00 et 01 |
| EF02 | Chaîne de préparation reproductible | fait, `scripts/build_dataset.py` |
| EF03 | Quatre modèles classiques | fait, carnet 02 |
| EF04 | Un réseau de neurones Keras | fait, carnets 02 et 04 |
| EF05 | Protocole commun et coût Scania | fait, `src/evaluation.py` |
| EF06 | Banc d'essai comparatif et choix justifié | fait, gradient boosting, départagé sur 30 mesures |
| EF07 | Sérialisation du modèle retenu | fait, `models/final_model.json` et `src/inference.py` |
| EF08 | Démonstrateur de prédiction | fait, `app/streamlit_app.py` |
| EF09 | Simulation de flux temps réel | abandonné, premier de l'ordre d'abandon, classé Optionnel |
| ENF01 | Python 3 et venv sous Ubuntu | fait |
| ENF02 | Git, code en anglais, documentation en français | fait |
| ENF03 | Reproductibilité : graines, versions figées, carnets | fait, plus `scripts/verify.py` |
| ENF04 | Exécutable sans GPU | fait, `tensorflow-cpu` |
| ENF05 | Image Docker du démonstrateur | fait, réintégré par [docs/amendment.md](docs/amendment.md) |
| ENF06 | Prédiction unitaire sous 1 s | fait, 50 ms en médiane et 184 ms au pire sur 200 appels, [reports/latency_single.csv](reports/latency_single.csv) |

## Limites connues

- **Les 7 groupes de variables histogramme ne sont pas traités.** 70 colonnes,
  identifiées dans [reports/dataset_report.txt](reports/dataset_report.txt),
  traitées comme des compteurs ordinaires. Ce sont aussi les moins touchées par
  l'absence, 1,13 % contre 13,38 % pour les compteurs isolés, si bien que le
  travail sur les absences ne les a jamais atteintes. En dériver des variables
  de forme est la première piste d'amélioration.
- **Les variables d'absence ne produisent aucun gain mesurable.** Six
  comparaisons appariées, aucune significative, et une importance par
  permutation quasi nulle. Soit l'effet est plus petit que le bruit à cette
  taille d'échantillon, soit les modèles à base d'arbres retrouvent
  l'information par eux-mêmes. Tester la seconde explication demanderait de
  rejouer le plan sur la régression logistique, qui ne peut pas.
- **Une seule grille d'hyperparamètres a été enregistrée.** Celle de la
  régression logistique subsiste avec ses quatre résultats intermédiaires ;
  pour les quatre autres modèles, seule la configuration retenue est connue
  ([docs/hyperparameter_grids.md](docs/hyperparameter_grids.md)). Aucun script
  ne rejoue ni l'une ni l'autre.
- **Le seuil figé n'est pas le moins cher sur le jeu de test.** 11 370 contre
  10 060 au seuil que le recul préfère. Le seuil figé est le résultat, l'autre
  est un diagnostic, consigné dans le même fichier.
- **Deux anomalies de nommage dans les colonnes**, `am_0` et `ec_00`, contre
  trois chiffres partout ailleurs. Conservées telles quelles, les renommer
  briserait la correspondance avec le jeu de données publié.
- **Les graines sont figées, ce qui rend les résultats reproductibles et non
  robustes.** C'est la validation croisée répétée sur 6 partitions qui soutient
  les affirmations de significativité.

## Compétences mobilisées

Apprentissage sensible au coût et optimisation de seuil sous perte asymétrique ;
traitement d'une classe rare sans rééchantillonnage ; analyse des valeurs
absentes comme source de variables ; conception d'un protocole sans fuite, figé
avant les mesures, avec ouverture unique des données réservées ; comparaison
statistique appariée avec marge de départage déclarée à l'avance, et séparation
de la désignation des finalistes et de l'arbitrage sur des données
différentes ; évaluation de la calibration sur des quantités libres
d'hypothèses de modélisation ;
scikit-learn et TensorFlow avec un estimateur et des pertes sur mesure ;
sérialisation et mise en service derrière une interface stable ; image
conteneur multi-étages ; organisation d'un projet Python reproductible avec une
vérification exécutable de cette reproductibilité.

## Sources

Jeu de données : APS Failure at Scania Trucks, Scania CV AB, 2016, UCI Machine
Learning Repository, GPLv3. Fiche :
[docs/dataset_scania.md](docs/dataset_scania.md). Bibliographie :
[docs/references.bib](docs/references.bib), méthode de sélection dans
[docs/bibliography_protocol.md](docs/bibliography_protocol.md), résultats
publiés avec leur contrôle arithmétique dans
[reports/published_results.csv](reports/published_results.csv).
