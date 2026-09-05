# Protocole d'évaluation des modèles

**Version 1.0, figée en semaine 3 (15 au 21 août 2026), avant le premier
entraînement du banc d'essai du 22 août 2026.**

Ce document est figé. Toute modification postérieure à l'entraînement d'un
modèle impose de réentraîner l'ensemble des modèles. Les corrections apportées
après le gel figurent en section 9, datées, plutôt que d'être intégrées en
silence au corps du document.

## 1. Données d'entrée

Tableaux produits par `scripts/build_dataset.py` : `data/processed/X_fit.csv` et
`X_val.csv`, de dimensions 48 000 x 180 et 12 000 x 180.

Chaîne de préparation, rejouable par les objets sérialisés
`missingness_encoder.joblib` et `preprocessor.joblib` : découpage stratifié de
graine 42, construction de la variable de profondeur et des neuf indicatrices,
imputation à zéro pour les huit colonnes du groupe 1 et par la médiane pour les
autres, normalisation des 170 colonnes de mesure. Toutes les quantités estimées
proviennent de la partie d'apprentissage seule.

Somme de contrôle du tableau final : 313 696,00.

## 2. Rôle des deux ensembles

**Les 48 000 lignes d'apprentissage** portent toute la phase de comparaison. Les
décisions de modélisation, le réglage des paramètres, le choix du modèle final
et les tests sur les indicatrices se prennent exclusivement sur leur validation
croisée.

**Les 12 000 lignes de validation ne sont pas consultées pendant les semaines 4
à 7.** Elles sont ouvertes une seule fois, en fin de semaine 7, pour arbitrer
entre les modèles finalistes et mesurer l'écart entre le score de validation
croisée et un score obtenu sur des données n'ayant participé à aucune décision.
Cet écart quantifie le surajustement de l'expérimentateur et sera rapporté comme
tel.

**Le jeu de test officiel reste fermé jusqu'à l'étape 6.4.**

## 3. Découpage d'évaluation

Validation croisée stratifiée à 5 plis sur les 48 000 lignes, graine 42. Chaque
pli d'évaluation contient environ 9 600 lignes et 160 pannes.

Les comparaisons appariées entre variantes reposent sur une validation croisée
répétée : 6 partitions différentes de graines 42 à 47, soit 30 mesures au lieu de
5. L'erreur type sur une différence appariée décroît comme la racine du nombre de
répétitions, ce qui est la condition pour détecter un petit effet.

## 4. Traitement du coût asymétrique



- pondération des classes à 50:1 à l'entraînement, valeur fixée depuis la
  matrice de coût et non depuis les fréquences observées ;
- seuil de décision réglé empiriquement par minimisation du coût total.

**Le seuil est réglé à l'intérieur de chaque pli, sur la partie d'apprentissage
de ce pli uniquement, puis appliqué à sa partie d'évaluation.** Un seuil réglé
globalement puis mesuré en validation croisée ferait contribuer chaque pli au
choix du seuil qui l'évalue.

Ce traitement est appliqué de façon strictement identique aux cinq modèles.

## 5. Mesures rapportées

Pour chaque modèle, **moyenne sur les 5 plis et écart type**, sans exception :

1. **Coût total de Scania.** C'est le critère d'arbitrage, et le seul.
2. Taux de détection (rappel).
3. Fiabilité des alertes (précision).
4. Aire sous la courbe ROC, et aire sous la courbe précision-rappel.
5. Détail des erreurs : VP, FP, FN, VN.
6. Seuil retenu, et sa valeur dépondérée comparée au repère analytique de
   1,96 %.

L'écart type n'est pas décoratif. Avec environ 900 unités de bruit sur la
moyenne, **deux modèles séparés de moins de 2 000 unités ne sont pas
départageables.** Cette marge est fixée avant toute mesure.

Le F1 et l'exactitude peuvent être reportés pour information mais ne servent
jamais à départager deux modèles.

## 6. Repères de comparaison

| Repère | Valeur | Niveau de confiance |
|---|---|---|
| Règle constante, sur le jeu de test | 156 250, tout signaler | Incontestable |
| Règle constante, sur la validation | 100 000, ne rien signaler | Incontestable |
| Challenge IDA 2016, obtenu à l'aveugle | 9 920 à 11 480 | Solide |
| Meilleur publié depuis 2016 | 3 440 | À citer avec réserve |

Les deux premières lignes ne désignent pas la même règle. Au-dessus du taux
d'équilibre de 1,96 % la règle la moins chère est de tout signaler, en dessous
c'est de ne rien signaler, et les deux fichiers tombent de part et d'autre. Tout
coût rapporté indique donc le fichier sur lequel il est mesuré.

La réserve sur la dernière ligne est motivée : les réponses du jeu de test sont
publiques depuis 2016, et les scores publiés s'améliorent régulièrement sur ce
même jeu fixe. Le projet compare donc un résultat obtenu à l'aveugle à des
résultats dont l'indépendance au jeu de test n'est pas garantie.

## 7. Réglage des paramètres

Grille sommaire, de taille comparable pour les cinq modèles, conformément au
périmètre réduit du cahier des charges. Le réglage se fait par validation
croisée interne sur la partie d'apprentissage de chaque pli, jamais sur la
partie d'évaluation.

Les configurations retenues sont consignées dans
[hyperparameter_grids.md](hyperparameter_grids.md), avec la seule grille dont
les résultats intermédiaires ont été conservés. Pour les quatre autres modèles,
l'étendue explorée n'a pas été enregistrée : manquement au présent article,
signalé et non corrigeable après coup.

## 8. Reproductibilité

Graine 42 partout : découpage, validation croisée, initialisation des modèles.
Environnement figé dans `requirements-lock.txt`. Carnets exécutables de bout en
bout.

Limite à énoncer : figer une graine rend un résultat reproductible, pas robuste.
C'est la validation croisée répétée de la section 3 qui répond à la robustesse.

## 9. Corrections postérieures au gel

Trois corrections apportées le 22 août 2026, avant que les résultats définitifs
du banc d'essai ne soient produits. Elles sont consignées ici parce que la
section 4 telle qu'elle était rédigée décrivait la première implémentation, qui
comportait un défaut.

**9.1. Réglage du seuil hors échantillon.** La section 4 prescrit un réglage sur
la partie d'apprentissage du pli. La première implémentation utilisait les
probabilités prédites par le modèle sur ces mêmes lignes, que le modèle venait
d'apprendre. Le réglage se fait désormais par validation croisée interne à 3
plis à l'intérieur du pli. La prescription de la section 4 est inchangée, son
implémentation est corrigée. Effet mesuré sur la forêt aléatoire : facteur 6,1
sur le coût.

**9.2. Détection des colonnes informatives sur l'apprentissage seul.** Elle
portait sur les 60 000 lignes, donc avant le découpage. Elle porte désormais sur
les 48 000 lignes d'apprentissage. Les listes obtenues sont identiques.

**9.3. Balayage vectorisé du seuil.** La boucle sur les probabilités observées
est remplacée par un tri et des sommes cumulées, et le cas dégénéré du
classifieur constant est désormais atteignable. Résultat inchangé sur les cas
non dégénérés, vérifié sur 200 tirages par `scripts/check_cost_function.py`.

Aucune de ces trois corrections ne modifie une prescription du protocole. Toutes
les trois précèdent les résultats rapportés dans `reports/`.
