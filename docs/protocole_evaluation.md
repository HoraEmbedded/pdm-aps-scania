# Protocole d'évaluation des modèles
## Version 1.0, figée le [date]

**Ce document est figé. Toute modification postérieure à l'entraînement d'un
modèle impose de réentraîner l'ensemble des modèles.**

---

## 1. Données d'entrée

Tableaux produits à l'étape 3.6 : `data/processed/X_app_final.csv` et
`X_val_final.csv`, de dimensions 48 000 × 180 et 12 000 × 180.

Chaîne de préparation, rejouable par les objets sérialisés dans
`data/processed/` : découpage stratifié de graine 42, extraction de la variable
de profondeur et des neuf indicatrices, imputation à zéro pour les huit colonnes
du groupe 1 et par la médiane pour les autres, normalisation des 170 colonnes de
mesure. Toutes les quantités estimées proviennent de la partie d'apprentissage
seule.

Somme de contrôle du tableau final : 313 695,00.

## 2. Rôle des deux ensembles

**Les 48 000 lignes d'apprentissage** portent toute la phase de comparaison. Les
décisions de modélisation, réglage des paramètres, choix du modèle final, tests
sur les indicatrices et sur l'hypothèse H1, se prennent exclusivement sur leur
validation croisée.

**Les 12 000 lignes de validation ne sont pas consultées pendant les semaines 4
à 7.** Elles sont ouvertes une seule fois, en fin de semaine 7, pour arbitrer
entre les modèles finalistes et mesurer l'écart entre le score de validation
croisée et un score obtenu sur des données n'ayant participé à aucune décision.
Cet écart quantifie mon propre surajustement et sera rapporté comme tel.

**Le jeu de test officiel reste fermé jusqu'à l'étape 6.4.**

## 3. Découpage d'évaluation

Validation croisée stratifiée à 5 plis sur les 48 000 lignes, graine 42.
Chaque pli d'évaluation contient environ 9 600 lignes et 160 pannes.

## 4. Traitement du coût asymétrique

Conformément à la décision D-11 :

- pondération des classes à 50:1 à l'entraînement, valeur fixée depuis la matrice
  de coût et non depuis les fréquences observées ;
- seuil de décision réglé empiriquement par minimisation du coût total.

**Le seuil est réglé à l'intérieur de chaque pli, sur la partie d'apprentissage de
ce pli uniquement, puis appliqué à sa partie d'évaluation.** Un seuil réglé
globalement puis mesuré en validation croisée ferait contribuer chaque pli au
choix du seuil qui l'évalue.

Ce traitement est appliqué de façon strictement identique aux cinq modèles.

## 5. Mesures rapportées

Pour chaque modèle, **moyenne sur les 5 plis et écart type**, sans exception :

1. **Coût total de Scania.** C'est le critère d'arbitrage, et le seul.
2. Taux de détection (rappel).
3. Fiabilité des alertes (précision).
4. Aire sous la courbe ROC.
5. Détail des erreurs : VP, FP, FN, VN.
6. Seuil optimal retenu, et sa valeur dépondérée comparée au repère analytique
   de 1,96 %.

L'écart type n'est pas décoratif : avec environ 900 unités de bruit sur la
moyenne, deux modèles séparés de moins de 2 000 unités ne sont pas départageables.

Le F1 et l'exactitude peuvent être reportés pour information mais ne servent
jamais à départager deux modèles.

## 6. Repères de comparaison

Trois lignes accompagnent le tableau final :

| Repère | Valeur | Niveau de confiance |
|---|---|---|
| Règle naïve, calculée par nos soins | 156 250 sur le test | Incontestable |
| Challenge IDA 2016, obtenu à l'aveugle | 9 920 à 11 480 | Solide |
| Meilleur publié depuis 2016 | 3 440 | À citer avec réserve |

## 7. Réglage des paramètres

Grille sommaire, de taille comparable pour les cinq modèles, conformément au
périmètre réduit du cahier des charges. La grille de chaque modèle est déclarée
avant l'entraînement dans `docs/grilles.md` et ne change plus.

Le réglage se fait par validation croisée interne sur la partie d'apprentissage de
chaque pli, jamais sur la partie d'évaluation.

## 8. Reproductibilité

Graine 42 partout : découpage, validation croisée, initialisation des modèles.
Environnement figé dans `requirements.txt`. Carnets exécutables de bout en bout.


