# Scania APS — Diagnostic de pannes sur poids lourds

[English](README.md) · [Lancer la démonstration](docs/reproduction.md) · [Résultats officiels](reports/test_result.json)

Stage académique de dix semaines à l’ENSA Tanger, sur les données Scania APS publiées par UCI. Le projet aide à prioriser l’inspection du circuit d’air comprimé de véhicules déjà en atelier. Il couvre la comparaison de modèles, le choix d’un seuil selon le coût des erreurs, puis la mise à disposition du modèle dans un tableau de bord et une API.

## Résultats sur le jeu de test officiel

| Indicateur | Résultat |
|---|---:|
| Pannes APS détectées | **360 sur 375 (96 %)** |
| Pannes manquées / fausses alertes | 15 / 387 |
| Coût du modèle / coût de la règle « tout signaler » | **11 370 / 156 250 unités** |
| Réduction du coût face à cette référence | **92,72 %** |
| Latence médiane d’une inférence locale sur Raspberry Pi 4 | **277,13 ms** sur 200 appels |

Une panne manquée vaut 500 unités et une fausse alerte en vaut 10 selon le barème du défi. Les économies sont exprimées dans ce barème. La latence correspond à l’inférence locale, hors aller-retour réseau. [Résultat officiel](reports/test_result.json) · [Mesures sur Raspberry Pi](reports/deployment_raspberry-pi-4.json)

## Démarche

1. **Comparer cinq familles de modèles.** Le benchmark utilise 48 000 véhicules. Un lot distinct de 12 000 véhicules sert à l’arbitrage et le jeu officiel de 16 000 véhicules sert à l’évaluation finale.
2. **Choisir un point de fonctionnement.** Le seuil du gradient boosting est ajusté sur des prédictions hors pli, puis figé avant l’évaluation officielle. L’écart entre les finalistes sur le lot d’arbitrage était inférieur à la marge prévue. La dispersion des résultats répétés a servi de critère de départage complémentaire.
3. **Rendre le modèle exploitable.** Le tableau de bord Streamlit permet d’examiner un véhicule ou un fichier et de visualiser le compromis entre fausses alertes et pannes manquées. L’API FastAPI utilise la même chaîne de préparation et de prédiction. Le portage sur Raspberry Pi 4 est accompagné de mesures et de 21 entrées de référence.

## Limites de validation

Les données sont anonymisées et ne contiennent pas de suivi temporel. L’évaluation porte donc sur le triage en atelier. Le délai d’anticipation des pannes et la tenue du modèle face à la dérive restent à mesurer. L’ajout d’indicateurs de valeurs manquantes n’a pas montré de gain mesurable dans les comparaisons publiées. Dans le benchmark historique, le prétraitement a été ajusté sur l’ensemble des 48 000 lignes avant la validation croisée. Une estimation strictement hors pli demanderait de réajuster ce prétraitement dans chaque pli. Le lot d’arbitrage et le jeu officiel étaient distincts de ces 48 000 lignes.

## Aller plus loin

| Vous cherchez | Point d’entrée |
|---|---|
| Essayer la démonstration ou relancer les contrôles | [Guide de reproduction](docs/reproduction.md) |
| Comprendre le protocole et le choix du modèle | [Protocole](docs/evaluation_protocol.md) · [Arbitrage](reports/arbitration.csv) |
| Examiner le code et les tests | [Prédicteur](src/inference.py) · [API](src/api.py) · [Tests](tests/) |
| Vérifier les chiffres de déploiement | [Comparatif des configurations](reports/deployment_summary.csv) · [Contrôle de portage](scripts/check_port.py) |
