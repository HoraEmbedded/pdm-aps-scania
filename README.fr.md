# Maintenance prédictive - APS Scania

Classification de pannes sensible au coût sur le système d'air comprimé de camions Scania.
Cinq familles de modèles comparées sous protocole figé avant tout entraînement. Ouverture unique du test officiel.

Projet de 4e année du cycle ingénieur, 10 semaines, encadré. English: [README.md](README.md).

## Résultat

| | |
|---|---|
| Coût (test officiel) | **11 370** |
| Référence constante | 156 250 |
| Économie | **92,7 %** |
| Détection | 96,0 % (360/375) |
| Pannes manquées | 15 |
| Fausses alertes | 387 |

Podium IDA 2016, même test, même métrique : 9 920, 10 900, **11 370**, 11 480 → 3e sur 4.
Écart avec la 4e place : 110 unités, toutes en fausses alertes (387 contre 398).

Chiffres : [reports/test_result.json](reports/test_result.json).

## Problème

Camions déjà en atelier. Question : panne APS ou autre organe ?
Une panne APS manquée laisse la vraie cause en place.

170 capteurs anonymisés par camion. Scania 2016, challenge IDA.

| Propriété | Valeur |
|---|---|
| Déséquilibre | 1,67 % train / 2,34 % test |
| Absences | 8,33 % des cellules, 8 colonnes > 65 % |
| Coût | fausse alerte 10, panne manquée 500 (50:1) |

Métrique = coût total Scania. Référence = moins chère des deux règles constantes.
Elle change de camp selon le fichier (égalité à 1,96 % de positifs) :

| Fichier | Ne rien signaler | Tout signaler | Référence |
|---|---|---|---|
| Test (16 000) | 187 500 | 156 250 | tout signaler |
| Réservé (12 000) | 100 000 | 118 000 | ne rien signaler |

## Solution

Protocole figé avant le premier entraînement. Trois mesures, dans l'ordre, sans rétroaction.

**1. Banc d'essai — 5 plis sur 48 000 lignes.**

| Modèle | Coût | σ | Détection |
|---|---|---|---|
| Gradient boosting | 6 554 | 827 | 0,954 |
| Forêt aléatoire | 6 926 | 804 | 0,963 |
| Perceptron Keras | 8 494 | 1 780 | 0,940 |
| SVM linéaire | 9 334 | 1 465 | 0,920 |
| Régression logistique | 9 596 | 1 222 | 0,928 |

Arbres −2 725 vs linéaires (marge protocole : 2 000). Deux premiers à 372 : non départagés par 5 plis.

**2. Validation croisée répétée — 6 partitions, 30 mesures.**
Écart apparié 396 (plancher 354). Désigne les finalistes.

**3. Arbitrage — 12 000 lignes réservées, ouvertes une fois.**
GB 6 410, forêt 7 310. Écart 900 < marge 2 000.
Retenu : **gradient boosting** (mesures répétées + dispersion plus faible).

**Trois points d'ingénierie :**

- **Absence = signal.** 8 colonnes emboîtées → variable de profondeur, imputées à zéro. 56 non emboîtées → 9 indicatrices. Construites avant imputation.
- **Coût entré une seule fois.** Pondération 50:1 porte le coût, seuil mesuré par balayage. Sinon rapport effectif 2 501:1.
- **Seuil hors échantillon.** Validation croisée interne. Forêt : 41 050 → 6 926 (×5,9).

## Difficultés

13 en semaines 1–2 : 2 de compréhension, 7 erreurs de méthode, 5 obstacles techniques.

**Erreurs de méthode** — invisibles dans le résultat produit :
- Grille biaisée : un critère récompensait un jeu dégradé.
- Candidat éliminé au mauvais étage (Engine Health).
- Livrable sans sa première exigence (sélection des familles).
- Recommandation contredisant son propre raisonnement (→ D-11).
- Décision renversée sans être nommée.
- Inversion recopiée d'une source officielle → règle : recalculer tout total fourni avec son détail.
- Registre inadapté (fiches adressées à leur auteur).

**Obstacles techniques** — résolus le jour même, sauf un :
- Python 3.14 vs TensorFlow 3.13 → 3.13 installé en parallèle.
- `na` en texte → colonnes traitées en texte, absences comptées à 0. Vérifier dimensions et types.
- Moyenne 8,3 % masquant 8 colonnes > 65 % → second indicateur ajouté.
- Faux nom : « Automotive Engine Health » = moteur de navire (IEEE DataPort 2022).
- Fins de ligne Windows/Linux → dépôt = seule référence.

Détail complet : [docs/method_notes.md](docs/method_notes.md).

## Perspectives

- **Groupes histogramme non traités** (70 colonnes, traitées comme compteurs). En dériver des variables de forme : première piste.
- **Variables d'absence sans gain mesurable** (6 comparaisons appariées non significatives). Effet < bruit, ou arbres retrouvent l'information seuls.
- **Une seule grille d'hyperparamètres enregistrée** (régression logistique), non rejouable.
- **Seuil figé non optimal** : 11 370 vs 10 060 au seuil préféré a posteriori.
- **Résultats publiés non indépendants** : test public depuis 2016, scores améliorés sur le même jeu fixe.

## Organisation

```
src/          config, seeding, cost, data, missingness, preprocessing,
              evaluation, models, losses, inference
scripts/      download, check_cost_function, build_dataset, verify,
              paired_comparisons, finalists, calibration, latency, ...
tests/        40 tests, 5 modules
notebooks/    00 sélection → 06 test final
app/          démonstrateur Streamlit
docs/         protocole, décisions, journal, fiches, bibliographie
reports/      tableaux de résultats — source de vérité
data/, models/ non versionnés, régénérés par script
```

**Règle** : `reports/` fait foi. Aucun chiffre saisi à la main.

## Démarrage

Python 3.13 requis (TF ne supporte pas 3.14). L'image conteneur n'en a pas besoin.

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
| EF01–EF08 | Chargement, chaîne, 4 modèles, Keras, protocole, choix, sérialisation, démonstrateur | fait |
| EF09 | Flux temps réel | abandonné (optionnel) |
| ENF01–ENF06 | Python/venv, Git, reproductibilité, sans GPU, Docker, latence < 1 s | fait |

## Sources

APS Failure at Scania Trucks, Scania CV AB, 2016, UCI, GPLv3.
[docs/dataset_scania.md](docs/dataset_scania.md) · [docs/references.bib](docs/references.bib)

