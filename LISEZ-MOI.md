# Mise en cohérence complète du dépôt

Version 2. La version 1 contenait une erreur de fond que la procédure de mise
en cohérence a relevée : voir la section « Ce que j'avais faux » en fin de
document. Si vous avez déjà appliqué la version 1, la présente version corrige
les fichiers concernés.

Trois choses : le nettoyage des fichiers de l'ancienne architecture, une suite
de tests, et l'alignement de tous les documents sur `reports/`.

## Ce que contient ce dossier

```
cleanup.sh                       supprime l'ancienne architecture
pytest.ini                       configuration de la suite
tests/                           6 modules, dont test_behaviour.py sans données
.github/workflows/tests.yml      intégration continue
README.md  README.fr.md          réécrits, avec le résultat en tête
docs/journal.md                  réécrit, entrées manquantes ajoutées
docs/hyperparameter_grids.md     réécrit, chiffres corrigés
scripts/apply_doc_patches.py     corrige les trois documents longs en place
scripts/check_documents.py       échoue si un chiffre périmé subsiste
scripts/export_report_figures.py sort en fichiers les chiffres du rapport
scripts/rebuild.py               corrige le mélange des sources
requirements-serve.txt           versions de sérialisation épinglées
```

## Ordre d'application

```bash
cd ~/pdm-aps-scania
git status                       # rien en attente
git checkout -b mise-en-coherence

# 1. copier
cp -r ~/Téléchargements/patch-v2/tests .
cp ~/Téléchargements/patch-v2/pytest.ini .
cp ~/Téléchargements/patch-v2/README.md ~/Téléchargements/patch-v2/README.fr.md .
cp ~/Téléchargements/patch-v2/requirements-serve.txt .
cp ~/Téléchargements/patch-v2/docs/*.md docs/
cp ~/Téléchargements/patch-v2/scripts/*.py scripts/
cp ~/Téléchargements/patch-v2/cleanup.sh .

# 2. corriger les trois documents longs, à blanc d'abord
python scripts/apply_doc_patches.py --check
python scripts/apply_doc_patches.py

# 3. nettoyer
bash cleanup.sh
git status                       # relire les suppressions

# 4. régénérer et vérifier
python scripts/build_dataset.py
python scripts/rebuild.py
python scripts/export_report_figures.py
python -m pytest
python scripts/verify.py
python scripts/check_documents.py     # doit ne rien renvoyer
```

`check_documents.py` est le contrôle qui compte. Tant qu'il échoue, l'étape 2
n'est pas terminée : il nomme le fichier, la ligne, et la valeur attendue. Il
cherche deux choses, les chiffres périmés et les affirmations que les mesures
contredisent. La seconde catégorie est la plus grave : un chiffre faux est une
coquille, une affirmation fausse est une thèse.

`export_report_figures.py` écrit sous `reports/report_figures/` les sept
grandeurs que la rédaction réclame et qui n'existaient nulle part sous forme de
fichier : la rupture des deux groupes, les neuf sous-blocs et leur accord, les
deux tests d'emboîtement, la table profondeur contre médiane d'usage d'où sort
le facteur 329, la répartition de la manquance entre histogrammes et compteurs,
les paires d'absence dupliquées, et un `summary.json`. Il s'arrête en code 1 si
la somme de contrôle n'est plus 313 696.

`apply_doc_patches.py` fait des remplacements de chaînes exactes et sort en
code 1 si l'une n'est pas trouvée. Lancez-le d'abord avec `--check` : s'il
signale un `[NOT FOUND]`, c'est que le passage a été édité depuis, et il faut
le corriger à la main plutôt que de forcer.

## 1. Le nettoyage

`cleanup.sh` supprime 48 fichiers et 6 dossiers. Le dépôt contient
actuellement les deux architectures côte à côte : c'est l'étape qui n'avait pas
été passée lors de la première restructuration.

| Catégorie | Ce qui part |
|---|---|
| Modules source | `absences`, `cout`, `donnees`, `graines`, `modeles`, `pertes`, `preparation` |
| Dossiers fantômes | `src/{data,features,models,evaluation}`, réduits à des caches périmés |
| Scripts | `baseline_check`, `inventaire`, `preparer`, `verifier_cout` |
| Carnets | `02_benchmark_ancien`, `03_experiences`, `05_perte_cout` |
| Documents | `CARTE`, `JOURNAL`, `JOURNAL_projet_2026-08-09`, `traceabilite`, `protocole_*`, les trois `fiche_*` |
| Résultats | `benchmark_log`, `comparaisons_appariees`, `experiences`, `fonctions_perte`, `variante_perceptron_retenue`, `s1_*`, `s2_*`, `reports/metrics` |
| Figures | les onze `f*.png` et les dix doublons `0x_` de l'ancienne numérotation |
| Données préparées | `X_app_final`, `X_val_final`, `y_app`, `extracteur_absences.joblib`, `preparateur.joblib`, `aps_scania.zip` |

Les deux `.joblib` de l'ancienne chaîne sont les plus dangereux à laisser :
`extracteur_absences.joblib` et `preparateur.joblib` ne se chargent plus, les
classes ayant changé de nom, mais rien n'indique lequel des deux jeux d'objets
est le bon quand on lit le dossier.

Un point sur `src/{data,features,models,evaluation}/`. Ces dossiers ne
contiennent plus que des `__pycache__`, sans aucun fichier source, donc
`src/data.py` l'emporte à l'import et il n'y a pas de bug actuel. Ils partent
pour deux raisons : les `.pyc` orphelins portent les noms de modules d'une
architecture disparue, et poser un `__init__.py` dans `src/data/` suffirait à
faire disparaître `src/data.py` de l'import sans aucun message.

## 2. La suite de tests

40 tests, cinq modules, construits à partir des vérifications qui existaient
déjà. Rien n'est inventé, aucune valeur n'est choisie pour faire passer un test.

| Module | Contenu | Données requises |
|---|---|---|
| `test_cost.py` | Les sept contrôles de `check_cost_function.py`, un par test, plus l'inversion des règles constantes, les ex aequo, le cas dégénéré et vingt tirages contre la boucle naïve | aucune |
| `test_data.py` | Dimensions, effectifs, découpage, stratification exacte, déterminisme, et la simulation qui montre pourquoi la stratification n'est pas cosmétique | `data/raw` |
| `test_missingness.py` | Partition des groupes, la falaise du seuil, emboîtement du groupe 1 à zéro exception, échec du groupe 2, les neuf sous-blocs et leur accord, la profondeur comme niveau d'usage | `data/raw` |
| `test_pipeline.py` | Somme de contrôle, absence de fuite dans les deux sens, imputation à zéro du groupe 1, préservation de l'ordre des colonnes | `data/processed` |
| `test_inference.py` | Le manifeste contre `arbitration.csv`, et surtout l'alignement : colonnes inversées, colonne manquante, colonne en trop | `models/` |
| `test_reports.py` | Cohérence mutuelle des fichiers de résultats | aucune |

Les modules marqués skippent proprement quand les données ne sont pas là, au
lieu d'échouer : `pytest` sur un clone neuf passe sans rien télécharger.

**`test_reports.py` est le module qui compte.** C'est lui qui rend impossible
la dérive qui a motivé cette séance. Il recalcule chaque coût de
`benchmark.csv` et d'`arbitration.csv` depuis ses décomptes d'erreurs, vérifie
que les matrices de confusion somment à 12 000 et à 16 000, que
`test_result.json` porte bien l'économie qu'il annonce, que le verdict de
`finalists.csv` découle de ses propres nombres, qu'aucune des six comparaisons
appariées ne franchit son plancher, et que l'écart de `overfitting.csv` est bien
le rapport 1,25 des tailles. Deux fichiers ne peuvent plus se contredire en
silence.

Il contient aussi le test qui vous sera le plus utile en soutenance : les dix
variables d'absence portent une importance par permutation inférieure à 0,001,
alors que `aa_000` seule en porte 0,057. Deux méthodes indépendantes, l'ablation
appariée et l'importance par permutation, ne détectent rien. C'est un argument
plus solide qu'une seule.

## 3. Les documents

**Réécrits en entier**, les changements étant trop nombreux pour des
remplacements : les deux README, `docs/journal.md`,
`docs/hyperparameter_grids.md`.

**Corrigés en place** par `apply_doc_patches.py` : `evaluation_protocol.md`,
`technical_decisions.md`, `dataset_scania.md`.

Les corrections de fond, au-delà des chiffres :

**La marge de 2 000 unités est requalifiée.** Le protocole la présentait comme
un seuil absolu. Elle porte en réalité sur la comparaison à cinq plis, et la
validation croisée répétée a un plancher mesuré, non fixé. Sans cette
distinction, `finalists.csv` contredit le protocole : 396 unités déclarées
significatives alors que la marge annoncée est de 2 000. C'est une correction
nécessaire, pas cosmétique.

**Le protocole gagne une section 10** consignant les deux ouvertures, celle des
lignes réservées et celle du jeu de test, dans l'ordre et chacune une fois.
C'était l'engagement le plus fort du document et rien n'attestait qu'il avait
été tenu.

**Les doublons d'absence passent de deux colonnes à plus de cinquante paires.**
Ma formulation précédente était fausse. La conséquence est plus intéressante que
la correction : elle donne une raison technique de ne pas surinterpréter le
classement de `variable_importance.csv`, l'importance se répartissant
arbitrairement à l'intérieur de chaque paire.

**Le journal reçoit les cinq séances qui manquaient** : arbitrage, calibration,
ouverture du test, sérialisation et conteneur, mise en cohérence. Avec les deux
incidents à consigner, l'inversion de conclusion sur les finalistes et la
corruption du fichier de verrouillage.

## Ce qui reste à faire de votre côté

**Régénérer `requirements-lock.txt`.** Il est actuellement inutilisable : le
`pip freeze` a été exécuté pendant que NumPy 2.5.2 était installé, si bien que
le fichier épingle `numpy==2.5.2` et `tensorflow-cpu==2.17.1`, qui sont
incompatibles, plus trois paquets ONNX dont l'un exige `ml_dtypes>=0.5.4` que
vous avez rétrogradé. C'est le fichier dont toute la fonction est la
reproductibilité.

```bash
pip uninstall -y onnx onnxruntime skl2onnx     # si vous n'en avez pas besoin
pip install -r requirements.txt
python scripts/verify.py                        # confirmer que ça tourne
pip freeze > requirements-lock.txt              # figer seulement après
```

Ne figez jamais un environnement avant d'avoir vérifié qu'il s'exécute. C'est
l'enseignement de l'incident, et il est consigné dans le journal.

**Trancher le port du conteneur.** `docker-compose.yml` publie sur 8502, et les
README que je livre le disent maintenant explicitement plutôt que de prétendre
8501. Si vous préférez 8501 partout, changez le compose et la ligne
correspondante des deux README.

**Compléter `scripts/fetch_models.sh`.** Il contient encore
`REPO="${MODEL_REPO:-<your-account>/pdm-aps-scania}"`. Votre dépôt est
`HoraEmbedded/pdm-aps-scania`, et une notice qui ne s'exécute pas telle quelle
est exactement ce que le critère de reproductibilité par un tiers vient
sanctionner.

**Vérifier le compte de tests.** J'annonce 40 tests dans les README sans avoir
pu exécuter pytest. Si le compte diffère, corrigez le chiffre aux deux endroits,
ou dites-le-moi.

## Ce que je n'ai pas pu vérifier

Je n'exécute pas Python. La suite de tests est écrite contre les signatures
réelles de vos modules et contre les valeurs de `reports/` et de la sortie de
`build_dataset.py`, mais elle n'a jamais été lancée. Attendez-vous à une ou deux
corrections d'import ou de nom de colonne au premier passage, et envoyez-moi la
trace si quelque chose casse.

Deux tests sont les plus susceptibles de demander un ajustement :
`test_pipeline.py::test_the_fitted_medians_are_not_the_pooled_medians`, qui
appelle `Preprocessor._impute`, une méthode privée, et
`test_inference.py::test_probabilities_are_in_range`, qui reconstruit une trame
brute par un chemin un peu détourné.


## Ce que j'avais faux

Trois erreurs dans la version 1, dont une de fond. Elles sont corrigées dans les
fichiers ci-dessus.

### 1. Le critère de décision du modèle final

J'avais conseillé de remplacer `deciding_criterion: "stability across
partitions"` par la différence appariée de 396 unités. **C'était une erreur, et
elle aurait introduit un défaut là où il n'y en avait pas.**

Les 396 unités sont mesurées sur les 48 000 lignes d'apprentissage
(`reports/finalists.csv`). Elles servent à désigner les deux modèles qui
entrent en arbitrage. L'arbitrage, lui, se joue sur les 12 000 lignes réservées
(`reports/arbitration.csv`), où l'écart vaut 900 unités, sous la marge de 2 000
du protocole, et où le nombre de pannes manquées est à égalité. Deux décisions,
deux jeux de données, deux étalons, et les deux produisent un chiffre du même
ordre : c'est précisément pourquoi la confusion est facile.

Le libellé d'origine était donc juste, seulement ambigu. Les deux README portent
maintenant une table qui sépare les deux décisions, et le manifeste doit préciser
de quelle dispersion il parle plutôt que changer de critère :

```json
"deciding_criterion": "dispersion across the 6 repeated partitions, 1203 against 1307; cost on the reserved rows did not separate, 900 units under a 2000 margin, and missed failures were tied"
```

**Un point que vous devez trancher, et que je ne peux pas trancher pour vous.**
La section 5 du protocole désigne le coût comme critère d'arbitrage « et le
seul ». Elle ne prévoit aucun critère subsidiaire. Retenir le gradient boosting
sur la dispersion est défendable, mais ce n'est pas l'application d'une règle
écrite à l'avance, et le présenter comme telle serait un départage rétrospectif
déguisé en protocole, exactement ce que le projet s'est interdit partout
ailleurs. Deux formulations honnêtes : citer l'article du cahier des charges qui
prévoit une cascade de critères, s'il existe, ou écrire que le protocole ne
départageait pas ce cas et que le choix a été fait hors protocole, sur les
mesures répétées. Le protocole corrigé consigne la seconde, à vous de la changer
si le cahier des charges dit autre chose.

### 2. Le facteur 457 et la dépondération

Je citais dans les README le seuil du gradient boosting à 457 fois le repère
analytique, comme diagnostic de calibration. C'est un artefact. La dépondération
suppose que la pondération a multiplié les cotes par cinquante, ce qui ne vaut
que pour deux modèles sur cinq, et l'appliquer aux trois autres fabrique le
chiffre. Le gradient boosting est le mieux calibré des cinq au score de Brier :
un diagnostic qui le déclare le pire est un diagnostic cassé.

Les deux README rapportent maintenant la probabilité moyenne prédite contre le
taux réel, et le score de Brier, qui ne dépendent d'aucune hypothèse sur l'effet
de la pondération. L'argument en faveur de D-11 en sort renforcé : la
pondération déplace les probabilités d'une manière qui dépend du modèle, donc
aucun seuil analytique unique ne s'applique aux cinq, donc il faut le mesurer.

`check_documents.py` interdit désormais `ratio_to_bayes` et `facteur 457`.

### 3. Le libellé du plan factoriel

Je parlais de la profondeur croisée avec le compteur d'usage `aa_000`. Faux :
`V1_no_flags` compte 171 colonnes, soit 180 moins 9, donc ce qu'elle retire
sont les neuf indicatrices de sous-bloc. `aa_000` est présente dans les quatre
conditions. Le plan croise la profondeur et les indicatrices, ce qui est un plan
légitime, mais le nom trompe et la redondance entre profondeur et compteur reste
non testée.

À renommer dans `scripts/paired_comparisons.py` : `V1_no_flags` devient
`V1_no_flags`, `V1_base` devient `V1_raw`, et les libellés des trois
comparaisons du plan deviennent « depth, flags present », « depth, flags
absent », « flags alone ». Les six écarts sont inchangés, seuls les noms
changent.

**Ce défaut est aussi dans le carnet 03 et dans `technical_decisions.md`**, que
je vous ai livrés plus tôt et qui décrivent le plan comme croisant la profondeur
et `aa_000`. À corriger aux deux endroits.

### Trois chiffres périmés au passage

L'étalement des fonctions de perte est 8 454 à 9 124, pas 8 368 à 9 210, et rien
ne doit être écrit sur leurs dispersions : le rapport de variances vaut 2,77
pour une probabilité de 0,34. La latence est de 50 ms en médiane, pas 34 ms en
moyenne, valeur que j'avais prise dans `latency.csv` au lieu de la distribution
des 200 appels. Et le facteur du seuil hors échantillon est 5,9, la forêt
passant de 41 050 à 6 926 et non à 6 714.

## Le démonstrateur

Un défaut que les captures d'écran montrent sans le nommer : **le curseur ne
peut pas afficher le seuil figé.** 0,0023719617 n'est pas représentable sur une
échelle linéaire de pas 0,0001, donc Streamlit le rabat sur la borne. Le
démonstrateur s'ouvre donc systématiquement sur le mauvais point de
fonctionnement, ce qui explique les 33 véhicules signalés sur 300, soit 11 % de
taux d'alerte, quand le taux réel au seuil figé est de 2,4 % sur le jeu de test.
Un lecteur du rapport verrait un système quatre fois plus bavard qu'il n'est.

Une grille logarithmique contenant la valeur exacte règle le problème, et
correspond mieux à la façon dont le seuil se comporte, sur trois décades :

```python
grid = sorted({round(v, 6) for v in np.logspace(-4, -0.3, 60)}
              | {round(predictor.threshold, 6)})
threshold = st.sidebar.select_slider(
    "Decision threshold", options=grid,
    value=round(predictor.threshold, 6),
    format_func=lambda v: f"{v:.5f}")
```

Le graphique du bas est par ailleurs tronqué par un `clip(upper=0.5)`, ce qui
masque le seul véhicule au-dessus, et son axe des abscisses est un rang de
véhicule et non une probabilité. Une courbe de coût espéré en fonction du seuil,
en échelle logarithmique, avec le seuil courant et le seuil figé en traits
verticaux, dit ce que le curseur déplace.

Enfin, le coût espéré qui monte quand le seuil baisse a besoin d'une phrase : le
seuil figé minimise le coût sur une population d'atelier à 1,67 % de pannes, pas
sur un échantillon de démonstration de 300 véhicules qui en contient un.

Les captures sont à refaire après ces corrections, recadrées sur la zone
applicative, sans barre d'URL ni bouton Deploy.

## Ce que j'ai repris de votre procédure, et ce que je n'ai pas repris

Sa partie 7 propose une suite de tests différente de la mienne. Les deux sont
complémentaires, et sur un point sa conception est meilleure que la mienne.

### Le point sur lequel elle a raison

**Mes tests lisent les données réelles et se sautent en leur absence. Un test
sauté est une intégration continue verte qui n'a rien vérifié.** Sa règle est
plus juste : aucun test ne lit `data/`, les structures sont reproduites par des
fixtures synthétiques, et la suite tourne partout.

J'ai donc ajouté `tests/test_behaviour.py`, vingt tests sans aucune donnée, et
un fichier d'intégration continue qui exécute ce module et `test_reports.py` en
entier plutôt que de laisser trois modules se sauter.

Mes modules à données réelles restent : ils vérifient des grandeurs que des
fixtures ne peuvent pas produire, la somme de contrôle, les 85 médianes
divergentes, l'accord des sous-blocs. Ils sont utiles en local et exclus de
l'intégration continue. Trois couches, trois classes d'erreur :

| Couche | Ce qu'elle attrape | Où elle tourne |
|---|---|---|
| `test_behaviour.py` | un comportement du code qui change | partout |
| `test_reports.py` | deux fichiers de résultats qui se contredisent | partout |
| `test_cost/data/missingness/pipeline/inference` | la chaîne réelle qui bouge | en local |
| `check_documents.py` | un document qui cite un chiffre périmé | partout |

### Son meilleur test, que j'ai reprise telle quelle

Le classifieur à un plus proche voisin pour attraper la fuite du seuil. Un
1-NN reproduit exactement ses lignes d'entraînement : un seuil réglé en
échantillon serait choisi contre une séparation parfaite qui n'existe pas
dehors, et resterait vers 0,5. C'est un test qui encode la difficulté M-08
directement, et il est meilleur que tout ce que j'avais écrit pour ce défaut.

### Le test qui échouera contre votre code, et pourquoi c'est intéressant

Sa version de `test_perfect_nesting_is_detected` passe les colonnes dans
l'ordre mélangé de la fixture et attend un emboîtement parfait. **Il échouera**,
parce que `nesting_report` teste l'ordre qu'on lui donne et ne trie pas.

Ce n'est pas un défaut du test, c'est une question de conception qu'il révèle.
Deux réponses possibles.

Laisser `nesting_report` tester l'ordre reçu, et faire porter le tri par
`detect_groups`, qui est ce que fait le code aujourd'hui. L'emboîtement est
alors une propriété d'un bloc muni d'un ordre, ce qui est la définition juste.
C'est l'option que j'ai retenue, et mon test l'énonce comme un contrat entre les
deux fonctions : trié, zéro exception ; mélangé, des exceptions.

Trier défensivement dans `nesting_report`. La fonction devient indépendante de
l'ordre, donc impossible à mal appeler, ce qui est exactement le défaut M-06.
C'est plus sûr et cela perd la distinction ci-dessus.

Votre difficulté M-06 est un argument pour la seconde. À vous de trancher ; si
vous triez, remplacez les trois assertions de mon test par la version de sa
partie 7.

### Ce que je ne reprendrais pas

**Sa partie 7.9, qui transforme `check_cost_function.py` en appel de pytest.**
Son motif est bon, deux copies d'un contrôle divergent. Mais le script perd
alors ses sept lignes imprimées, dont sa propre note dit qu'elles ont une valeur
narrative, et il exige pytest de qui veut seulement vérifier la métrique. Le
README l'annonce comme le point d'entrée à lancer en premier.

La bonne forme garde les deux et une seule copie de la logique : le test importe
et appelle la fonction du script.

```python
def test_the_cost_function_script_passes():
    from scripts.check_cost_function import main
    main()          # its own assertions, and its printed output
```

**Le chiffre 276 contre 315**, la dispersion entre moyennes de partitions, cité
dans son paragraphe de remplacement sur la stabilité. Il nomme
`runs/finalists_r6.csv` comme source, mais aucun script ne le calcule : c'est un
groupby par répétition, une moyenne, puis un écart type. Il est donc saisi à la
main, ce que sa propre règle interdit. Mes README citent 1 203 contre 1 307, qui
sont dans `final_model.json`. Si vous voulez garder 276 et 315, faites-les
produire par `rebuild.py`.

**Son `STALE` interdit "1 030" et "138 unit"**, ce qui déclenchera sur des
usages légitimes : 1 030 apparaîtra dans un journal citant une campagne
antérieure, et « 138 » dans toute phrase parlant du passé. Mon
`check_documents.py` ne les liste pas, et interdit en revanche les affirmations
contredites, catégorie que sa version n'a pas.

### Un accord à noter

Sur le manifeste, sa partie 4b.4 et ma correction disent la même chose : ne pas
remplacer le critère par les 396 unités. Sa formulation le rattache toutefois à
un « critère 3 de la règle préenregistrée ». La section 5 du protocole ne
prévoit pas de cascade de critères, elle désigne le coût comme critère « et le
seul ». Si le cahier des charges prévoit cette cascade, citez son article ; sinon
la formulation préenregistrée est à éviter, et c'est le point que je vous ai
signalé.