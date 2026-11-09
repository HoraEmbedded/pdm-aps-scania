# Reproduire le démonstrateur / Reproduce the demo

## Démarrage / Quick start

Prérequis sur Linux ou WSL / Prerequisites on Linux or WSL: Python 3.12, wget, unzip and Docker Compose.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-serve.txt
bash scripts/download_data.sh
.venv/bin/python scripts/prepare_demo.py
docker compose up --build
```

- Tableau de bord / Dashboard: http://localhost:8501
- Documentation API / API documentation: http://localhost:8000/docs
- État de l’API / API health: http://localhost:8000/health

La préparation régénère les deux objets de prétraitement depuis les données UCI. Si un manifeste est déjà présent, elle conserve le modèle correspondant et vérifie que le prédicteur le charge. Sinon, elle reconstruit le gradient boosting et reprend le seuil historique du rapport officiel. Cette procédure ne dépend pas d’une release de poids.

Preparation rebuilds the two preprocessing objects from UCI data. If a manifest exists, it preserves the associated model and checks that the predictor can load it. Otherwise it rebuilds gradient boosting and uses the historical threshold recorded in the official report. This path does not require a weights release.

## Contrôles / Checks

```bash
.venv/bin/python -m pip install "pytest>=8,<9"
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_documents.py
.venv/bin/python scripts/check_port.py
```

La suite locale utilise les données et les artefacts lorsqu’ils sont présents. Le contrôle de portage compare les prédictions obtenues aux 21 entrées enregistrées. Une reconstruction qui s’en écarte doit être présentée comme une nouvelle construction. Les chiffres historiques restent ceux de [test_result.json](../reports/test_result.json) et des [mesures de déploiement](../reports/deployment_summary.csv).

The local suite uses data and artifacts when available. The port check compares predictions with the 21 recorded inputs. A rebuild that differs should be identified as a separate build. The historical results remain in [test_result.json](../reports/test_result.json) and the [deployment measurements](../reports/deployment_summary.csv).

## Campagne expérimentale / Experimental campaign

Pour les notebooks, installer `requirements.txt` dans un environnement Python 3.12 dédié. Les carnets 00 à 06 couvrent la sélection des données, l’exploration, le benchmark, l’ablation, les variantes de perte, l’arbitrage et l’évaluation officielle. Exécuter le carnet final peut réécrire des fichiers de résultats. Utiliser une copie de travail pour comparer une nouvelle campagne aux résultats publiés.

For notebooks, install `requirements.txt` in a dedicated Python 3.12 environment. Notebooks 00–06 cover dataset selection, exploration, benchmarking, ablation, loss variants, arbitration and official evaluation. Running the final notebook can overwrite result files. Use a working copy to compare a new run with the published results.

## Raspberry Pi 4

Sur un système ARM 64 bits, disposer de Python 3.12, venv, wget, unzip et du
runtime OpenMP (`libgomp1` sous Debian). Depuis le dépôt, lancer
`bash scripts/setup_pi.sh`. Le contrôle des prédictions s’exécute avant toute
nouvelle mesure. Pour servir ensuite l’API sur la carte, exécuter
`.venv/bin/python -m uvicorn src.api:app --host 127.0.0.1 --port 8000`.

On 64-bit ARM, install Python 3.12, venv, wget, unzip and the OpenMP runtime
(`libgomp1` on Debian). Run `bash scripts/setup_pi.sh` from the checkout.
It verifies predictions before any new timing run. The command above starts
the API on the board's loopback interface.
