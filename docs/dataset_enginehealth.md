# Fiche jeu de données : Automotive Vehicles Engine Health

Candidat écarté. Fiche conservée comme pièce de justification du choix du jeu de données,
et parce que la vérification de provenance qu'elle documente est un résultat en soi.

## 1. Origine, et un ré-étiquetage

Le fichier `engine_data.csv` diffusé sur Kaggle sous le nom « Automotive Vehicles Engine
Health Dataset », compte `parvmodi`, publié en avril 2023, correspond colonne par colonne
et jusqu'à la taille de fichier au dépôt « Predictive Maintenance on Ship's Main Engine
using AI », déposé sur IEEE DataPort par Devabrat Mohakul le 16 novembre 2022,
DOI 10.21227/g3za-v415.

**Ce jeu de données décrit un moteur principal de navire, pas un véhicule automobile.** Le
nom employé sur Kaggle est un ré-étiquetage, et Kaggle n'est pas la source primaire.

Trois conséquences ont été tirées de cette vérification.

1. La note de pertinence métier de ce candidat tombe au minimum : le domaine réel est
   naval, et le composant étudié n'a aucun rapport avec le freinage.
2. Le projet perd la seule solution de repli située dans le domaine automobile.
3. La section du cahier des charges qui présente ce jeu comme automobile devient
   inexacte, et une mise à jour formelle du document a été demandée.

Enseignement retenu : une plateforme de diffusion n'est pas une source. Le nom sous lequel
un jeu de données circule ne garantit ni son contenu ni son domaine d'application.

- Source primaire : Devabrat Mohakul, IEEE DataPort,
  https://ieee-dataport.org/open-access/predictive-maintenance-ships-main-engine-using-ai
- Miroir utilisé :
  https://www.kaggle.com/datasets/parvmodi/automotive-vehicles-engine-health-dataset

## 2. Licence

CC0, domaine public.

## 3. Volume

19 535 lignes, mesurées sur le fichier. Aucun découpage entraînement / test fourni : un
seul fichier `engine_data.csv`.

## 4. Variables

7 colonnes, soit 6 variables prédictives et une cible. Toutes numériques, noms de capteurs
explicites.

| Colonne | Type |
|---|---|
| `Engine rpm` | int64 |
| `Lub oil pressure` | float64 |
| `Fuel pressure` | float64 |
| `Coolant pressure` | float64 |
| `lub oil temp` | float64 |
| `Coolant temp` | float64 |
| `Engine Condition` | int64, cible |

## 5. Variable cible

Colonne `Engine Condition`. **Son sens est ambigu dans la documentation source.** Le
producteur décrit l'objectif comme prédire si le moteur est bon ou mauvais, sans préciser
quelle valeur correspond à quel état. Sur la page IEEE DataPort, un lecteur a posé la
question sans obtenir de réponse claire.

La convention généralement retenue par les republications tierces est 0 pour normal et 1
pour défaillant. Elle est à traiter comme une hypothèse non vérifiée, pas comme un fait.

## 6. Proportion de la classe minoritaire

| Classe | Effectif | Part |
|---|---|---|
| 0 | 7 218 | 36,95 % |
| 1 | 12 317 | 63,05 % |

Aucun déséquilibre marqué, à l'inverse du jeu Scania où la classe positive pèse 1,67 %.
C'est le point de contraste décisif entre les deux candidats : le déséquilibre de classes
est l'une des trois difficultés que le projet doit traiter, et ce jeu ne la présente pas.

## 7. Valeurs manquantes

Aucune. 0 % sur les 7 colonnes, sans exception.

## 8. Métrique de coût

Aucune matrice de coût n'accompagne ce jeu de données.

## 9. Publications de référence

Aucune publication scientifique citant spécifiquement ce jeu de données n'a été
identifiée, ni sous son nom Kaggle ni sous son nom IEEE DataPort. Une citation existe sur
IEEE DataPort, référencée par DOI 10.1177/14750902251400373, décembre 2025, dont le
contenu n'a pas été vérifié et qui n'est donc pas citée dans le rapport.

## 10. Résultat de la notation

Écarté au second étage de la grille, par la notation et non par un filtre : 12 points
contre 34 pour le jeu Scania. La première version du livrable l'éliminait dès le premier
étage, sur une réserve portée à la colonne « données réelles », ce qui était incorrect :
ce sont bien des données réelles, réellement collectées sur un moteur.

## 11. Taille sur disque

1 301 801 octets, soit environ 1,24 Mo.
