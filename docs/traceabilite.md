# Tracabilite exigences -> artefacts

Statuts : [ ] a faire, [~] en cours, [x] satisfait.

## Exigences fonctionnelles

| ID | Exigence | Priorite | Statut | Artefact |
|----|----------|----------|--------|----------|
| EF01 | Chargement + analyse exploratoire | Essentielle | [~] | `src/data/load_aps.py`, `scripts/sanity_check.py` |
| EF02 | Pipeline de preparation reproductible | Essentielle | [ ] | S3 |
| EF03 | 4 modeles ML classiques | Essentielle | [ ] | S4-S5 |
| EF04 | 1 modele DL Keras | Essentielle | [ ] | S6-S7 |
| EF05 | Protocole d'evaluation commun + cout Scania | Essentielle | [~] | `src/evaluation/cost.py` |
| EF06 | Benchmark comparatif et choix justifie | Essentielle | [ ] | S8 |
| EF07 | Serialisation du modele retenu | Importante | [ ] | S7 |
| EF08 | Demonstrateur de prediction | Importante | [ ] | S8 |
| EF09 | Simulation de flux temps reel | Optionnelle | [ ] | S9 |

## Exigences non fonctionnelles

| ID | Exigence | Priorite | Statut | Artefact |
|----|----------|----------|--------|----------|
| ENF01 | Python 3 + venv sous Ubuntu | Essentielle | [x] | `.venv/`, `requirements.txt` |
| ENF02 | Git, code en anglais, doc en francais | Essentielle | [x] | depot Git, `README.md` |
| ENF03 | Reproductibilite (graines, requirements, notebooks) | Essentielle | [x] | `src/utils/seeds.py`, `requirements-lock.txt` |
| ENF04 | Executable sans GPU | Importante | [x] | `tensorflow-cpu` |
| ENF05 | Image Docker du demonstrateur | Importante | [ ] | S9 |
| ENF06 | Prediction unitaire < 1 s | Importante | [ ] | S8 |

## Livrables

| ID | Livrable | Echeance | Statut |
|----|----------|----------|--------|
| D1 | Cahier des charges valide | S1 | [x] |
| D2 | Etat de l'art + choix du dataset | S2 | [ ] |
| D3 | Notebooks EDA + pipeline | S3 | [ ] |
| D4 | Code source versionne | S9 | [~] |
| D5 | Modeles entraines | S7 | [ ] |
| D6 | Rapport de benchmark | S8 | [ ] |
| D7 | Demonstrateur | S8 | [ ] |
| D8 | Image Docker + README | S9 | [ ] |
| D9 | Rapport final | S10 | [ ] |
| D10 | Support de soutenance | S10 | [ ] |
