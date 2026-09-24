# Maintenance prédictive sur le jeu de données APS Scania

Classification de pannes sensible au coût sur le circuit d'air comprimé de camions Scania. Cinq familles de modèles comparées sous protocole figé avant tout entraînement. Ouverture unique du jeu de test officiel.

Projet de 4e année du cycle ingénieur, 10 semaines, encadré. English version: [README.md](README.md).

## Description

Le travail compare cinq familles de modèles de classification pour détecter les défaillances du circuit d'air comprimé de poids lourds. Données industrielles publiées par Scania en 2016.

Le protocole est écrit, daté et figé avant le premier entraînement. Le jeu de test officiel n'est ouvert qu'une fois, sur un modèle déjà figé, seuil de décision compris.

## Problème

Les camions du jeu de données sont déjà en atelier. La question n'est pas de savoir s'ils sont en panne, mais si la panne vient du circuit d'air comprimé (APS) ou d'un autre organe.

Trois propriétés commandent toutes les décisions de conception :

| Propriété | Valeur mesurée |
|---|---|
| Déséquilibre | 1,67 % de positifs en apprentissage, 2,34 % en test |
| Absences | 8,33 % de cellules vides, 8 colonnes au-delà de 65 % |
| Coût asymétrique | Fausse alerte 10, panne manquée 500, soit 50 contre 1 |

L'exactitude n'est pas la métrique. La métrique est le coût total Scania. La référence à battre est la moins chère des deux règles constantes, et elle change selon le fichier.

| Fichier | Ne rien signaler | Tout signaler | Référence |
|---|---|---|---|
| Test officiel, 16 000 lignes | 187 500 | 156 250 | tout signaler |
| Réservé, 12 000 lignes | 100 000 | 118 000 | ne rien signaler |

## Solution

Trois mesures, dans l'ordre prescrit. Aucune mesure postérieure n'informe une mesure antérieure.

**1. Banc d'essai, 5 plis sur 48 000 lignes.** Compare les cinq familles sous protocole unique.

**2. Validation croisée répétée, 6 partitions, 30 mesures.** Désigne les deux finalistes. Écart apparié de 396 unités, plancher de détection 354.

**3. Arbitrage, 12 000 lignes réservées, ouvertes une fois.** Gradient boosting 6 410, forêt 7 310. Écart 900 sous la marge de 2 000. Modèle retenu : gradient boosting.

**Trois points d'ingénierie :**

- **L'absence traitée comme signal.** 8 colonnes absentes en cascade parfaite (9 motifs sur 256, aucune exception) résumées en une profondeur d'absence. 56 colonnes non emboîtées regroupées en 9 indicatrices par palier. Variables construites avant imputation, qui détruirait le motif.
- **Le rapport de coût entre une seule fois.** Pondération 50:1 pour porter le coût, seuil mesuré par balayage exhaustif. Sinon rapport effectif de 2 501:1.
- **Le seuil réglé hors échantillon.** Validation croisée interne dans chaque pli. Forêt aléatoire passée de 41 050 à 6 926, facteur 5,9.

## Modèles utilisés

Cinq familles, réglage volontairement sommaire et d'effort comparable.

| Modèle | Configuration |
|---|---|
| Gradient boosting | XGBoost, profondeur 8, taux 0,1, 300 arbres |
| Forêt aléatoire | scikit-learn, 300 arbres, profondeur libre |
| Perceptron Keras | 2 couches (64, 32), abandon 0,3, Adam 10⁻³ |
| SVM linéaire | LinearSVC C=0,001, calibration de Platt à 3 plis |
| Régression logistique | liblinear C=0,001, 2 000 itérations |

## Résultats

**Banc d'essai, 5 plis :**

| Modèle | Rappel | Précision | AUC-PR | AUC-ROC |
|---|---|---|---|---|
| Gradient boosting | 95,4 % | 35,3 % | 0,878 | 0,989 |
| Forêt aléatoire | 96,3 % | 28,2 % | 0,830 | 0,986 |
| Perceptron (64, 32) | 94,0 % | 29,4 % | 0,760 | 0,985 |
| SVM linéaire | 92,0 % | 33,9 % | 0,757 | 0,981 |
| Régression logistique | 92,8 % | 28,3 % | 0,744 | 0,977 |
| Témoin constant | 0,0 % | - | 0,017 | 0,500 |

**Test officiel, ouverture unique :**

| | |
|---|---|
| Coût | **11 370** |
| Référence constante | 156 250 |
| Économie | **92,7 %** |
| Rappel | 96,0 % (360/375) |
| Pannes manquées | 15 |
| Fausses alertes | 387 |

Podium IDA 2016, même test, même métrique : 9 920, 10 900, **11 370**, 11 480. Troisième sur quatre. À détection égale avec la quatrième place (15 pannes manquées), les 110 unités d'écart sont entièrement des fausses alertes (387 contre 398).

Chiffres : [reports/test_result.json](reports/test_result.json).

## Déploiement

Modèle exposé via démonstrateur Streamlit, containerisé, puis porté sur Raspberry Pi 4.

**Chaîne d'inférence.** La classe `Predictor` rassemble modèle, seuil et préparation derrière une interface unique. Un manifeste sert de contrat : seuil 0,002 37, liste ordonnée des colonnes attendues. Réindexation explicite, colonnes manquantes traitées comme relevés absents.

**Interface.** Trois onglets : notation de flotte, véhicule isolé, consultation du modèle gelé. Sortie utile en atelier : ordre de passage trié par probabilité, pas une étiquette binaire. Seuil réglable par curseur pour rendre l'arbitrage visible ; le seuil figé reste la valeur par défaut.

**Conteneur.** Image multi-étages, compte sans privilège, point de contrôle de santé. TensorFlow absent : le modèle gelé est un ensemble d'arbres.

**Mesures.**

| Configuration | Latence médiane |
|---|---|
| Poste de développement | 50,92 ms |
| Conteneur | 45,98 ms |
| Raspberry Pi 4 | 277,13 ms |

Modèle sérialisé : 1 093 kB. Mémoire résidante : 190 à 192 MB. Empreinte non limitante. Coût presque fixe : 48 ms par véhicule isolé, 0,043 ms sur un lot de 1 000.

**Portage.** Raspberry Pi 4, Debian 13, sans ventilateur. Vingt-et-un vecteurs de référence recalculés sur la carte : prédictions identiques, écart nul sous 10⁻⁹. Débit soutenable : 2 véhicules/s.

**Lecture.** Le conteneur ne coûte rien. La cible matérielle coûte un facteur 5,4, invisible depuis un poste. Le réseau ajoute environ 82 ms et une queue de distribution.

## Difficultés rencontrées

13 difficultés recensées en semaines 1 et 2 : 2 de compréhension, 7 erreurs de méthode, 5 obstacles techniques.

**Erreurs de méthode**, invisibles dans le résultat produit :

- Grille de sélection biaisée : un critère récompensait un jeu de données dégradé.
- Candidat éliminé au mauvais étage (Engine Health).
- Livrable oubliant sa première exigence (sélection des familles de modèles).
- Recommandation contredisant le raisonnement du même document.
- Décision renversée sans être nommée.
- Inversion recopiée d'une source officielle. Règle adoptée : recalculer tout total fourni avec son détail.
- Registre d'écriture inadapté.

**Obstacles techniques**, résolus le jour même sauf un :

- Python 3.14 incompatible avec TensorFlow 3.13. Installation de 3.13 en parallèle.
- Valeurs `na` en texte, colonnes lues en texte, absences comptées à zéro. Vérifier dimensions et types.
- Moyenne d'absences de 8,3 % masquant 8 colonnes au-delà de 65 %. Second indicateur ajouté.
- Jeu diffusé sous un faux nom sur Kaggle (moteur de navire, pas automobile).
- Fins de ligne Windows/Linux. Règle : le dépôt est la seule référence.
- Seuil de décision réglé en échantillon : 82 pannes manquées par pli au lieu de 6. Défaut invisible sans erreur d'exécution.

Détail complet : [docs/method_notes.md](docs/method_notes.md).

## Perspectives

- **Groupes histogramme non traités.** 70 colonnes traitées comme compteurs ordinaires. En dériver des variables de forme : piste la plus directe.
- **Variables d'absence sans gain mesurable.** 6 comparaisons appariées, aucune significative. Effet plus petit que le bruit, ou arbres retrouvant l'information seuls.
- **Signal réduit à un indicateur d'usure.** Importance par permutation : `aa_000` en tête. Le modèle rate préférentiellement les véhicules peu utilisés (compteur médian 199 744 chez les 15 pannes manquées, contre 634 684 chez les détectées).
- **Pas de dimension temporelle.** Une seule campagne de collecte, aucune donnée horodatée, dérive non mesurable.
- **Anonymisation des colonnes.** Analyse structurelle, pas de recommandation physique du type « surveiller tel organe ».
- **Modèle non optimisé pour l'inférence.** 277 ms sur Raspberry Pi 4 contre 50 ms sur poste de développement. Une conversion vers un format d'inférence optimisé allégerait le portage.

## Organisation

```
src/          config, seeding, cost, data, missingness, preprocessing,
              evaluation, models, losses, inference
scripts/      download, check_cost_function, build_dataset, verify,
              paired_comparisons, finalists, calibration, latency
tests/        40 tests, 5 modules
notebooks/    00 sélection, 01 exploration, 02 benchmark, 03 ablation,
              04 pertes sensibles au coût, 05 arbitrage, 06 test final
app/          démonstrateur Streamlit
docs/         protocole, décisions, journal, fiches, bibliographie
reports/      tableaux de résultats, source de vérité
data/, models/  non versionnés, régénérés par script
```

**Règle** : les fichiers de `reports/` font foi. Aucun chiffre saisi à la main.

## Installation

Python 3.13 requis (TensorFlow ne supporte pas 3.14). L'image conteneur n'en a pas besoin.

```bash
python3.13 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./scripts/download_data.sh
./.venv/bin/python scripts/check_cost_function.py
./.venv/bin/python scripts/build_dataset.py
./.venv/bin/python -m pytest
./.venv/bin/python scripts/verify.py
```

Démonstrateur :

```bash
./scripts/fetch_models.sh
docker compose up --build   # http://localhost:8501
```

## Exigences

| ID | Exigence | État |
|---|---|---|
| EF01 | Chargement et analyse exploratoire | fait |
| EF02 | Chaîne de préparation reproductible | fait |
| EF03 | Quatre modèles classiques | fait |
| EF04 | Un réseau de neurones Keras | fait |
| EF05 | Protocole commun et coût Scania | fait |
| EF06 | Banc d'essai comparatif et choix justifié | fait |
| EF07 | Sérialisation du modèle retenu | fait |
| EF08 | Démonstrateur de prédiction | fait |
| EF09 | Simulation de flux temps réel | abandonné |
| ENF01 | Python 3 et venv sous Ubuntu | fait |
| ENF02 | Git, code en anglais, documentation en français | fait |
| ENF03 | Reproductibilité : graines, versions figées | fait |
| ENF04 | Exécutable sans GPU | fait |
| ENF05 | Image Docker du démonstrateur | fait |
| ENF06 | Prédiction unitaire sous 1 s | fait, 50 ms médiane |

## Sources

Jeu de données : APS Failure at Scania Trucks, Scania CV AB, 2016, UCI Machine Learning Repository, GPLv3. Fiche : [docs/dataset_scania.md](docs/dataset_scania.md). Bibliographie : [docs/references.bib](docs/references.bib).


