# Grilles et configurations d'hyperparamètres

Ce document consigne les grilles explorées et les configurations retenues. Il
est reconstitué depuis les carnets et depuis `reports/benchmark.csv`.

## Grille réellement enregistrée

Une seule grille a été conservée avec ses résultats intermédiaires, celle de la
régression logistique, dans le carnet d'exploration. Quatre valeurs, à protocole
et découpage identiques.

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
coût de 9 598. Le gain sur `C = 0,01` est de 10 unités : la valeur retenue est
équivalente, et le prolongement de la grille n'a rien produit.

## Configurations retenues par le banc d'essai

| Modèle | Configuration | Coût moyen | Écart type |
|---|---|---|---|
| Gradient boosting (XGBoost) | `max_depth=8`, `learning_rate=0.1` | 6 576 | 1 030 |
| Forêt aléatoire | `n_trees=300`, `max_depth=None`, `min_samples_leaf=1` | 6 714 | 530 |
| Perceptron Keras | `units=(64, 32)` | 8 550 | 1 838 |
| SVM linéaire | `C=0.001` | 9 326 | 1 473 |
| Régression logistique | `C=0.001` | 9 598 | 1 218 |

Les valeurs par défaut de `src/models.py` ne sont pas toutes celles du tableau :
les fabriques ont `max_depth=6` pour le gradient boosting et `C=0.01` pour les
deux modèles linéaires. Les configurations du tableau sont passées explicitement
par les carnets. Cet écart est volontaire, les défauts du module restant des
valeurs de démarrage neutres.

## Ce qui n'a pas été enregistré

**L'étendue des grilles des quatre autres modèles.** Seules les configurations
retenues sont connues. Les valeurs candidates et leurs coûts n'ont pas été
consignés au moment des exécutions et ne sont pas reconstituables depuis les
fichiers de résultats. C'est un trou de reproductibilité, et il est signalé
comme tel dans les limites du README.

**Une exception documentée : le SVM à noyau RBF.** Il ne figure dans aucun
résultat, mais sa faisabilité a été mesurée avant de l'écarter : 0,2 s pour
5 000 lignes, ce qui extrapole à quelques minutes pour un entraînement complet
et rend la campagne réalisable. La fabrique correspondante a néanmoins été
retirée de `src/models.py`, puisque aucune campagne ne l'a exécutée. Le
chronométrage justifie que l'abandon n'était pas une contrainte de calcul.

## Ce qui reste à déclarer avant la prochaine campagne

- L'étendue de la grille de chaque modèle, écrite avant l'exécution.
- Le nombre de candidats par modèle, qui doit être comparable entre les cinq.
- La métrique de sélection interne, qui doit être le coût et non l'AUC.
