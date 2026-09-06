# Journal de bord

Une entrée par séance. Les chiffres définitifs sont ceux de `reports/`, ce
journal en conserve la chronologie et les difficultés rencontrées.

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
forêt aléatoire est un facteur 5,9 sur le coût, de 41 050 à 6 926.

La détection des colonnes informatives était effectuée sur les 60 000 lignes,
donc avant le découpage. Elle est désormais effectuée sur les 48 000 lignes
d'apprentissage seules. Les listes obtenues sont identiques, ce qui constitue un
argument de robustesse.

La recherche du seuil optimal était une boucle sur les probabilités observées.
Elle est désormais vectorisée par tri et sommes cumulées, et traite le cas
dégénéré du classifieur constant que l'ancienne version ne pouvait pas
atteindre.

Chaîne de préparation rejouée et vérifiée. Sept vérifications de la fonction de
coût passées, dont la reconstitution du score du vainqueur du concours 2016.

## 22 août 2026, première campagne du banc d'essai

Quatre modèles évalués sous protocole identique, campagne interrompue.

Difficulté rencontrée : le solveur du support à vecteurs ne converge pas au-delà
d'une certaine valeur du paramètre de régularisation. Le perceptron restait à
évaluer, et les deux modèles linéaires ont été réexécutés ensuite à `C=0.001`.
Les valeurs de cette campagne sont périmées ; celles qui font foi sont dans
`reports/benchmark.csv`.

## Séances suivantes, dates non consignées

Les entrées ci-dessous reconstituent le travail achevé, d'après les fichiers de
`reports/`. Les dates de séance n'ont pas été notées sur le moment et ne sont
pas reconstituables.

**Banc d'essai terminé** (`reports/benchmark.csv`). Cinq modèles et un témoin
constant, moyenne sur cinq plis. Échelle d'un pli : 9 600 lignes, 160 pannes,
règle constante de référence à 80 000.

| Modèle | Coût | Dispersion |
|---|---|---|
| Gradient boosting, profondeur 8 | 6 554 | 827 |
| Forêt aléatoire, 300 arbres | 6 926 | 804 |
| Perceptron Keras (64, 32) | 8 494 | 1 780 |
| SVM linéaire, C = 0,001 | 9 334 | 1 465 |
| Régression logistique, C = 0,001 | 9 596 | 1 222 |
| Témoin constant | 80 000 | 0 |

Les deux premiers sont séparés de 372 unités, en dessous de la marge de
départage de 2 000 fixée par le protocole. Cinq plis ne les départagent pas. La
famille des arbres bat la famille linéaire de 2 725 unités, ce qui franchit la
marge.

**Ablation et plan factoriel** (`reports/paired_comparisons.csv`,
`reports/runs/ablation_r6.csv`). Six comparaisons appariées sur validation
croisée répétée à 6 partitions, 30 mesures chacune. Écarts de 3 à 111 unités
pour des planchers de détection de 223 à 285. Aucune comparaison n'est
significative, y compris celles qui auraient valorisé le travail de
préparation.

**Quatre fonctions de perte sur le perceptron**
(`reports/loss_functions.csv`). Étalement de 8 454 à 9 124 : B à 8 454, la
référence A à 8 494, D à 8 622, C à 9 124. Aucun écart ne franchit le bruit, et
la variante retenue est la référence par principe de simplicité
(`reports/selected_perceptron_variant.json`).

Rien n'est affirmé sur leurs dispersions. Le rapport de variances entre A et D
vaut 2,77 sur quatre degrés de liberté, pour une probabilité de 0,34 :
l'observation sur la stabilité apparente des pertes portant le coût, notée dans
une version antérieure, est retirée.

## Désignation des finalistes, puis arbitrage

Deux décisions distinctes, sur deux jeux de données, avec deux étalons. À ne pas
confondre dans le rapport : les deux produisent un chiffre du même ordre, 396 et
900 unités.

**Désignation, sur les 48 000 lignes d'apprentissage**
(`reports/finalists.csv`). Le banc d'essai à cinq plis ne séparait pas les deux
premiers, 372 unités. La validation croisée répétée à 6 partitions donne une
différence appariée de 396 unités pour un plancher de détection mesuré de 354 :
les deux modèles sont séparables, et ce sont eux qui entrent en arbitrage.

Ce résultat ne tranche pas l'arbitrage. Il est mesuré sur les données mêmes sur
lesquelles toutes les décisions de modélisation ont déjà été prises.

**Arbitrage, ouverture unique des 12 000 lignes réservées**
(`reports/arbitration.csv`). Les cinq modèles y sont mesurés, l'ordre du banc
d'essai est confirmé, et le gradient boosting donne 6 410 contre 7 310 pour la
forêt et une référence constante de 100 000.

Mais l'écart de 900 unités est sous la marge de 2 000 du protocole : le coût ne
départage pas. Et le nombre de pannes manquées est à égalité, 6 de chaque côté,
l'écart venant des fausses alertes, 341 contre 431.

Le gradient boosting a été retenu sur la base des mesures répétées de l'étape
précédente et de sa dispersion plus faible entre partitions, 1 203 contre
1 307.

**Point à trancher avant le rapport.** La section 5 du protocole désigne le coût
comme critère d'arbitrage « et le seul ». Elle ne prévoit pas de critère de
départage subsidiaire. Retenir le gradient boosting sur la dispersion est
défendable, mais ce n'est pas l'application d'une règle écrite à l'avance, et le
rapport doit le dire ainsi. Deux options honnêtes : soit citer l'article du
cahier des charges qui prévoit une cascade de critères, s'il existe, soit écrire
que le protocole ne départageait pas ce cas et que le choix a été fait sur les
mesures répétées, hors protocole.

**La stabilité reste un critère faible.** La forêt a la plus faible dispersion
entre plis sur la partition unique, 804 contre 827, et le classement s'inverse
sur les 30 mesures. Les écarts sont de l'ordre de dix pour cent : lequel des
deux paraît le plus stable dépend de la dispersion que l'on lit.

**Mesure du surajustement à l'estimation d'évaluation**
(`reports/overfitting.csv`). Remise à l'échelle par 1,25 pour passer d'un pli
de 9 600 lignes aux 12 000 réservées, la validation croisée prédit 8 343 et les
lignes réservées donnent 6 410, soit −23 %. L'écart est de signe opposé au
surajustement attendu : aucun biais optimiste n'est détectable. Deux effets de
sens contraire se superposent, le surajustement de la sélection et le volume
d'apprentissage plus grand, et la mesure ne les sépare pas. À énoncer ainsi
dans le rapport plutôt que comme une absence de surajustement.

**Calibration des cinq modèles** (`reports/calibration.csv`,
`reports/figures/02_calibration.png`). Probabilités hors pli. Trois modèles
restent centrés sur le taux de base de 1,667 %, le gradient boosting à 0,0165,
la forêt à 0,0148, le SVM à 0,0167. Deux le dépassent d'un facteur trois à six,
le perceptron à 0,0596 et la régression logistique à 0,0982. Meilleur score de
Brier pour le gradient boosting, 0,0052.

Conséquence méthodologique, plus forte que l'argument initial de D-11 : la
pondération déplace les probabilités d'une manière qui dépend du modèle et n'est
pas prévisible a priori. Aucun seuil analytique unique ne s'applique donc aux
cinq modèles, ce qui impose de le mesurer.

Correction à propager : la colonne `ratio_to_bayes` ne doit plus être citée. La
dépondération suppose que la pondération a multiplié les cotes par cinquante, ce
qui ne vaut que pour deux modèles sur cinq. Appliquée aux trois autres elle
fabrique un artefact, le gradient boosting, le mieux calibré des cinq, en
ressortant à 457 fois le repère.

## Ouverture du jeu de test officiel

Une seule fois, sur le modèle figé au préalable (`reports/test_result.json`).

Coût 11 370 contre une référence de 156 250, soit 92,7 % d'économie. Détection
de 96,0 %, 360 pannes sur 375, 15 manquées, 387 fausses alertes, fiabilité des
alertes 0,482.

Face au podium 2016, sur le même fichier et la même métrique : 9 920, 10 900,
11 370, 11 480. Troisième sur quatre. La comparaison avec la quatrième place est
lisible : mêmes 15 pannes manquées, 387 fausses alertes contre 398.

À signaler, et non à masquer : le seuil figé n'est pas le moins cher sur ce
fichier. Le seuil que le recul préfère aurait donné 10 060. Le premier chiffre
est le résultat, le second est un diagnostic, et les deux sont dans le même
fichier.

## Sérialisation, démonstrateur et conteneur

Modèle figé et manifeste écrit, `models/final_model.json` : nom du modèle,
seuil, critère de décision, les 180 colonnes attendues et les mesures sur les
lignes réservées. `src/inference.py` réunit le modèle, son seuil et la chaîne
de préparation derrière une interface unique, de sorte que le démonstrateur
n'ait pas à savoir quelle famille de modèles se trouve dessous.

Point d'attention traité explicitement : l'alignement des colonnes. Un fichier
dont les colonnes arrivent dans un autre ordre, ou dont il manque une colonne,
produirait des prédictions absurdes sans aucun message d'erreur. C'est le mode
de défaillance le plus dangereux d'un démonstrateur parce qu'il est silencieux.
La méthode d'alignement réordonne, complète et consigne ce qui manquait.

Démonstrateur Streamlit, `app/streamlit_app.py`, avec le seuil réglable pour
rendre visible l'arbitrage économique.

**Temps de prédiction unitaire** (`reports/latency_single.csv`,
`reports/latency.csv`). 200 appels après dix appels de chauffe. Médiane
50,4 ms, 90e centile 110,6 ms, 95e centile 126,3 ms, maximum 183,9 ms, très en
dessous de la seconde exigée par ENF06. Les appels de chauffe
sont nécessaires : les premiers appels incluent les imports paresseux et
peuvent durer cent fois plus longtemps, ce qui donnerait l'impression que
l'exigence est en danger alors qu'elle ne l'est pas.

**Réintégration de ENF05** (`docs/amendment.md`). L'image Docker avait été
retirée du périmètre en application du plan de repli. La contrainte de
calendrier ayant disparu, le motif du retrait n'existe plus. Image multi-étages,
sans compilateur au stade final, exécution sous un compte non privilégié,
contrôle de santé. Compromis assumé sur les poids : non versionnés dans Git,
copiés dans l'image et publiés dans une distribution, récupérables par
`scripts/fetch_models.sh`.

**Vérification de reproductibilité** (`scripts/verify.py`). 23 contrôles qu'un
clone neuf doit passer : versions, métrique, présence des données, dimensions,
taille des groupes, emboîtement, somme de contrôle, chargement du prédicteur.
Code de sortie non nul en cas d'échec, donc automatisable.

## Séance de mise en cohérence

Constat : six incohérences entre les documents et les fichiers de résultats,
toutes de la même cause. Les documents avaient été rédigés contre des données
préparées qui n'existaient plus, la chaîne ayant changé depuis.

Règle adoptée et inscrite dans les deux README : les fichiers de `reports/`
font foi, aucun chiffre d'un document n'est saisi à la main, et tout nombre
cité par un document nomme le fichier qui le porte.

Corrections apportées. Les cinq lignes du banc d'essai et leurs dispersions.
L'écart entre les deux premiers, 372 et non 138. L'écart entre familles, 2 725
et non 2 725. La somme de contrôle, 313 696 et non 313 695. Le compte des
vérifications de la fonction de coût, sept et non six. Le passage sur la
stabilité de la forêt, réécrit. Les affirmations « le jeu de test n'a jamais été
ouvert » et « aucun modèle sérialisé et aucun démonstrateur », supprimées.

Trois chiffres de la documentation étaient par ailleurs démentis par la sortie
de `build_dataset.py` : l'emboîtement du groupe 2 donne 115 motifs et 3 860
exceptions et non 119 et 4 799 ; les médianes divergentes sont 85 et non 93 ;
les paires de colonnes parfaitement corrélées en absence se comptent par
dizaines et non deux.

**Défaut de nommage dans le plan factoriel.** Les conditions portaient des noms
qui décrivaient autre chose que leur contenu. `V1_no_flags` compte 171
colonnes, soit 180 moins 9 : ce qu'elle retire, ce sont les neuf indicatrices de
sous-bloc, et non la colonne `aa_000`. Le plan croise donc la profondeur et les
indicatrices, ce qui est un plan légitime, mais le libellé « compteur d'usage »
désigne `aa_000` partout ailleurs dans le projet. Écrire que la profondeur est
redondante avec le compteur d'usage serait faux, `aa_000` étant présente dans
les quatre conditions. Conditions renommées en `V1_no_flags` et `V1_raw`.

La question de la redondance entre la profondeur et `aa_000` reste donc ouverte
et non testée. Elle reçoit une réponse indirecte par l'importance par
permutation : `aa_000` au rang 1 sur 180, `depth_g1` au rang 102 avec 0,000078.

Défaut trouvé dans `scripts/rebuild.py` : il agrégeait tous les fichiers
`*_r6.csv`, donc mélangeait les finalistes aux variantes d'ablation dans
`experiments.csv`, et faisait apparaître la forêt aléatoire deux fois sous deux
noms, puisque la variante V1 est le jeu de variables complet. Les deux sources
sont désormais séparées.

Incident d'environnement à consigner : l'installation d'ONNX a remplacé NumPy
1.26.4 par 2.5.2, ce qui a cassé TensorFlow, et `pip freeze` a été exécuté
pendant cet état. Le fichier `requirements-lock.txt` a donc été écrit avec des
versions mutuellement incompatibles. C'est précisément le fichier dont toute la
fonction est la reproductibilité. À régénérer une fois l'environnement
rétabli. Enseignement : ne jamais figer un environnement sans vérifier d'abord
qu'il s'exécute.

**Suite de tests** (`tests/`). 40 tests répartis en cinq modules, construits à
partir des vérifications déjà existantes plutôt qu'inventés : la fonction de
coût, le chargement et le découpage, les variables d'absence, la chaîne de
préparation, le prédicteur, et la cohérence mutuelle des fichiers de résultats.
Ce dernier module est celui qui rend impossible la dérive qui a motivé la
séance.

## Reste à faire

Rapport final et support de soutenance.
