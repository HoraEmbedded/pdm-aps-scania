# Carte du dépôt

Ce document associe chaque fichier du dépôt à sa raison d'être, à l'étape qui
l'a produit et à l'exigence du cahier des charges qu'il couvre. Il est mis à
jour à chaque fin de séance. L'inventaire automatique correspondant est produit
par `scripts/inventaire.py`.

## Principe d'organisation

Le dossier `src` contient le code réutilisable, importé par les carnets et par
les scripts, jamais dupliqué. Le dossier `scripts` contient les points d'entrée
en ligne de commande. Le dossier `notebooks` contient l'exploration et les
résultats, avec leurs commentaires. Le dossier `docs` contient les livrables
rédigés. Les données et les modèles ne sont pas versionnés : ils sont
régénérables par script, et c'est le script qui est versionné.

## Le code source

| Fichier | Rôle | Étape | Exigence |
|---|---|---|---|
| `src/config.py` | Point unique de vérité : chemins, graine, matrice de coût, constantes du protocole | Migration | ENF03 |
| `src/graines.py` | Initialise les générateurs aléatoires de Python, NumPy et TensorFlow | S1 | ENF03 |
| `src/cout.py` | Fonction de coût de Scania, recherche du seuil optimal, dépondération | 4.1 | EF05 |
| `src/donnees.py` | Chargement du fichier brut, découpage stratifié, accès au jeu de test scellé | 3.2 | EF01 |
| `src/absences.py` | Détection des colonnes informatives, variable de profondeur, indicatrices | 3.1 à 3.3 | EF01, EF02 |
| `src/preparation.py` | Imputation différenciée puis normalisation, apprises sur l'apprentissage seul | 3.5 et 3.6 | EF02 |
| `src/evaluation.py` | Validation croisée sous protocole figé, avec réglage du seuil dans chaque pli | 4.2 | EF05 |
| `src/modeles.py` | Les cinq modèles du banc d'essai, avec la pondération issue de la matrice de coût | 4.3 | EF03, EF04 |

## Les scripts

| Fichier | Rôle | Étape |
|---|---|---|
| `scripts/download_data.sh` | Télécharge le jeu de données depuis sa source primaire | S1 |
| `scripts/verifier_cout.py` | Six tests de la fonction de coût, dont la reconstitution d'un résultat publié | 4.1 |
| `scripts/preparer.py` | Rejoue toute la chaîne de préparation et vérifie les chiffres connus | 3.6 |
| `scripts/inventaire.py` | État des lieux du dépôt, relançable à tout moment | Reprise |

## Les carnets

| Fichier | Contenu |
|---|---|
| `notebooks/01_exploration.ipynb` | Analyse des valeurs absentes, figures, décisions D-09 et D-10 |
| `notebooks/02_benchmark.ipynb` | Comparaison des cinq modèles sous protocole identique |
| `notebooks/03_experiences.ipynb` | Ablation V0, V1, V2 et plan factoriel sur la variable d'usage |
| `notebooks/04_final.ipynb` | Ouverture unique du jeu de test et analyse des erreurs |

## Les documents

| Fichier | Rôle | Livrable |
|---|---|---|
| `docs/D2_note_etat_de_lart.md` | État de l'art et choix justifié du jeu de données | D2 |
| `docs/grille_selection_dataset.md` | Grille multicritère ayant conduit au choix | D2 |
| `docs/fiche_dataset_*.md` | Fiches des trois candidats instruits | D2 |
| `docs/bibliographie.md` | Références vérifiées à la source | D2, D9 |
| `docs/protocole_evaluation.md` | Protocole d'évaluation figé avant tout entraînement | EF05, EF06 |
| `docs/JOURNAL.md` | Journal chronologique des séances | D9 |
| `docs/CARTE.md` | Le présent document | ENF02 |

## Les décisions, et où elles vivent désormais

Les décisions numérotées D-01 à D-11 ne font plus l'objet de fichiers séparés.
Leur contenu est intégré aux documents qui les appliquent : les décisions D-09 et
D-10 dans le protocole de préparation et dans `src/absences.py` et
`src/preparation.py`, la décision D-11 dans la section 4 du protocole
d'évaluation. Le journal conserve la trace de leur date d'adoption.

Motif de ce changement : la coexistence de fichiers de décision qui se
corrigeaient les uns les autres rendait l'état courant du projet illisible.
