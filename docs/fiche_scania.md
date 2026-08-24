# Fiche dataset : APS Failure at Scania Trucks

## 1. Origine
- Organisme producteur : Scania CV AB (Suède)
- Donateurs : Tony Lindgren et Jonas Biteus
- Année : septembre 2016
- Lien de téléchargement : dépôt UCI Machine Learning Repository, page "APS Failure at Scania Trucks"

## 2. Licence
- Licence exacte : **GNU General Public License, version 3 (GPLv3) ou ultérieure**
  Copyright Scania CV AB, 2016
  Lien du texte de licence : https://www.gnu.org/licenses/

## 3. Nombre d'exemples
- Entraînement : 60 000 (dont 59 000 classe négative, 1 000 classe positive)
- Test : 16 000
- Total : 76 000

## 4. Variables
- Nombre total : 171 attributs (dont la colonne `class`, donc 170 variables prédictives)
- Nature : entièrement **numériques et anonymisées**. Les noms de colonnes (`aa_000`,
  `ab_000`, etc.) ne renvoient à aucune grandeur physique nommée, pour raisons de
  confidentialité industrielle. 7 d'entre elles sont des variables « histogramme »
  (comptages répartis dans des classes de valeurs, ex. plusieurs bins de température),
  les autres sont des compteurs numériques simples.

## 5. Variable cible
- Nom de la colonne : `class`
- Signification précise de chaque classe : **attention, ce n'est pas « sain vs
  défaillant ».** Les deux classes concernent des camions **déjà en panne**, arrivés à
  l'atelier :
  - classe positive = panne d'un composant spécifique du système à air comprimé (APS)
  - classe négative = panne d'un autre système, sans lien avec l'APS
  Le dataset ne contient donc aucun camion en état de marche normal.

## 6. Proportion de la classe minoritaire
    Training : (60000, 171), positifs = 1,67 %, manquants global = 8,28 %
    Test      : (16000, 171), positifs = 2,34 %, manquants global = 8,36 %
  2,34 % sur un jeu de données antérieur ; à confirmer ou infirmer sur ton propre fichier.

## 7. Valeurs manquantes
- Encodage : valeurs manquantes notées `"na"` dans le fichier (texte), à passer en
  paramètre `na_values=["na"]` de `pd.read_csv`.
- Taux global : `df.isna().mean().mean()` : 0.08284746588693956 ~ 8.3 %
- Colonnes les plus touchées : `df.isna().mean().sort_values(ascending=False).head(10)` 

## 8. Métrique de coût
- **Fournie : oui.** Matrice de coût explicite du producteur :
  - Coût d'une **fausse alerte** (prédit positif, vrai négatif) = **10**
  - Coût d'une **panne manquée** (prédit négatif, vrai positif) = **500**
  - Coût total = 10 × (nb fausses alertes) + 500 × (nb pannes manquées)
  - Rapport de coût : 50:1 en défaveur du faux négatif.

## 9. Publications de référence
- Challenge industriel IDA 2016 (15th International Symposium on Intelligent Data
  Analysis) — trois meilleurs résultats annoncés par le producteur, avec leur coût total
  et le détail des erreurs de type 1 / type 2 :
  - Camila F. Costa, Mario A. Nascimento — coût 9 920 (542 erreurs type 1, 9 erreurs type 2)
  - Christopher Gondek, Daniel Hafner, Oliver R. Sampson — coût 10 900 (490 / 12)
  - Sumeet Garnaik, Sushovan Das, Rama Syamala Sreepada, Bidyut Kr. Patra — coût 11 480 (398 / 15)
  
## 10. Taille sur disque
43M	aps_failure_training_set.csv
12M	aps_failure_test_set.csv
