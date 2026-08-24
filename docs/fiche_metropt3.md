# Fiche dataset — MetroPT-3

## 1. Origine
- Organisme producteur : INESC TEC — Laboratory of Artificial Intelligence and Decision
  Support (Porto, Portugal), en collaboration avec la Faculté d'Économie et la Faculté
  des Sciences de l'Université de Porto
- Auteurs : Narjes Davari, Bruno Veloso, Rita P. Ribeiro, João Gama
- Année : données collectées février–août 2020 ; publication associée 2021/2022
- Lien de téléchargement : dépôt UCI Machine Learning Repository, page "MetroPT-3"

## 2. Licence
- **[À VÉRIFIER]** — la fiche technique fournie ne mentionne pas explicitement de
  licence. Aller voir directement le bas de la page UCI (section "License") avant de
  compléter ce champ ; ne pas supposer une licence par défaut.

## 3. Nombre d'exemples
- Total (dataset complet publié) : **1 5169 48** points de données, collectés à 1 Hz
  entre février et août 2020
- Entraînement / test : pas de découpage officiel fourni 

## 4. Variables
- Nombre total : **15 capteurs** (7 analogiques + 8 numériques/digitaux), plus
  l'horodatage
- Nature : **numériques et nommées** (pas anonymisées, contrairement à Scania) :
  - Analogiques (mesures continues) : TP2 (pression compresseur), TP3 (pression panneau
    pneumatique), H1 (pression liée au filtre séparateur cyclonique), DV pressure (chute
    de pression au séchage), Reservoirs (pression aval des réservoirs), Motor Current
    (courant moteur), Oil Temperature (température huile)
  - Digitales (signaux électriques on/off) : COMP, DV electric, TOWERS, MPG, LPS,
    Pressure Switch, Oil Level, Caudal Impulse

## 5. Variable cible
⚠️ **Point structurant, à ne pas manquer** : contrairement à Scania et Engine Health,
**ce dataset n'est PAS étiqueté nativement**. Il n'existe pas de colonne binaire
« défaillance oui/non » dans le fichier de capteurs.
- Ce qui est fourni séparément : un tableau de rapports de panne, avec des **fenêtres
  temporelles** de 4 événements de fuite d'air (« Air leak »), chacun avec une date de
  début, une date de fin, une sévérité (« High stress ») et parfois une date de
  maintenance associée.
- Construire une variable cible suppose donc de **croiser l'horodatage des mesures avec
  ces fenêtres de panne** (une ligne de capteur tombant dans une fenêtre = positive,
  sinon négative) — une étape de préparation à part entière, à documenter explicitement
  dans le pipeline (EF02).
- Nom de colonne cible : timestamp

## 6. Proportion de la classe minoritaire
- **[À CALCULER APRÈS CONSTRUCTION DE LA CIBLE]** — non mesurable avant l'étape 5
  ci-dessus. Une fois la cible construite, applique `value_counts(normalize=True)`.
  Attention : avec seulement 4 événements de quelques jours sur une période de 7 mois de
  mesures à 1 Hz, attends-toi à un déséquilibre potentiellement **encore plus extrême**
  que Scania — à vérifier, ne pas supposer.

## 7. Valeurs manquantes
- "Missing Values: N/A" dans le tableau de caractéristiques —
  

## 8. Métrique de coût
- Fournie : **non**. Aucune matrice de coût n'est donnée par le producteur, contrairement
  à Scania. À construire soi-même si besoin, ou à justifier son absence dans le rapport.

## 9. Publications de référence
- Davari, N., Veloso, B., Ribeiro, R.P., Pereira, P.M., Gama, J. (2021). *Predictive
  maintenance based on anomaly detection using deep learning for air production unit in
  the railway industry.* IEEE 8th International Conference on Data Science and Advanced
  Analytics (DSAA). DOI: 10.1109/DSAA53316.2021.9564181
- Veloso, B., Ribeiro, R.P., Pereira, P.M., Gama, J. (2022). *The MetroPT dataset for
  predictive maintenance.* Scientific Data, 9(1), 764. DOI: 10.1038/s41597-022-01877-3
- Barros, M., Veloso, B., Pereira, P.M., Ribeiro, R.P., Gama, J. (2020). *Failure
  detection of an air production unit in the operational context.* In IoT Streams for
  Data-Driven Predictive Maintenance, pp. 61–74. Springer. DOI: 10.1007/978-3-030-66770-2_5


## 10. Taille sur disque
