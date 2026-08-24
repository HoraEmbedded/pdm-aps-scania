# Journal de bord

Une entrée par séance. Ce journal alimente la section « difficultés rencontrées »
du rapport final.

## Semaine du 10 au 15 août 2026

Analyse exploratoire du jeu APS Scania. Mise en évidence de 64 colonnes dont le
motif d'absence porte de l'information, réparties en deux groupes de sens
opposés. Emboîtement parfait du premier groupe, huit colonnes, neuf motifs
observés sur 256 possibles, aucune exception. Mise en relation avec la seule
colonne complète du fichier, dont la médiane varie d'un facteur 329 selon la
profondeur d'absence, à classe constante. Décisions D-09 et D-10.

## 12 août 2026

Décision D-11. Constat que pondérer les classes selon le rapport des coûts et
appliquer par ailleurs le seuil analytique appliquerait ce rapport deux fois,
pour un rapport effectif de 2501 contre 1. Le coût n'entre désormais qu'une seule
fois dans la chaîne, par la pondération, et le seuil est mesuré et non déduit.

## 22 août 2026, reprise du projet sur un dépôt unique

Constat de départ : dix-neuf documents de travail pour un carnet sans aucune
cellule de texte, ce qui rendait l'état courant du projet illisible. Décision de
restructurer le dépôt, de ramener le code à un seul niveau et la documentation à
deux fichiers, et d'intégrer les décisions aux documents qui les appliquent.

Trois corrections techniques apportées à la chaîne existante.

Le seuil de décision était réglé sur des probabilités prédites sur les lignes
d'entraînement du pli lui-même. Il est désormais réglé sur des probabilités hors
échantillon, obtenues par validation croisée interne. L'effet mesuré sur la forêt
aléatoire est un facteur 6,1 sur le coût.

La détection des colonnes informatives était effectuée sur les 60 000 lignes,
donc avant le découpage. Elle est désormais effectuée sur les 48 000 lignes
d'apprentissage seules. Les listes obtenues sont identiques, ce qui constitue un
argument de robustesse.

La recherche du seuil optimal était une boucle sur les probabilités observées.
Elle est désormais vectorisée par tri et sommes cumulées, et traite le cas
dégénéré du classifieur constant que l'ancienne version ne pouvait pas atteindre.

Chaîne de préparation rejouée et vérifiée. Six tests de la fonction de coût
passés, dont la reconstitution du score du vainqueur du concours 2016.

## 22 août 2026, banc d'essai

Trois modèles évalués sous protocole identique. Coûts moyens sur cinq plis,
échelle d'un pli de 9 600 lignes et 160 pannes, règle naïve de référence à
80 000.

| Modèle | Coût | Dispersion |
|---|---|---|
| Gradient boosting, profondeur 8 | 6 576 | 1 030 |
| Forêt aléatoire, 300 arbres | 6 714 | 530 |
| Machine à vecteurs de support linéaire | 9 188 | 760 |
| Régression logistique | 9 596 | 1 515 |

Les deux premiers sont séparés de 138 unités, très en dessous du seuil de
départage de 2 000 unités fixé par le protocole. Ils ne sont pas départageables.

Difficulté rencontrée : le solveur du support à vecteurs ne converge pas au-delà
d'une certaine valeur du paramètre de régularisation, et la campagne a dû être
interrompue. Le perceptron reste à évaluer.

## Prochaine séance

Terminer le banc d'essai, puis conduire les deux expériences d'ablation.
