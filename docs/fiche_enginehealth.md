# Fiche dataset — Automotive Vehicles Engine Health Dataset (Kaggle)

## 1. Origine
⚠️ **Provenance à signaler dans le rapport, importante pour C1 (pertinence métier).**

Le fichier `engine_data.csv` circulant sous le nom « Automotive Vehicles Engine Health »
(Kaggle : `parvmodi/automotive-vehicles-engine-health-dataset`, publié avril 2023)
correspond **exactement**, colonne par colonne et jusqu'à la taille de fichier, au
dataset original **« Predictive Maintenance on Ship's Main Engine using AI »**, déposé
sur IEEE DataPort par Devabrat Mohakul le 16 novembre 2022 (DOI : 10.21227/g3za-v415).

Autrement dit : ce dataset décrit à l'origine un **moteur principal de navire**, pas un
véhicule automobile. Le nom Kaggle est un ré-étiquetage, pas la source primaire. C'est
exactement le genre d'écart qu'un jury peut pointer si tu écris « domaine automobile »
sans vérification — à documenter honnêtement dans la fiche et à répercuter dans la note
C1 (le domaine réel est naval/moteur thermique générique, pas automobile spécifiquement,
et encore moins freinage).

- Organisme producteur (source primaire) : Devabrat Mohakul, via IEEE DataPort
- Miroir utilisé : Kaggle, utilisateur `parvmodi`
- Année : dataset créé le 16 novembre 2022 (IEEE DataPort), publié sur Kaggle en avril 2023
- Lien de téléchargement : https://www.kaggle.com/datasets/parvmodi/automotive-vehicles-engine-health-dataset
  (source primaire : https://ieee-dataport.org/open-access/predictive-maintenance-ships-main-engine-using-ai)

## 2. Licence
- CC0 : Public Domaine
 
## 3. Nombre d'exemples
- Total : **19 535** lignes (mesuré directement sur ton fichier)
- Pas de split train/test séparé fourni — un seul fichier `engine_data.csv`.

## 4. Variables
- Nombre total : 7 colonnes (6 variables prédictives + 1 cible)
- Nature : **entièrement numériques**, aucune anonymisation (noms de capteurs explicites) :
  - `Engine rpm` (int64)
  - `Lub oil pressure` (float64)
  - `Fuel pressure` (float64)
  - `Coolant pressure` (float64)
  - `lub oil temp` (float64)
  - `Coolant temp` (float64)
  - `Engine Condition` (int64) — variable cible

## 5. Variable cible
- Nom de la colonne : `Engine Condition`
- Signification précise de chaque classe : **ambiguë dans la documentation source**.
  Le producteur décrit uniquement l'objectif comme « prédire si le moteur est bon ou
  mauvais » (*"Engine is Good or Bad"*), sans préciser explicitement quelle valeur (0
  ou 1) correspond à quel état. Sur la page IEEE DataPort elle-même, un lecteur a posé
  la question sans obtenir de réponse claire de l'auteur.
  - Convention généralement retenue par les republications tierces : 0 = normal,
    1 = défaillant — **à traiter comme une hypothèse à vérifier, pas un fait établi**,
    et à signaler comme telle dans le rapport si tu la retiens.

## 6. Proportion de la classe minoritaire
- Classe 0 : 7 218 exemples (**36,95 %**)
- Classe 1 : 12 317 exemples (**63,05 %**)
- **Aucun déséquilibre marqué** ici (à l'inverse de Scania, où la classe positive
  pèse 1,7 %). C'est un point de contraste net entre les deux candidats pour C3
  (déséquilibre de classes).

## 7. Valeurs manquantes
- Taux global : **0 %**
- Colonnes les plus touchées : aucune — 0 % de valeurs manquantes sur les 7 colonnes,
  sans exception.

## 8. Métrique de coût
- Fournie : **non**. Aucune matrice de coût n'accompagne ce dataset.

## 9. Publications de référence
- **[À COMPLÉTER]** — aucune publication scientifique n'a été identifiée citant
  spécifiquement ce dataset sous son nom Kaggle ou sous son nom IEEE DataPort d'origine
  au moment de cette recherche. Une citation directe existe sur IEEE DataPort
  (référencée par https://doi.org/10.1177/14750902251400373, déc. 2025) — à vérifier son
  contenu et son score avant de la citer dans le rapport.

## 10. Taille sur disque
- 1 301 801 octets (**≈ 1,24 Mo**)