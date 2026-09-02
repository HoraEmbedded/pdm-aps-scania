# Fiche jeu de données : MetroPT-3

Candidat écarté. Fiche conservée comme pièce de justification du choix du jeu de données.

## 1. Origine

- Organisme producteur : INESC TEC, Laboratory of Artificial Intelligence and Decision
  Support, Porto, en collaboration avec la Faculté d'Économie et la Faculté des Sciences
  de l'Université de Porto
- Auteurs : Narjes Davari, Bruno Veloso, Rita P. Ribeiro, João Gama
- Collecte : février à août 2020. Publication associée : 2021 et 2022
- Source : UCI Machine Learning Repository, page "MetroPT-3"

## 2. Licence

Non vérifiée. La fiche technique du dépôt ne mentionne pas de licence explicite, et
aucune licence par défaut ne peut être supposée. Ce point aurait dû être tranché avant
tout usage : le filtre « licence autorisant un usage académique » est éliminatoire dans
la grille de sélection.

## 3. Volume

1 516 948 points de données, collectés à 1 Hz. Aucun découpage entraînement / test
officiel n'est fourni.

## 4. Variables

15 capteurs, plus l'horodatage. Contrairement au jeu Scania, les variables sont nommées
et non anonymisées.

- Analogiques, 7 mesures continues : TP2 (pression compresseur), TP3 (pression du panneau
  pneumatique), H1 (pression liée au filtre séparateur cyclonique), DV pressure (chute de
  pression au séchage), Reservoirs (pression aval des réservoirs), Motor Current (courant
  moteur), Oil Temperature (température d'huile).
- Digitales, 8 signaux tout ou rien : COMP, DV electric, TOWERS, MPG, LPS, Pressure
  Switch, Oil Level, Caudal Impulse.

## 5. Variable cible : motif d'élimination

**Le jeu de données n'est pas étiqueté.** Il n'existe aucune colonne indiquant la présence
ou l'absence de panne dans le fichier de capteurs.

Ce qui est fourni séparément est un tableau de rapports de panne : quatre événements de
fuite d'air, chacun avec une date de début, une date de fin, une sévérité et parfois une
date de maintenance associée.

Construire une variable cible supposerait donc de croiser l'horodatage des mesures avec
ces fenêtres, une ligne tombant dans une fenêtre devenant positive. C'est une étape de
préparation à part entière, dont le résultat conditionnerait tout le reste du projet.

Le filtre « étiquetage exploitable » de la grille de sélection est éliminatoire. Ce
candidat échoue au premier étage, sans avoir à être noté.

## 6. Proportion de la classe minoritaire

Non mesurable, faute de variable cible. Ordre de grandeur attendu si la cible était
construite : quatre événements de quelques jours sur sept mois de mesures à 1 Hz, soit un
déséquilibre probablement plus extrême encore que celui du jeu Scania. Cette estimation
n'a pas été vérifiée.

## 7. Valeurs manquantes

Le tableau de caractéristiques du dépôt indique « N/A », ce qui n'est pas une mesure. Non
vérifié sur le fichier, le candidat ayant été écarté avant cette étape.

## 8. Métrique de coût

Aucune. Contrairement au jeu Scania, le producteur ne fournit pas de matrice de coût. Elle
aurait dû être construite et justifiée, ce qui aurait affaibli la comparabilité des
résultats avec la littérature.

## 9. Publications de référence

- Davari, N., Veloso, B., Ribeiro, R. P., Pereira, P. M., Gama, J. (2021). Predictive
  maintenance based on anomaly detection using deep learning for air production unit in
  the railway industry. IEEE 8th International Conference on Data Science and Advanced
  Analytics. DOI 10.1109/DSAA53316.2021.9564181
- Veloso, B., Ribeiro, R. P., Pereira, P. M., Gama, J. (2022). The MetroPT dataset for
  predictive maintenance. Scientific Data, 9(1), 764. DOI 10.1038/s41597-022-01877-3
- Barros, M., Veloso, B., Pereira, P. M., Ribeiro, R. P., Gama, J. (2020). Failure
  detection of an air production unit in the operational context. IoT Streams for
  Data-Driven Predictive Maintenance, pages 61 à 74, Springer.
  DOI 10.1007/978-3-030-66770-2_5
