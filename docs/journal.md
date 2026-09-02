# Journal de bord

Une entrée par séance. Les chiffres définitifs sont ceux de `reports/`, ce
journal en conserve la chronologie.

## Semaine du 10 au 15 août 2026

Analyse exploratoire du jeu APS Scania. Mise en évidence de 64 colonnes dont le
motif d'absence porte de l'information, réparties en deux groupes de sens
opposés. Emboîtement parfait du premier groupe : huit colonnes, neuf motifs
observés sur 256 possibles, aucune exception. Mise en relation avec la seule
colonne complète du fichier, dont la médiane varie d'un facteur 329 selon la
profondeur d'absence, à classe constante. Décisions D-09 et D-10.

## 12 août 2026

Décision D-11. Constat que pondérer les classes selon le rapport des coûts et
appliquer par ailleurs le seuil analytique appliquerait ce rapport deux fois,
pour un rapport effectif de 2 501 contre 1. Le coût n'entre désormais qu'une
seule fois dans la chaîne, par la pondération, et le seuil est mesuré et non
déduit.

## 22 août 2026, reprise du projet sur un dépôt unique

Constat de départ : dix-neuf documents de travail pour un carnet sans aucune
cellule de texte, ce qui rendait l'état courant du projet illisible. Décision de
restructurer le dépôt, de ramener le code à un seul niveau et d'intégrer les
décisions aux documents qui les appliquent.

Trois corrections techniques apportées à la chaîne existante, consignées en
section 9 du protocole d'évaluation.

Le seuil de décision était réglé sur des probabilités prédites sur les lignes
d'entraînement du pli lui-même. Il est désormais réglé sur des probabilités hors
échantillon, obtenues par validation croisée interne. L'effet mesuré sur la
forêt aléatoire est un facteur 6,1 sur le coût.

La détection des colonnes informatives était effectuée sur les 60 000 lignes,
donc avant le découpage. Elle est désormais effectuée sur les 48 000 lignes
d'apprentissage seules. Les listes obtenues sont identiques, ce qui constitue un
argument de robustesse.

La recherche du seuil optimal était une boucle sur les probabilités observées.
Elle est désormais vectorisée par tri et sommes cumulées, et traite le cas
dégénéré du classifieur constant que l'ancienne version ne pouvait pas
atteindre.

Chaîne de préparation rejouée et vérifiée. Six vérifications de la fonction de
coût passées, dont la reconstitution du score du vainqueur du concours 2016.

## 22 août 2026, première campagne du banc d'essai

Quatre modèles évalués sous protocole identique. Échelle d'un pli : 9 600 lignes
et 160 pannes ; règle constante de référence à 80 000 sur un pli.

| Modèle | Coût | Dispersion |
|---|---|---|
| Gradient boosting, profondeur 8 | 6 576 | 1 030 |
| Forêt aléatoire, 300 arbres | 6 714 | 530 |
| Machine à vecteurs de support linéaire | 9 188 | 760 |
| Régression logistique | 9 596 | 1 515 |

Les deux premiers sont séparés de 138 unités, très en dessous de la marge de
départage de 2 000 unités fixée par le protocole. Ils ne sont pas
départageables.

Difficulté rencontrée : le solveur du support à vecteurs ne converge pas au-delà
d'une certaine valeur du paramètre de régularisation, et la campagne a dû être
interrompue. Le perceptron reste à évaluer.

## Séances suivantes, dates non consignées

Les entrées ci-dessous reconstituent le travail achevé depuis, d'après les
fichiers de `reports/`. Les dates de séance n'ont pas été notées sur le moment
et ne sont pas reconstituables.

**Banc d'essai terminé.** Le perceptron a été évalué et les deux modèles
linéaires réexécutés à `C=0.001`. Les valeurs définitives des cinq modèles sont
celles de `reports/benchmark.csv` ; elles remplacent les deux dernières lignes
du tableau du 22 août, obtenues lors de la campagne interrompue. Le témoin
constant à 80 000 est ajouté au tableau.

**Ablation et plan factoriel sur les variables d'absence.** Six comparaisons
appariées sur validation croisée répétée à 6 partitions
(`reports/paired_comparisons.csv`). Écarts de 18 à 220 unités pour des erreurs
types de 157 à 337. Aucune comparaison n'est significative, y compris celles qui
auraient valorisé le travail de préparation. Résultat rapporté comme tel.

**Quatre fonctions de perte sur le perceptron**
(`reports/loss_functions.csv`). Étalement de 8 368 à 9 210. La variante retenue
est la référence, par principe de simplicité
(`reports/selected_perceptron_variant.json`).

**Restructuration du dépôt.** Code passé en anglais, README créé, protocole
daté et doté d'une section de corrections, documentation alignée sur le contenu
réel du dépôt, fichiers morts de l'ancienne architecture supprimés.

## Reste à faire

Le projet est en cours. Cette liste est celle du plan de projet, dans son ordre.

1. Arbitrer entre les deux finalistes par ouverture unique des 12 000 lignes
   réservées, ce qui mesurera aussi le surajustement de la sélection.
2. Courbes de calibration sur les cinq modèles, puis gel du modèle final. Seule
   la régression logistique a été diagnostiquée à ce jour : seuils par pli de
   0,331 à 0,544, soit 0,0154 après dépondération contre 0,0196 attendu.
3. Ouverture unique du jeu de test officiel, comparaison aux chiffres publiés,
   analyse des erreurs, importance des variables.
4. Démonstrateur de prédiction et mesure du temps de prédiction unitaire.
5. Conteneurisation, notice d'installation, vérification de reproductibilité par
   un tiers.
6. Rapport final et support de soutenance.
