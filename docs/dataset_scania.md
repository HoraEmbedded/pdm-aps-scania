# Fiche jeu de données : APS Failure at Scania Trucks

Candidat retenu. Mesures effectuées directement sur les fichiers, pas reprises de la
documentation du producteur.

## 1. Origine

- Organisme producteur : Scania CV AB, Suède
- Donateurs : Tony Lindgren et Jonas Biteus
- Année : septembre 2016
- Source : UCI Machine Learning Repository, page "APS Failure at Scania Trucks"
- Contexte de publication : challenge industriel IDA 2016, 15th International Symposium
  on Intelligent Data Analysis

## 2. Licence

GNU General Public License version 3 ou ultérieure, copyright Scania CV AB 2016. Texte
de la licence : https://www.gnu.org/licenses/. Usage académique autorisé.

## 3. Volume

| Fichier | Lignes | Colonnes | Classe positive |
|---|---|---|---|
| Entraînement | 60 000 | 171 | 1 000, soit 1,67 % |
| Test | 16 000 | 171 | 375, soit 2,34 % |

Le découpage entraînement / test est fourni par le producteur. Les deux taux de positifs
ont été vérifiés sur les fichiers, et l'écart entre eux est réel : les scores obtenus en
validation interne ne sont donc pas directement comparables aux scores de test.

## 4. Variables

171 attributs, dont la colonne `class`, soit 170 variables prédictives. Toutes numériques
et anonymisées : les noms de colonnes (`aa_000`, `ab_000` et suivants) ne renvoient à
aucune grandeur physique nommée, pour raisons de confidentialité industrielle.

Sept groupes de colonnes sont des variables histogramme, c'est-à-dire des comptages
répartis en classes de valeurs. Ils totalisent 70 colonnes, de préfixes `ag`, `ay`, `az`,
`ba`, `cn`, `cs` et `ee`. Les 100 autres colonnes sont des compteurs isolés.

Conséquence pour l'interprétation : aucune variable ne peut être reliée à un organe
physique nommé. L'analyse des variables influentes restera donc structurelle et non
physique.

## 5. Variable cible

Colonne `class`. Le sens des deux classes n'est pas « sain contre défaillant ». Les deux
classes concernent des camions déjà en panne et déjà arrivés à l'atelier :

- classe positive : panne d'un composant du système d'air comprimé (APS) ;
- classe négative : panne d'un autre système, sans lien avec l'APS.

Le jeu de données ne contient aucun camion en état de marche normal. Une fausse alerte
signifie donc qu'un mécanicien inspecte un circuit d'air sain sur un véhicule déjà à
l'atelier, et non qu'un camion en service est immobilisé à tort.

## 6. Valeurs manquantes

Encodées `na` en texte dans le fichier, ce qui impose `na_values=["na"]` à la lecture.
Sans ce paramètre, la lecture réussit sans message d'erreur, toutes les colonnes sont
traitées comme du texte et le comptage des absences renvoie zéro partout.

Taux global : 8,33 % des cellules en entraînement, 8,41 % en test. La moyenne est
trompeuse. Lecture par colonne, sur l'entraînement :

| Colonne | Taux d'absence |
|---|---|
| `br_000` | 82,1 % |
| `bq_000` | 81,2 % |
| `bp_000` | 79,6 % |
| `bo_000` | 77,2 % |
| `cr_000` | 77,2 % |

Huit colonnes dépassent 50 % d'absences, 24 dépassent 20 %, et une seule colonne est
complète. Le profil est presque identique entre entraînement et test, ce qui indique une
collecte homogène.

## 7. Métrique de coût

Fournie par le producteur, sous forme de matrice explicite.

| Erreur | Coût unitaire |
|---|---|
| Fausse alerte : prédit positif, vrai négatif | 10 |
| Panne manquée : prédit négatif, vrai positif | 500 |

Coût total = 10 x (fausses alertes) + 500 x (pannes manquées). Rapport de 50 contre 1 en
défaveur de la panne manquée.

## 8. Publications de référence

Les trois meilleurs résultats du challenge IDA 2016, annoncés par le producteur avec le
détail de leurs erreurs. Les trois totaux ont été reconstitués par le calcul depuis ce
détail et tombent juste au chiffre près, ce qui établit que la règle de coût employée
dans ce projet est celle du challenge, sur le même jeu de test.

| Auteurs | Coût | Fausses alertes | Pannes manquées |
|---|---|---|---|
| Costa, Nascimento | 9 920 | 542 | 9 |
| Gondek, Hafner, Sampson | 10 900 | 490 | 12 |
| Garnaik, Das, Sreepada, Patra | 11 480 | 398 | 15 |

Attention à la terminologie de la source, qui désigne ces erreurs par « type 1 » et
« type 2 ». L'ambiguïté a d'abord conduit à les inverser ; le recalcul a révélé l'erreur,
la version inversée donnant 199 150 au lieu de 11 480.

Références complètes dans `references.bib`.

## 9. Taille sur disque

43 Mo pour le fichier d'entraînement, 12 Mo pour le fichier de test.
