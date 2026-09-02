# Maintenance prédictive sur le jeu de données APS Scania

Classification de pannes sensible au coût sur le système d'air comprimé de
camions Scania, avec cinq familles de modèles comparées sous un protocole
d'évaluation figé.

Projet de quatrième année du cycle ingénieur, 10 semaines, encadré. Version
anglaise : [README.md](README.md).

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
| Validation, 12 000 lignes | 1,67 % | 100 000 | 118 000 | ne rien signaler |

La règle la moins chère s'inverse entre les deux : un chiffre de référence pour
ce jeu de données ne veut rien dire sans le fichier sur lequel il est mesuré.

## Résultats

Moyenne sur 5 plis d'une validation croisée stratifiée sur 48 000 lignes, un
pli représentant environ 9 600 lignes et 160 pannes. Tableau complet dans
[reports/benchmark.csv](reports/benchmark.csv).

| Modèle | Coût | Écart type | Détection | Fiabilité |
|---|---|---|---|---|
| Gradient boosting, profondeur 8 | 6 576 | 1 030 | 0,955 | 0,342 |
| Forêt aléatoire, 300 arbres | 6 714 | 530 | 0,964 | 0,290 |
| Perceptron Keras (64, 32) | 8 550 | 1 838 | 0,939 | 0,294 |
| SVM linéaire | 9 326 | 1 473 | 0,920 | 0,340 |
| Régression logistique | 9 598 | 1 218 | 0,928 | 0,283 |
| Témoin constant | 80 000 | 0 | 0 | - |

Le protocole fixe la marge de départage à 2 000 unités avant toute mesure. Les
deux premiers modèles sont séparés de 138 unités pour des écarts types de 530 et
1 030 : ils ne sont pas départageables, et aucun vainqueur n'est déclaré entre
eux.

Les deux familles, elles, sont départageables : 6 645 en moyenne pour les
modèles à base d'arbres contre 9 462 pour les modèles linéaires, soit 2 817
unités. C'est une différence de moyennes de familles et non une comparaison
appariée, mais l'écart franchit la marge d'un facteur suffisant pour conclure
sur les familles plutôt que sur les cinq implémentations testées.

Deux expériences ont été conduites au-dessus du banc d'essai, toutes deux
rapportées dans [reports/](reports/) :

- **Ablation et plan factoriel sur les variables d'absence.** Six comparaisons
  appariées, toutes non significatives. Le travail de préparation qui constitue
  le cœur intellectuel de ce projet ne produit aucun gain mesurable. C'est un
  résultat, et il est rapporté comme tel. À noter ce que cela n'autorise pas :
  diviser les 2 817 unités significatives par les 220 non significatives pour
  affirmer que la préparation pèse un nombre de fois donné de moins que le choix
  du modèle. Un effet est mesurable, l'autre non
  ([docs/technical_decisions.md](docs/technical_decisions.md)).
- **Quatre fonctions de perte sur le perceptron.** L'étalement va de 8 368 à
  9 210, les écarts ne franchissent pas le bruit, et la configuration de
  référence a été conservée par simplicité.

Le jeu de test officiel n'a jamais été ouvert. Aucun chiffre de test ne figure
dans ce dépôt.

## Démarche

Trois points portent le travail d'ingénierie.

**L'absence traitée comme un signal.** Le taux d'absence par colonne est comparé
entre les deux classes. Deux groupes de sens opposés en ressortent : 8 colonnes
absentes surtout chez les pannes non-APS, dont l'absence est parfaitement
emboîtée, résumées en une variable ordinale de profondeur ; 56 colonnes absentes
surtout chez les pannes APS, regroupées en 9 sous-blocs par taux d'absence, une
indicatrice par sous-bloc. Le groupe 2 reçoit des indicatrices et non une
profondeur parce qu'il échoue au test d'emboîtement que le groupe 1 réussit :
119 motifs là où un bloc emboîté de 56 colonnes en produirait 57. Les variables
sont construites avant l'imputation, qui détruirait le motif. Le groupe 1 est ensuite imputé à zéro et non par la
médiane, parce que ses colonnes sont absentes pour les camions les moins
utilisés.

**Le rapport de coût n'entre qu'une seule fois dans la chaîne.** Pondérer les
classes à 50:1 et appliquer par ailleurs le seuil analytique de Bayes à 1,96 %
appliquerait le rapport deux fois, pour un rapport effectif de 2 501 contre 1.
La pondération porte le coût, le seuil est mesuré par balayage exhaustif, et
`src.cost.unweight` inverse la pondération lorsque le seuil mesuré doit être
comparé au repère analytique.

**Le seuil est réglé hors échantillon.** La première implémentation le réglait
sur les lignes d'entraînement du pli lui-même, où une forêt aléatoire produit
des probabilités quasi parfaites. Il est désormais réglé par validation croisée
interne dans chaque pli. La forêt aléatoire passe de 41 050 à 6 714, un facteur
6,1 ; dans sa forme la plus dégradée, le seuil fuité ramenait le modèle à la
règle "tout signaler", 94 400 par pli, pour un taux de détection de 1,0.

Raisonnement derrière chaque décision :
[docs/technical_decisions.md](docs/technical_decisions.md). Protocole figé avant
l'entraînement : [docs/evaluation_protocol.md](docs/evaluation_protocol.md).

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
scripts/                 points d'entrée en ligne de commande
  download_data.sh       télécharge le jeu depuis sa source primaire
  check_cost_function.py six vérifications de la fonction de coût
  build_dataset.py       rejoue la chaîne de préparation et vérifie les chiffres connus
notebooks/
  00_dataset_selection   les trois candidats, et la métrique vérifiée
  01_exploration         l'absence comme signal, le découpage, l'imputation
  02_benchmark           les cinq modèles sous protocole figé
  03_ablation            les variables d'absence rapportent-elles
  04_cost_sensitive_losses  écrire le coût dans l'objectif
docs/                    protocole, décisions, journal, fiches, bibliographie
reports/                 tableaux de résultats et figures
data/                    brut et préparé, non versionnés, régénérés par script
models/                  modèles sérialisés, non versionnés
```

Les données et les modèles ne sont pas versionnés ; les scripts qui les
régénèrent le sont. Les figures sont suivies volontairement, puisqu'elles
constituent un livrable.

## Installation

TensorFlow ne prend pas en charge Python 3.14, la version 3.13 est donc requise.

```bash
python3.13 -m venv .venv
./.venv/bin/pip install -r requirements.txt   # ou requirements-lock.txt
```

`requirements.txt` liste les dépendances directes. `requirements-lock.txt` fige
toutes les versions transitives, pour que deux installations à six mois
d'écart donnent les mêmes chiffres.

## Exécution

```bash
./scripts/download_data.sh                          # récupère data/raw
./.venv/bin/python scripts/check_cost_function.py   # vérifier la métrique d'abord
./.venv/bin/python scripts/build_dataset.py         # écrit data/processed
./.venv/bin/jupyter lab                             # carnets 00 à 04
```

`check_cost_function.py` est le point d'entrée à lancer en premier : il
reconstitue le score publié du vainqueur du challenge 2016 à partir du détail de
ses erreurs, ce qui rend les coûts de ce dépôt directement comparables à la
littérature. Il vérifie aussi l'inversion des règles constantes décrite plus
haut.

Le carnet 00 lit en plus les deux jeux de données candidats écartés. Ils ne sont
nécessaires à rien d'autre, et sa section 2 se saute d'elle-même en leur absence.

`build_dataset.py` vérifie les dimensions, les effectifs de classe, la taille
des groupes et l'absence de fuite, puis imprime une somme de contrôle du tableau
final. Toute modification silencieuse de la chaîne le fait échouer.


## Reste à faire

Le projet est en cours. Cette liste est celle du plan de projet, dans son ordre.

1. Arbitrer entre les deux finalistes par ouverture unique des 12 000 lignes
   réservées, ce qui mesurera aussi le surajustement de la sélection à
   l'estimation de validation croisée qui l'a produite.
2. Courbes de calibration sur les cinq modèles, puis gel du modèle final.
3. Ouverture unique du jeu de test officiel, comparaison aux chiffres publiés,
   analyse des erreurs et étude d'importance des variables.
4. Démonstrateur de prédiction et mesure du temps de prédiction unitaire.
5. Conteneurisation , notice d'installation, et vérification de
   reproductibilité par un tiers.
6. Rapport final et support de soutenance.

## Limites connues

- **Les 7 variables histogramme ne sont pas traitées.** Le jeu contient 7
  groupes de colonnes histogramme, 70 colonnes au total, identifiés dans
  [reports/dataset_report.txt](reports/dataset_report.txt). La chaîne actuelle
  les traite comme des compteurs ordinaires. En dériver des variables de forme
  est la première piste d'amélioration.
- **Les variables d'absence ne produisent aucun gain mesurable.** Six
  comparaisons appariées, aucune significative. Soit l'effet est plus petit que
  le bruit à cette taille d'échantillon, soit les modèles à base d'arbres
  retrouvent déjà l'information par eux-mêmes.
- **Une seule grille d'hyperparamètres a été enregistrée.** Celle de la
  régression logistique subsiste avec ses quatre résultats intermédiaires ; pour
  les quatre autres modèles, seule la configuration retenue est connue. Les deux
  cas sont documentés dans
  [docs/hyperparameter_grids.md](docs/hyperparameter_grids.md), et aucun script
  ne rejoue ni l'une ni l'autre.
- **Aucun modèle sérialisé et aucun démonstrateur.**
- **Les graines sont figées, ce qui rend les résultats reproductibles et non
  robustes.** C'est la validation croisée répétée sur 6 partitions qui soutient
  les affirmations de significativité.

## Compétences mobilisées

Apprentissage sensible au coût et optimisation de seuil sous perte asymétrique ;
traitement d'une classe rare sans rééchantillonnage ; analyse des valeurs
absentes comme source de variables ; conception d'un protocole expérimental sans
fuite, figé avant les mesures ; comparaison statistique appariée avec marge de
départage déclarée à l'avance ; scikit-learn et TensorFlow, avec un estimateur
et des pertes sur mesure ; organisation d'un projet Python reproductible.

## Sources

Jeu de données : APS Failure at Scania Trucks, Scania CV AB, 2016, UCI Machine
Learning Repository, GPLv3. Fiche :
[docs/dataset_scania.md](docs/dataset_scania.md). Bibliographie :
[docs/references.bib](docs/references.bib), méthode de sélection dans
[docs/bibliography_protocol.md](docs/bibliography_protocol.md).
