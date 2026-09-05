# Décisions techniques

Les décisions numérotées sont celles adoptées en cours de projet. Ce document
porte le raisonnement ; le code porte la mise en oeuvre. Les commentaires du
code renvoient ici plutôt que de reproduire l'argumentation.

## La référence à battre dépend du fichier

Ce point précède les décisions numérotées, parce qu'il conditionne la lecture de
tous les coûts du projet.

Deux règles constantes sont possibles, et la moins chère des deux est la
référence. Laquelle gagne n'est pas une propriété du problème : cela dépend du
taux de positifs, comparé au taux d'équilibre de 1,96 % auquel les deux règles
coûtent la même chose.

| Fichier | Taux de positifs | Ne rien signaler | Tout signaler | Référence |
|---|---|---|---|---|
| Test officiel, 16 000 lignes | 2,34 % | 187 500 | 156 250 | tout signaler |
| Validation, 12 000 lignes | 1,67 % | 100 000 | 118 000 | ne rien signaler |

La règle la moins chère s'inverse entre les deux. Sur le test, au-dessus du taux
d'équilibre, envoyer toute la flotte au contrôle est la référence ; sur un
découpage du fichier d'apprentissage, en dessous, ne rien signaler l'est.

Conséquence pratique : annoncer un chiffre de référence pour ce jeu de données
sans préciser sur quel fichier il est mesuré n'a pas de sens.
`cost.constant_rule_costs` renvoie les deux coûts, la règle gagnante et le taux
d'équilibre, plutôt que de laisser le lecteur choisir.

## D-09. L'absence des valeurs porte de l'information

**Constat.** Le taux d'absence par colonne, mesuré séparément dans chaque
classe, ne se répartit pas au hasard. Sur les 170 colonnes de mesure, 64
présentent un écart supérieur à 10 points entre les deux classes, réparties en
deux groupes de sens opposés.

- Groupe 1, 8 colonnes : absentes surtout chez les pannes non-APS.
- Groupe 2, 56 colonnes : absentes surtout chez les pannes APS.
- 106 colonnes muettes : écart inférieur au seuil.

**Le seuil de 10 points a été écrit avant le calcul qu'il sélectionne.** C'est
une mesure de discipline, pas un argument de robustesse, et il faut distinguer
les deux côtés.

Du côté du groupe 1, le seuil tombe dans une vraie rupture : le huitième écart
le plus grand vaut 0,323 et le neuvième 0,026, soit un facteur supérieur à dix.
Tout seuil placé entre les deux sélectionne exactement les mêmes huit colonnes,
le choix de la valeur est donc sans effet.

Du côté du groupe 2, il n'y a pas de rupture comparable. Le seuil y est un choix
déclaré et rien de plus. `missingness.gap_cliff` mesure les deux côtés au lieu
de laisser l'affirmation sans preuve.

**L'emboîtement du groupe 1.** Prises par taux d'absence croissant, les 8
colonnes du groupe 1 vérifient une propriété stricte : dès qu'une colonne est
absente, toutes les suivantes le sont aussi. Neuf motifs sont observés sur 256
possibles, sans aucune exception, et neuf est exactement le nombre de motifs
qu'un bloc emboîté de huit colonnes peut produire.

Compter les motifs n'est pas une preuve. Neuf motifs quelconques sur 256
donneraient le même compte. C'est le test explicite du motif interdit "10" qui
établit l'emboîtement.

La conséquence est la partie utile : un seul entier, le nombre de colonnes
absentes, résume tout le bloc sans perte. C'est la variable `depth_g1`.

**Le groupe 2 n'est pas emboîté, et c'est pour cela qu'il est traité
autrement.** Le même test appliqué à ses 56 colonnes échoue : 115 motifs
observés là où un bloc emboîté en produirait 57, et 8 % des lignes violent la
règle. Une variable de profondeur sur un bloc non emboîté ramènerait des motifs
réellement différents sur le même entier. Le groupe 2 reçoit donc une
indicatrice par palier de taux d'absence, pas une profondeur.

**Les sous-blocs du groupe 2.** Les 56 colonnes se regroupent en 9 paliers de
taux d'absence identique à trois décimales. Une indicatrice par palier, et non
une par colonne, ce qui ramène 56 colonnes à 9 variables.

L'indicatrice lit une colonne représentative par palier, la première par ordre
alphabétique, afin que le résultat ne dépende pas de l'ordre dans lequel les
colonnes arrivent. Ce raccourci n'est légitime que si les colonnes d'un palier
bougent ensemble, donc l'accord est mesuré et non supposé :
`missingness.sub_block_homogeneity` renvoie, pour chaque palier, la part des
lignes où toutes ses colonnes sont dans le même état. Sur le plus gros palier,
l'accord dépasse 99,9 %.

**Deux colonnes sont des doublons d'absence.** `ab_000` et `cr_000` ont des
indicateurs d'absence corrélés à exactement 1,00 : elles portent deux fois la
même information de manque. Sans effet sur l'ajustement, mais à connaître avant
de lire une importance de variable, qui se répartira arbitrairement entre les
deux. `missingness.duplicate_absence_columns` les détecte.

**Détection sur l'apprentissage seul.** Elle était initialement effectuée sur
les 60 000 lignes, donc avant le découpage. Elle porte désormais sur les 48 000
lignes d'apprentissage. Les listes obtenues sont identiques, ce qui constitue un
argument de robustesse a posteriori.

## Le découpage 80/20 stratifié

**La taille.** Ce que la partie de validation doit mesurer est un taux de
détection, et la précision de cette mesure dépend du nombre de pannes qu'elle
contient, pas du nombre de lignes. À 20 %, la validation contient 200 pannes,
pour une erreur type d'environ 2,1 points sur un taux de détection de 90 %.
Descendre à 10 % la porterait à 3 points, sur une grandeur dont les écarts entre
modèles se comptent en fractions de point.

**La stratification.** Sans elle, le taux de positifs de la partie de validation
est lui-même une variable aléatoire. Sur 500 tirages non stratifiés, il varie de
1,36 % à 1,98 %, pour un écart type de 0,106 point.

Cet intervalle enjambe le taux d'équilibre de 1,96 %. Un tirage non stratifié
peut donc changer laquelle des deux règles constantes est la référence à battre,
ce qui rendrait la référence elle-même dépendante du tirage. C'est la raison de
la stratification, et elle est plus forte que l'argument habituel de
représentativité.

## D-10. Imputation différenciée

**Le groupe 1 est imputé à zéro, les autres colonnes par la médiane.**

Les colonnes du groupe 1 sont absentes pour les camions les moins utilisés. La
lecture de `aa_000`, seule colonne complète du fichier et compteur d'usage, le
montre à classe constante : à profondeur maximale la médiane d'usage s'effondre
de plus de deux ordres de grandeur par rapport aux profondeurs intermédiaires.
La relation n'est pas monotone à l'extrémité basse, et la table est donc publiée
telle quelle dans le carnet 01 plutôt que résumée par un seul rapport.

La médiane des 18 % de lignes qui portent une valeur est la médiane d'une
population fortement sollicitée, pas de la population générale. Remplir 82 %
d'une colonne avec cette constante élevée affirme le contraire de ce que les
données indiquent. Zéro existe déjà légitimement dans le fichier, la valeur
n'est donc pas artificielle.

**La charge d'imputation, pour situer l'enjeu.** 28 colonnes sont imputées à
plus de 10 %, 10 à plus de 30 %, 8 à plus de 50 %. Les 8 dernières sont
exactement le groupe 1, ce qui explique que la décision porte sur elles.

**La variable de profondeur et les 9 indicatrices ne sont pas normalisées.**
Leur amplitude est déjà du bon ordre, et les normaliser rendrait illisible
l'interprétation des coefficients des modèles linéaires.

**Une colonne est constante après préparation.** `cd_000` ne porte qu'une seule
valeur distincte dans tout le fichier d'apprentissage, 1 209 600, sur les 98,9 %
de lignes où elle est renseignée. Elle est sans pouvoir prédictif et son écart
type nul est signalé par `build_dataset.py` plutôt que découvert plus tard sous
la forme d'un avertissement de division par zéro.

**Toutes les quantités sont estimées sur l'apprentissage seul.**
`scripts/build_dataset.py` en apporte la preuve inverse : sur 180 colonnes, 93
ont une médiane d'apprentissage différente de la médiane calculée sur les deux
parties réunies, et l'écart type mesuré sur la validation vaut 0,897 et non 1.
Si ces deux vérifications donnaient l'égalité, il y aurait fuite.

**La chaîne est écrite à la main plutôt qu'avec `ColumnTransformer`.** Le carnet
d'exploration l'avait d'abord construite avec `ColumnTransformer`, ce qui
fonctionne mais renvoie un tableau nu dont les colonnes sortent dans l'ordre des
transformateurs : il fallait reconstruire à la main la liste des colonnes et
l'index à chaque appel. La version écrite à la main conserve le `DataFrame` et
son index, et l'ordre des colonnes est celui de l'entrée.

## D-11. Le coût n'entre qu'une seule fois dans la chaîne

**Le problème.** Deux mécanismes corrigent l'asymétrie des coûts, et ils sont
alternatifs, pas cumulables.

1. Pondérer les classes à l'entraînement dans le rapport des coûts, soit 50:1.
2. Abaisser le seuil de décision au seuil de Bayes, soit 10 / (10 + 500) =
   1,96 %.

Les appliquer tous les deux revient à multiplier les cotes par 50 puis à
décider comme si elles ne l'avaient pas été, pour un rapport effectif de 2 501
contre 1. Le modèle alerterait alors sur presque tout, et son coût remonterait
vers celui de la règle constante.

**La décision.** Le coût entre une seule fois, par la pondération. Le seuil est
ensuite mesuré, par minimisation exhaustive du coût, et non déduit.

**La pondération vient du rapport des coûts, pas des fréquences.** Les
fréquences observées donneraient 59:1. La valeur retenue est 50:1, parce que
c'est le rapport de coût qui définit ce que l'on cherche à minimiser.

**La dépondération.** Comparer le seuil mesuré au repère analytique de 1,96 %
n'a de sens qu'après avoir annulé la pondération. Une pondération de facteur r
multiplie les cotes par r, donc le modèle produit
`p_w = r*p / (1 + (r - 1)*p)`. La fonction `cost.unweight` inverse cette
relation. Vérification : le seuil de Bayes de 1,96 % tombe exactement sur 0,5
sur l'échelle pondérée, ce que teste `check_cost_function.py`.

**Le seuil de Bayes reste un diagnostic.** Il n'est jamais utilisé comme point
de fonctionnement. Un seuil mesuré très éloigné de 0,5 sur l'échelle pondérée
signale un défaut de calibration, ce qui est une information utile, mais pas une
consigne. Sur la régression logistique, les seuils retenus par pli valent 0,331
à 0,544 pour une moyenne de 0,439, soit 0,0154 après dépondération contre 0,0196
attendu : le modèle est légèrement sous-confiant, sans plus.

## L'effet du modèle et l'effet de la préparation ne se comparent pas

Deux écarts sont mesurés dans ce projet, et il est tentant d'en faire un rapport.
Il ne faut pas.

**L'écart entre familles de modèles est mesurable.** Moyenne des deux modèles à
base d'arbres, 6 645, contre moyenne des deux modèles linéaires, 9 462 : 2 725
unités. C'est une différence de moyennes entre familles, pas une comparaison
appariée, mais l'écart dépasse largement les dispersions individuelles et la
marge de départage de 2 000 unités.

**L'écart apporté par la préparation n'est pas mesurable.** La comparaison
appariée V1 contre V0 donne 220 unités pour une erreur type de 329. Elle est
déclarée non significative, comme les cinq autres.

**Le rapport entre les deux n'existe donc pas.** Écrire que la préparation pèse
treize fois moins que le choix du modèle, 2 725 contre 220, traite un nombre non
significatif comme une quantité. Le 220 n'est pas un petit effet mesuré, c'est
un effet dont la mesure ne permet pas de dire s'il est positif, nul ou négatif.
La formulation correcte est dissymétrique : le choix de la famille de modèles
produit un effet mesurable, celui de la préparation non, à cette taille
d'échantillon.

Même prudence pour l'interprétation qui suivait : que des travaux publiés
suppriment les colonnes très incomplètes sans dégradation notable est une
observation sur ces travaux, pas une conséquence de notre résultat nul.

## Le réglage du seuil hors échantillon

Cette correction n'a pas de numéro de décision, elle a été apportée le 22 août
2026 en même temps que deux autres.

**Le défaut.** Le seuil était réglé sur les probabilités prédites par le modèle
sur les lignes d'entraînement de son propre pli. Une forêt aléatoire prédit
presque parfaitement ses propres données d'entraînement : le seuil trouvé était
excellent en échantillon et arbitraire en dehors.

**L'ampleur du défaut.** Réglé en échantillon, le seuil dégénérait : le modèle
signalait la totalité des camions, pour un taux de détection de 1,0, zéro panne
manquée et un coût de 94 400 par pli. Ce nombre n'est pas quelconque, c'est
exactement le coût de la règle constante "tout signaler" à l'échelle d'un pli,
9 440 non-APS à 10 unités. Le modèle avait donc cessé de décider. Un résultat
parfait sur le rappel et sans valeur sur le critère qui compte.

**Sur la forêt aléatoire**, dont le seuil ne dégénérait pas complètement, le
coût passe de 41 050 à 6 926, soit le facteur 6,1.

**La correction.** Le seuil est réglé sur des probabilités hors échantillon,
obtenues par une validation croisée interne à 3 plis à l'intérieur de chaque pli
externe.

**L'ancienne version est conservée.** Le paramètre
`evaluate(..., out_of_sample_threshold=False)` reproduit le comportement fautif.
Ce n'est pas un reste de code : c'est la comparaison entre les deux qui produit
le facteur 6,1, et elle doit rester rejouable.

## Le balayage vectorisé du seuil

La recherche du seuil optimal était une boucle sur les probabilités observées,
en O(n²). Elle est désormais vectorisée : un tri par probabilité décroissante,
puis les effectifs de la matrice de confusion lus sur des sommes cumulées, en
O(n log n).

Deux points la rendent moins évidente qu'il n'y paraît.

**Les ex aequo.** Seule la dernière occurrence d'une valeur de probabilité est
un point de coupure valide, puisque toutes les lignes qui partagent cette
probabilité sont signalées ensemble.

**Le cas dégénéré.** Ne rien signaler du tout n'est jamais un point de coupure
observé, mais c'est parfois la décision la moins chère, notamment pour un
classifieur constant. Ce cas est traité explicitement ; l'ancienne boucle ne
pouvait pas l'atteindre.

## Les pertes sur mesure

Le réseau de neurones est le seul modèle du banc d'essai dont l'objectif
d'apprentissage puisse être réécrit librement. Les quatre modèles classiques ont
le leur imposé par la méthode qui les définit. C'est la raison d'être propre du
réseau dans ce projet, au-delà de l'obligation du cahier des charges, et
`src/losses.py` est le module où cette liberté est exercée.

Trois pertes sont implémentées : entropie croisée pondérée par le coût, perte
focale, et la combinaison des deux. Lorsque la perte porte déjà la matrice de
coût, `KerasPerceptron(weighted=False)` est obligatoire, sinon le rapport entre
à nouveau deux fois dans la chaîne, ce qui est exactement l'erreur que D-11
corrige.

Résultat mesuré : les quatre variantes s'étalent de 8 368 à 9 210 pour des
écarts types de 690 à 1 840. Aucun écart ne franchit le bruit. La configuration
de référence a été conservée par principe de simplicité
(`reports/loss_functions.csv`).
