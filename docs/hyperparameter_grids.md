# Grilles et configurations d'hyperparamètres

Ce document consigne les grilles explorées et les configurations retenues. Il
est reconstitué depuis les carnets et depuis `reports/benchmark.csv`.

## Grille réellement enregistrée

Une seule grille a été conservée avec ses résultats intermédiaires, celle de la
régression logistique, dans le carnet d'exploration. Quatre valeurs, à
protocole et découpage identiques.

| C | Coût moyen | Écart type |
|---|---|---|
| 0,01 | 9 608 | 1 428 |
| 0,1 | 10 164 | 492 |
| 1,0 | 10 296 | 193 |
| 10,0 | 10 916 | 398 |

Lecture : le coût décroît de façon monotone quand la régularisation augmente,
et la dispersion suit le mouvement inverse. Le modèle le plus régularisé est le
moins cher et le plus instable.

C'est ce comportement monotone qui a conduit à prolonger la grille vers le bas.
Le banc d'essai final retient `C = 0,001`, en dehors de cette grille, pour un
coût de 9 596. Le gain sur `C = 0,01` est de 12 unités : la valeur retenue est
équivalente, et le prolongement de la grille n'a rien produit.

## Configurations retenues par le banc d'essai

Valeurs de `reports/benchmark.csv`.

| Modèle | Configuration | Coût moyen | Écart type |
|---|---|---|---|
| Gradient boosting (XGBoost) | `max_depth=8`, `learning_rate=0.1`, `n_trees=300` | 6 554 | 827 |
| Forêt aléatoire | `n_trees=300`, `max_depth=None`, `min_samples_leaf=1` | 6 926 | 804 |
| Perceptron Keras | `units=(64, 32)`, `epochs=20` | 8 494 | 1 780 |
| SVM linéaire | `C=0.001` | 9 334 | 1 465 |
| Régression logistique | `C=0.001` | 9 596 | 1 222 |

Les valeurs par défaut de `src/models.py` ne sont pas toutes celles du tableau :
les fabriques ont `max_depth=6` pour le gradient boosting et `C=0.01` pour les
deux modèles linéaires. Les configurations du tableau sont passées explicitement
par les carnets et par les scripts. Cet écart est volontaire, les défauts du
module restant des valeurs de démarrage neutres.

## Le modèle retenu

Le gradient boosting, départagé de la forêt aléatoire sur 30 mesures et non sur
cinq (`reports/finalists.csv`), puis confirmé sur les 12 000 lignes réservées
(`reports/arbitration.csv`) et figé avant l'ouverture du jeu de test
(`models/final_model.json`).

Aucune recherche d'hyperparamètres n'a été conduite après le banc d'essai. La
configuration figée est celle du tableau ci-dessus, et le seuil de décision est
celui mesuré par le protocole, 0,002372.

## Ce qui n'a pas été enregistré

**L'étendue des grilles des quatre autres modèles.** Seules les configurations
retenues sont connues. Les valeurs candidates et leurs coûts n'ont pas été
consignés au moment des exécutions et ne sont pas reconstituables depuis les
fichiers de résultats. C'est un trou de reproductibilité, signalé comme tel dans
les limites des deux README, et c'est un manquement à la section 7 du protocole
d'évaluation.

**Une exception documentée : le SVM à noyau RBF.** Il ne figure dans aucun
résultat, mais sa faisabilité a été mesurée avant de l'écarter : 0,2 s pour
5 000 lignes, ce qui extrapole à quelques minutes pour un entraînement complet
et rendait la campagne réalisable. La fabrique correspondante a été retirée de
`src/models.py`, puisque aucune campagne ne l'a exécutée. Le chronométrage
justifie que l'abandon n'était pas une contrainte de calcul.

## Ce qui reste à déclarer avant toute nouvelle campagne

- L'étendue de la grille de chaque modèle, écrite avant l'exécution.
- Le nombre de candidats par modèle, qui doit être comparable entre les cinq.
- La métrique de sélection interne, qui doit être le coût et non l'AUC.
- Le nombre de partitions, puisque cinq plis se sont révélés insuffisants pour
  départager deux modèles proches.
