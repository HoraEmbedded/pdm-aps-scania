# Journal de projet. Maintenance prédictive automobile par intelligence artificielle

**Étudiante :** Lys RICHE, 4ᵉ année, cycle ingénieur, filière Génie des Systèmes Électroniques et Automatiques, ENSA de Tanger
**Encadrant :** Mike BEAUJOUR, laboratoire d'accueil
**Période couverte :** du samedi 1ᵉʳ août au dimanche 9 août 2026 (semaine 1 et début de semaine 2)
**Soutenance :** dimanche 18 octobre 2026
**Dépôt de code :** `predictive-maintenance-aps` sur GitHub (compte HoraEmbedded)

---

## Le projet en quelques phrases

Un camion moderne est équipé de capteurs qui mesurent en permanence des pressions, des températures et des compteurs d'usage. L'objectif du projet est de construire un programme capable de lire ces mesures et de dire si une panne est en train de se produire sur un composant précis, avant qu'elle n'immobilise le véhicule. C'est ce qu'on appelle la maintenance prédictive.

Le composant étudié est le système d'air comprimé du camion, en anglais Air Pressure System, abrégé APS. Il fournit l'air sous pression qui actionne notamment les freins. Les données proviennent du constructeur suédois Scania, qui les a rendues publiques en 2016.

La difficulté n'est pas de faire fonctionner un programme, mais de le faire fonctionner sur des données difficiles. Trois obstacles structurent tout le travail.

Premier obstacle : les pannes sont rares. Elles représentent moins de 2 pour cent des cas. Un programme qui répondrait systématiquement "pas de panne" aurait donc raison plus de 98 fois sur 100, tout en étant parfaitement inutile.

Deuxième obstacle : beaucoup de mesures sont absentes. Certaines colonnes de données sont vides dans plus de 80 pour cent des cas.

Troisième obstacle : les deux types d'erreurs ne coûtent pas la même chose. Ne pas détecter une vraie panne coûte 500 unités. Déclencher une fausse alerte sur un camion en bon état coûte 10 unités. Rater une panne coûte donc cinquante fois plus cher qu'une fausse alerte, et tout le travail consiste à en tenir compte.

---

## Repères administratifs

| Élément | Valeur |
|---|---|
| Durée contractuelle | 10 semaines, du 1ᵉʳ août au 9 octobre 2026 |
| Marge disponible avant la soutenance | 9 jours |
| Charge de travail hebdomadaire | 15 heures (3 heures par jour, 5 jours sur 7) |
| Charge totale prévisionnelle | environ 150 heures |
| Réunion d'avancement avec l'encadrant | chaque samedi |
| Document de référence | cahier des charges version 1.0, juillet 2026 |

Les semaines du projet courent du samedi au vendredi.

| Semaine | Dates | Contenu | Livrables attendus |
|---|---|---|---|
| S1 | 1 au 7 août | Cadrage et validation du cahier des charges | D1 |
| S2 | 8 au 14 août | État de l'art, choix du jeu de données | D2 |
| S3 | 15 au 21 août | Analyse des données et chaîne de préparation | D3 |
| S4 et S5 | 22 août au 4 septembre | Comparaison des modèles classiques. Revue de mi-parcours le 4 septembre | D6 partiel |
| S6 et S7 | 5 au 18 septembre | Réseau de neurones | D5 |
| S8 | 19 au 25 septembre | Comparaison finale et démonstrateur | D6 et D7 |
| S9 | 26 septembre au 2 octobre | Empaquetage du programme, gel du code | D4 et D8 |
| S10 | 3 au 9 octobre | Rapport final et préparation de la soutenance | D9 et D10 |

---

# Partie I. Semaine 1, du 1ᵉʳ au 7 août

## Étape 1.1. Lecture approfondie du cahier des charges

Le cahier des charges est le document contractuel qui définit ce que le projet doit produire. Il a été lu intégralement, puis huit questions de vérification ont été traitées sans le rouvrir. Note obtenue : 6,5 sur 8.

**Ce qui était acquis.** La compréhension du problème de la rareté des pannes, et celle de l'asymétrie des coûts d'erreur. Trois éléments exclus du périmètre du projet ont été correctement identifiés.

**Quatre corrections ont été nécessaires.**

La première porte sur l'objet même du projet. La réponse initiale ne retenait que le programme de démonstration. Or le projet doit produire deux choses : d'une part une comparaison rigoureuse d'au moins cinq modèles évalués dans des conditions strictement identiques, d'autre part un programme de démonstration. Ne livrer que le second serait un échec.

La deuxième porte sur la nature des données, et c'est une erreur importante. Les camions présents dans le jeu de données sont tous déjà en panne et déjà à l'atelier. La question posée n'est donc pas "ce camion est-il en bon état ou en panne", mais "la panne de ce camion vient-elle du système d'air comprimé, ou d'un autre organe". Une panne non détectée signifie concrètement qu'on ne va pas inspecter le circuit d'air, et que la vraie cause reste en place.

La troisième porte sur les critères de réussite. Un seul avait été cité alors que le cahier des charges en fixe six, tous obligatoires.

La quatrième porte sur l'ordre d'abandon en cas de retard. Le cahier des charges impose un ordre précis, désigné par des identifiants : on abandonne d'abord l'exigence EF09 (la simulation d'un flux de données en temps réel), puis l'exigence ENF05 (l'empaquetage du programme dans un conteneur Docker). Les exigences dites essentielles ne sont jamais abandonnées.

**Une objection légitime a été soulevée** par l'étudiante : pourquoi lui imposer un jeu de données plutôt que la laisser conduire elle-même la comparaison. Le cahier des charges lui donne raison. Sa section 5 prévoit que le choix définitif est validé avec l'encadrant en semaine 2, après une première analyse des candidats. Le document propose, il n'impose pas. Il a donc été décidé de construire une grille de critères et d'instruire les trois candidats.

## Étape 1.2. Mise en place de l'environnement de travail

Le cahier des charges impose de travailler sous Linux. L'ordinateur dispose d'Ubuntu 26.04 installé en double démarrage aux côtés de Windows, ce qui satisfait cette exigence. Git version 2.53 est présent, l'espace disque libre dépasse 100 gigaoctets, et un compte Kaggle a été créé pour télécharger les jeux de données.

**Un incident technique majeur a été détecté à ce stade.** Le langage Python installé par défaut sur le système est en version 3.14.4. Or TensorFlow, la bibliothèque imposée par le cahier des charges pour construire le réseau de neurones, ne prend pas en charge cette version. Elle s'arrête à la version 3.13.

La conséquence était bloquante. L'exigence EF04, qui impose d'entraîner un réseau de neurones, est classée essentielle, donc non abandonnable. Sans correction, le projet se serait heurté à ce mur en semaine 6, après deux mois de travail. La solution retenue consiste à installer la version 3.13 de Python en parallèle, sans toucher à celle du système dont Ubuntu a besoin pour fonctionner.

**Une organisation de travail a été arrêtée.** Windows sert aux échanges et à la réflexion, Linux à tout le code. Une règle en découle : le dépôt de code est la seule référence, et aucun fichier de programme ne transite par Windows. La raison est technique. Windows et Linux ne codent pas les fins de ligne de la même façon, et un fichier qui passe de l'un à l'autre apparaît dans Git comme entièrement modifié alors que rien n'a changé, ce qui rend l'historique du projet illisible.

## Étape 1.3. Création du dépôt de code et de sa structure

Un dépôt nommé `predictive-maintenance-aps` a été créé et publié sur GitHub. Un dépôt, en anglais repository, est un dossier dont chaque modification est enregistrée et datée, ce qui permet de revenir en arrière et de prouver l'historique du travail.

L'organisation retenue sépare les données brutes (`data/raw`), les données transformées (`data/processed`), les carnets d'analyse (`notebooks`), le code réutilisable (`src`), les modèles enregistrés (`models`), les résultats (`reports`) et la documentation (`docs`).

Deux principes ont été posés. Le dossier des données brutes est en lecture seule : aucune transformation ne l'écrase, chaque traitement produit un nouveau fichier ailleurs. Et les données elles-mêmes ne sont pas enregistrées dans Git, qui est conçu pour du code et non pour des fichiers volumineux. La documentation devra donc expliquer comment retélécharger les données, ce qui est précisément ce que le cahier des charges appelle la reproductibilité par une tierce personne.

Une correction a été nécessaire : Git n'enregistre pas les dossiers vides. Des fichiers marqueurs nommés `.gitkeep` ont été ajoutés pour que la structure reste visible par quelqu'un qui télécharge le dépôt.

## Étape 1.4. Installation de l'environnement Python

Python 3.13.15 a été installé en parallèle de la version du système. Un environnement virtuel a ensuite été créé. Il s'agit d'un dossier isolé contenant sa propre copie de Python et ses propres bibliothèques, ce qui garantit que le projet fonctionne indépendamment du reste de la machine.

Les bibliothèques de base ont été installées : pandas et numpy pour manipuler les tableaux de données, scikit-learn pour les modèles classiques, matplotlib et seaborn pour les graphiques, jupyter pour les carnets d'analyse. Leurs versions ont été figées dans un fichier nommé `requirements.txt`.

Les vérifications sont concluantes. La commande de version renvoie bien 3.13.15, l'environnement virtuel est bien celui utilisé, et Git confirme que les fichiers de l'environnement ne sont pas enregistrés par erreur.

**Un choix a été assumé sur le fichier de dépendances.** Ce fichier liste une centaine de bibliothèques, dont beaucoup n'ont jamais été demandées explicitement : ce sont les bibliothèques dont dépendent celles qui ont été installées. Cette liste complète est peu lisible, mais elle garantit que deux personnes installant le projet à six mois d'écart obtiennent exactement les mêmes versions, donc les mêmes résultats. C'est ce que le cahier des charges exige sous le nom de reproductibilité. La liste des six bibliothèques réellement demandées sera rappelée dans la documentation pour la lisibilité.

TensorFlow n'a volontairement pas été installé à ce stade. Il le sera au moment de son usage, avec vérification de sa compatibilité avec Python 3.13.

## Étape 1.5. Cahier des charges complété et réunion de cadrage

Les champs laissés vides dans le document ont été renseignés. La réunion de cadrage s'est tenue le samedi 8 août avec Mike BEAUJOUR, et un compte rendu a été rédigé puis diffusé.

Le premier livrable, D1, est acquis dans les délais.

## Calcul de la référence à battre

Le cahier des charges impose que le modèle final coûte nettement moins cher qu'une règle naïve de référence, c'est-à-dire une règle qui déciderait sans regarder les données. Encore fallait-il choisir laquelle, et la chiffrer.

Le jeu de test contient 16 000 camions, dont 375 avec une panne du système d'air comprimé. Deux règles naïves sont possibles.

| Règle naïve | Calcul | Coût total |
|---|---|---|
| Répondre toujours "pas une panne APS" | 375 pannes ratées, à 500 chacune | 187 500 |
| Répondre toujours "panne APS" | 15 625 fausses alertes, à 10 chacune | 156 250 |

La seconde est la moins chère. C'est donc elle qui devient la référence à battre, avec un coût de 156 250.

Ce résultat est contre-intuitif et mérite d'être retenu pour la soutenance : compte tenu du rapport de coût de 50 pour 1, envoyer l'intégralité de la flotte au contrôle revient moins cher que de laisser des camions tomber en panne sur la route.

## Analyse critique de l'objectif chiffré

L'encadrant a fixé un objectif : le modèle final doit coûter au moins 50 pour cent de moins que la règle naïve, soit un budget maximal de 78 125.

Ce chiffre a été décomposé pour voir ce qu'il autorise réellement. Un modèle qui détecte 90 pour cent des pannes en rate 38, ce qui consomme 19 000 du budget. Il lui reste donc de quoi payer environ 5 900 fausses alertes. Autrement dit, l'objectif contractuel accepte un modèle dont 94,6 pour cent des alertes seraient fausses.

Un tel taux poserait un problème concret en atelier. Un chef d'atelier qui reçoit des alertes fausses dans 19 cas sur 20 cesse rapidement de faire confiance au système, et le débranche.

Pour comparaison, un modèle qui détecterait 90 pour cent des pannes avec une alerte juste sur deux coûterait environ 22 000, soit 86 pour cent de moins que la référence naïve.

Conclusion retenue : l'objectif fixé est un plancher à franchir, pas une cible à viser.

## Décisions prises en réunion le 8 août

| Numéro | Décision |
|---|---|
| D-01 | Cahier des charges validé |
| D-02 | Aucun seuil minimal de justesse des alertes n'est imposé. L'arbitrage se fait sur le coût total |
| D-03 | Règle naïve de référence : répondre toujours "panne APS", coût 156 250 |
| D-04 | Le modèle final doit coûter au moins 50 pour cent de moins que cette référence |
| D-05 | Grille de critères et trois candidats présentés en semaine 2 |
| D-06 | Environnement pour le réseau de neurones : Python 3.13, en réponse à l'incompatibilité détectée |

Trois anomalies ont été relevées dans le compte rendu et corrigées : une mention erronée d'une version 2.0 du cahier des charges alors qu'il est en version 1.0, l'emploi d'identifiants de sections inexistants, et deux erreurs de dates. Une version rectifiée a été rediffusée à l'encadrant.

---

# Partie II. Semaine 2, les 8 et 9 août

## Étape 2.1. Construction de la grille de sélection

Une grille de critères a été construite pour comparer les trois jeux de données candidats. Deux versions ont été nécessaires.

**La première version a été rejetée** sur trois défauts. Un critère était construit à l'envers : il récompensait un jeu de données de mauvaise qualité, au motif que le nettoyer permettrait de montrer des compétences. C'est une justification fabriquée pour favoriser un candidat, pas un critère. Par ailleurs, la version confondait deux natures de critères : ceux qui éliminent un candidat, et ceux qui départagent les survivants. Enfin, aucune échelle de notation n'était définie, ce qui rendait les notes arbitraires.

**La deuxième version a été retenue.** Elle sépare le travail en deux étages. Le premier étage applique trois filtres à réponse binaire : les données sont-elles réelles, sont-elles étiquetées de manière exploitable, la licence autorise-t-elle un usage académique. Un seul "non" élimine le candidat. Le second étage note et pondère les candidats restants sur cinq critères, avec une échelle explicite de 1 à 5.

## Étape 2.2a. Premier chargement des données Scania

La première tentative de lecture du fichier a échoué avec un message d'erreur signalant une incohérence dès la ligne 8. Le diagnostic était correct : le fichier commence par une vingtaine de lignes de commentaires descriptifs avant le tableau proprement dit.

Deux réglages ont résolu le problème. Le premier demande d'ignorer ces vingt lignes. Le second indique que les valeurs absentes sont écrites `na` dans le fichier, ce que le programme ne devine pas seul. Ce second réglage était indispensable : sans lui, toutes les colonnes auraient été traitées comme du texte, et le comptage des valeurs absentes aurait renvoyé zéro partout.

## Étape 2.2. Mesures effectuées sur les trois candidats

Un carnet d'analyse de 23 cellules a été produit.

**Jeu Scania (système d'air comprimé de camions)**

| Mesure | Jeu d'entraînement | Jeu de test |
|---|---|---|
| Nombre de lignes et de colonnes | 60 000 par 171 | 16 000 par 171 |
| Proportion de pannes APS | 1,67 pour cent (1 000 cas) | 2,34 pour cent (375 cas) |
| Valeurs absentes, en moyenne | 8,28 pour cent | 8,36 pour cent |

Les valeurs absentes ne sont pas réparties uniformément. Huit colonnes dépassent 65 pour cent de valeurs absentes, dont quatre au-delà de 79 pour cent. La colonne la plus touchée est vide dans 82,1 pour cent des cas.

Le profil est presque identique entre les deux jeux, ce qui indique que les données ont été collectées de la même manière dans les deux cas.

**Jeu MetroPT-3 (compresseur d'air de rames de métro)** : 1 516 948 lignes et 17 colonnes, mesures de février à septembre 2020, aucune valeur absente, mais aucune colonne indiquant s'il y a panne ou non.

**Jeu Engine Health (moteur)** : 19 535 lignes et 7 colonnes, aucune valeur absente, répartition 63 pour cent contre 37 pour cent, donc aucun déséquilibre entre les deux classes.

### Découverte importante : le jeu Engine Health n'est pas automobile

Une vérification de provenance a été menée jusqu'à la source d'origine. Le fichier diffusé sur Kaggle sous le nom "Automotive Vehicles Engine Health" correspond exactement à un dépôt publié par Devabrat Mohakul sur la plateforme IEEE DataPort en novembre 2022, sous le titre "Predictive Maintenance on Ship's Main Engine using AI". Il décrit un moteur principal de navire, et non un véhicule automobile. Le nom employé sur Kaggle est un ré-étiquetage sans fondement.

Trois conséquences en découlent. La note de pertinence de ce candidat tombe au minimum. Le projet perd la seule solution de repli située dans le domaine automobile. Et la section 5 du cahier des charges, qui présente ce jeu comme automobile, devient inexacte, ce qui appelle une mise à jour formelle du document.

### Enseignement statistique

Le taux moyen de valeurs absentes, 8,3 pour cent, est un indicateur trompeur. Une moyenne écrase la réalité : elle ne distingue pas une situation où toutes les colonnes auraient 8 pour cent de trous d'une situation où la plupart sont parfaites et huit sont pratiquement inutilisables. C'est le second cas qui se présente ici, et les deux situations n'ont rien de comparable en termes de travail de préparation.

Le critère correspondant de la grille a donc été corrigé pour intégrer un second indicateur : le nombre de colonnes dépassant un seuil élevé de valeurs absentes.

## Décision de l'encadrant sur le jeu de données

Mike a arrêté le choix du jeu de données : ce sera APS Failure at Scania Trucks. Cette décision clôt par anticipation la phase de comparaison. Elle est conforme à la section 5 du cahier des charges, qui prévoit une validation par l'encadrant en semaine 2.

Le livrable D2 est donc recentré sur sa seconde composante, l'état de l'art. La grille et les trois fiches produites deviennent une annexe de justification, conservée parce que la question "pourquoi ce jeu de données" sera posée en soutenance, et que répondre "mon encadrant l'a décidé" serait insuffisant.

## Étape 2.4. Constitution de la bibliographie

Un fichier de bibliographie a été produit, contenant treize références réparties en quatre thèmes : les travaux menés sur le jeu Scania, la comparaison entre modèles à base d'arbres et réseaux de neurones, le traitement des situations où une classe est rare, et l'interprétation des décisions d'un modèle.

**Une erreur a été détectée et corrigée.** Les résultats du concours de 2016 étaient rapportés avec les deux types d'erreurs inversés. La vérification s'est faite par recalcul : 398 fausses alertes à 10 unités plus 15 pannes ratées à 500 unités donnent bien 11 480, alors que l'inverse donnerait 199 150. L'origine de la confusion est une terminologie ambiguë employée par la source ("erreur de type 1" désigne une fausse alerte, "erreur de type 2" une panne ratée).

De là une méthode retenue pour toute la suite : lorsqu'une source donne à la fois un total et son détail, vérifier systématiquement la cohérence par le calcul.

**Une convergence encourageante a été constatée.** Un article publié rapporte que 8 variables sur 170 dépassent 50 pour cent de valeurs absentes. La mesure effectuée indépendamment sur le fichier en identifie 8 au-delà de 65 pour cent. La littérature et la mesure propre se confirment mutuellement, ce qui valide la fiabilité de la chaîne de mesure.

## Étapes 2.5 et 2.6. Rédaction du livrable D2

**La première version a été rejetée** sur un défaut de fond. Le cahier des charges assigne au livrable D2 un objectif précis : sélectionner et justifier les familles de modèles qui entreront dans la comparaison. Or trois des quatre thèmes de la bibliographie avaient disparu entre la bibliographie et la note, laissant huit références inutilisées et le choix du réseau de neurones sans aucune justification.

**La version 1.1 est validée.** Elle compte douze sections et s'ouvre sur un encadré listant les cinq corrections apportées par l'étudiante elle-même, dont l'invalidation de deux de ses propres affirmations après lecture intégrale des sources concernées.

### Ce que le document apporte

**Une vérification de la métrique.** Les trois scores du concours de 2016 ont été reconstitués à partir du détail des erreurs, avec la règle de coût de 10 et 500. Les trois calculs tombent juste au chiffre près. Cela permet d'affirmer, et non de supposer, que la manière de compter les coûts dans ce projet est rigoureusement celle du concours, sur exactement le même jeu de test. Les résultats publiés sont donc directement comparables à ceux que produira le projet. La vérification a été refaite indépendamment sur les onze résultats du tableau élargi : toutes les lignes se reconstituent.

**Le calcul de performances non publiées.** Les équipes lauréates n'ont jamais publié leurs taux de détection ni leur proportion d'alertes justes. Ils ont été déduits du détail des erreurs : les trois lauréats détectent entre 96 et 97,6 pour cent des pannes, avec entre 40 et 47 pour cent d'alertes justes, pour un coût compris entre 6,3 et 7,3 pour cent de la référence naïve. Le projet dispose ainsi d'une cible chiffrée que la littérature ne fournit pas.

**Un panorama complet des résultats publiés**, onze au total, de 2018 à 2024. Le pire coûte 69 270, le meilleur 3 440. Trois lectures en ont été tirées. D'abord, l'état de l'art se situe à 3 440 et non à 9 920 comme le laissait croire la seule lecture du concours de 2016. Ensuite, le coût ne suit pas la qualité des alertes : le modèle dont les alertes sont les plus fiables est aussi le plus coûteux du classement, parce qu'il laisse passer 137 pannes. Enfin, un résultat annonçant zéro fausse alerte sur 15 625 camions sains a été conservé mais assorti d'une réserve explicite, car un tel chiffre est difficilement crédible sur des capteurs industriels.

**La sélection justifiée de cinq modèles**, choisis pour couvrir trois manières différentes d'apprendre : les modèles linéaires, les modèles à base d'arbres de décision, et les réseaux de neurones. C'est cette diversité qui donne son sens à la comparaison, car elle permet de conclure sur des familles de méthodes et non sur cinq programmes particuliers.

**Une hypothèse formulée de manière vérifiable.** Il existe deux façons de tenir compte du coût asymétrique : soit l'inscrire directement dans l'objectif que le modèle cherche à atteindre pendant son apprentissage, soit corriger sa décision après coup. L'hypothèse retenue est que la première fait mieux que la seconde. Le réseau de neurones est le seul modèle du panel dont l'objectif d'apprentissage puisse être librement réécrit, ce qui lui donne une raison d'être propre, au-delà de l'obligation contractuelle. Si l'hypothèse est démentie, ce sera un résultat, pas un échec.

**Un seuil de décision calculé.** Un modèle produit une probabilité, et il faut choisir à partir de quelle probabilité on déclenche une alerte. La théorie établit que ce seuil doit valoir le coût d'une fausse alerte divisé par la somme des deux coûts, soit ici environ 1,96 pour cent. Comparer des modèles au seuil habituel de 50 pour cent, sur un problème où les pannes représentent 2,34 pour cent des cas, fausserait complètement la comparaison.

**Un résultat d'expérience exploité.** Une équipe a mesuré la contribution de chaque composant de sa méthode en les retirant un par un. Retirer la prise en compte du coût dans l'objectif d'apprentissage multiplie le coût final par 5,5, bien au-delà de l'effet de toutes les autres composantes réunies. C'est le levier le plus important identifié dans tout l'état de l'art.

**Une erreur détectée dans une revue scientifique à comité de lecture**, qui cite un article sous un identifiant erroné. C'est un bon rappel, pour la soutenance, sur la propagation des références fausses.

**Trois niveaux d'objectif proposés** pour remplacer l'objectif unique : un plancher de recevabilité à 78 125 qui reste l'engagement contractuel, un objectif de travail à 20 000, et un niveau d'excellence à 10 000.

**Une proposition de restitution plutôt que de contrainte.** Plutôt que d'imposer un seuil minimal de fiabilité des alertes, qui exclurait mécaniquement des modèles moins coûteux, le rapport final présentera systématiquement le taux de détection et le taux d'alertes justes à côté du coût. Si le modèle retenu produit une proportion élevée de fausses alertes, un paragraphe traitera explicitement de son acceptabilité en atelier. Aucun modèle n'est écarté sur ce seul critère.

**Une solution de repli réexaminée puis abandonnée.** Un second jeu de données publié par Scania en 2024 avait été envisagé comme repli. Sa lecture attentive a montré qu'il pose un problème à cinq catégories et non à deux, avec une grille de coûts de cinq lignes sur cinq colonnes, et des données organisées en séries temporelles. Basculer dessus ne serait pas un repli mais un changement de sujet. La position retenue est d'assumer l'absence de repli, le risque de blocage étant très faible sur un jeu documenté depuis 2016 et exploité par onze travaux publiés.

### Trois réserves à traiter

**Une contradiction technique à trancher avant de figer le protocole.** Le document prescrit simultanément deux corrections de l'asymétrie des coûts : augmenter le poids des pannes pendant l'apprentissage, et abaisser le seuil de déclenchement des alertes. Ces deux méthodes visent le même objectif et sont des alternatives, pas des étapes à enchaîner. Les appliquer toutes les deux revient à corriger deux fois, ce qui porterait le rapport de coût effectif à environ 2 500 pour 1 au lieu de 50 pour 1. Le modèle alerterait alors sur presque tout, et son coût remonterait vers celui de la règle naïve. Trois solutions cohérentes sont possibles, et il faut en choisir une et l'écrire.

**Une réserve sur les objectifs chiffrés.** Les réponses correctes du jeu de test sont publiques depuis 2016. Or les scores publiés s'améliorent régulièrement au fil des années sur ce même jeu de test fixe : 10 140 en 2018, 6 050 en 2019, 3 440 en 2024. C'est la signature d'un phénomène connu, où une communauté finit par ajuster ses choix au jeu de test à force d'itérer contre lui, même sans le vouloir. Deux valeurs extrêmes renforcent le doute. Le projet s'étant imposé de n'ouvrir le jeu de test qu'une seule fois, il compare donc un résultat honnête à des résultats dont l'honnêteté n'est pas garantie. Cette réserve doit être écrite, et elle constitue un argument de maturité plus fort qu'un bon score.

**Une correction mineure.** Le document affirme que la régression logistique est le seul modèle produisant naturellement des probabilités fiables. C'est excessif : elle ne l'est que sous des conditions rarement réunies, et jamais si on modifie les poids des classes. À reformuler, avec une vérification empirique pour tous les modèles.

---

# Partie III. Difficultés rencontrées

Cette partie recense les difficultés au fur et à mesure du projet. Elle est destinée à alimenter le rapport final et la soutenance, où les questions portent régulièrement sur les obstacles rencontrés et la manière dont ils ont été surmontés.

Chaque difficulté porte un identifiant, pour pouvoir y renvoyer plus tard. La lettre indique la nature : C pour une difficulté de compréhension, M pour une erreur de méthode, T pour un obstacle technique, O pour un obstacle d'organisation.

La colonne de droite est laissée à compléter par l'étudiante. Elle sert à noter le temps réellement passé et ce qui reste en mémoire, deux choses qu'elle seule connaît.

## A. Difficultés de compréhension

**C-01. La nature des deux classes du jeu de données.**

La première lecture du cahier des charges a conduit à comprendre que le problème consistait à distinguer un camion en bon état d'un camion en panne. C'est faux. Tous les camions du jeu de données sont déjà en panne et déjà à l'atelier. La question posée est de savoir si la panne provient du système d'air comprimé ou d'un autre organe.

L'erreur n'était pas anodine. Elle change complètement l'interprétation d'une fausse alerte : il ne s'agit pas d'immobiliser inutilement un camion en service, mais de faire perdre du temps à un mécanicien qui inspecte un circuit sain sur un véhicule déjà à l'atelier. Elle a été corrigée lors de la fiche de lecture, puis reprise explicitement dans le livrable D2.

Ce qu'elle apprend : lire un document de cadrage ne suffit pas à comprendre un problème. Il faut se représenter la situation concrète que les données décrivent.

*Temps passé et remarques :*

**C-02. Le rôle du code informatique dans la démarche.**

Après la construction de la grille de sélection, l'utilité du code proposé n'était pas claire. La consigne enchaînait trop d'étapes à la fois sans expliquer le lien entre la grille et les mesures à effectuer.

Le lien est le suivant. Chaque case de la grille demande un chiffre, par exemple la proportion de valeurs absentes. Ce chiffre ne figure nulle part dans la documentation des jeux de données. Il faut donc le mesurer soi-même, et sur un fichier de 60 000 lignes et 171 colonnes, cela passe nécessairement par du code.

Ce qu'elle apprend, et la responsabilité en incombe à l'encadrement : une consigne qui empile plusieurs objectifs sans expliciter leur articulation produit du blocage, pas de l'apprentissage. La difficulté a été résolue en reprenant la tâche au ralenti, sur un seul jeu de données à la fois.

*Temps passé et remarques :*

## B. Erreurs de méthode

**M-01. Une grille de sélection construite pour favoriser un candidat.**

La première version de la grille comportait un critère récompensant un jeu de données de mauvaise qualité, au motif que le nettoyer permettrait de démontrer des compétences. Formulé ainsi, plus les données sont dégradées, mieux c'est. Ce n'est pas un critère de qualité, c'est une justification construite après coup pour que le jeu Scania, riche en valeurs absentes, obtienne une bonne note.

Cette erreur est la plus instructive des neuf premiers jours, pour trois raisons. Elle n'était pas intentionnelle. Elle est passée inaperçue à la relecture. Et elle est invisible dans le résultat final, puisque la grille aurait simplement désigné le candidat attendu.

Correction apportée : le critère a été retourné pour mesurer la charge de préparation, qui est un coût et non un atout. La grille a par ailleurs été restructurée en deux étages, séparant les critères qui éliminent de ceux qui départagent, et dotée d'une échelle de notation explicite.

Ce qu'elle apprend : une méthode d'évaluation doit être construite avant de connaître les candidats, et testée en vérifiant qu'un candidat autre que le favori peut l'emporter sur au moins un critère.

*Temps passé et remarques :*

**M-02. Un candidat éliminé au mauvais étage de la grille.**

La première version du livrable D2 éliminait le jeu Engine Health dès le premier étage, celui des filtres à réponse binaire, en portant une réserve dans la colonne "données réelles". Or ce sont bien des données réelles, réellement collectées sur un moteur. Les trois motifs invoqués relevaient tous du second étage.

Cette erreur donnait précisément prise au soupçon que le document cherchait par ailleurs à écarter : celui d'une méthode arrangée pour aboutir au résultat voulu.

Correction apportée : le candidat a été rétabli au premier étage, puis noté au second, où il obtient 12 points contre 34. L'élimination est donc justifiée par la notation et non par un filtre déformé.

Ce qu'elle apprend : lorsqu'on écarte quelque chose, la tentation est d'employer le motif le plus rapide plutôt que le motif correct. C'est un raccourci qui affaiblit tout le raisonnement.

*Temps passé et remarques :*

**M-03. Un livrable qui oubliait son objectif principal.**

La première version du livrable D2 était solide sur le choix du jeu de données, mais ne traitait pas ce que le cahier des charges lui demandait en premier : sélectionner et justifier les familles de modèles à comparer. Trois des quatre thèmes de la bibliographie avaient disparu entre la bibliographie et la note, soit huit références inutilisées, et le choix du réseau de neurones n'était justifié nulle part.

C'est le défaut le plus coûteux de la période. Le document faisait une trentaine de pages et paraissait complet, ce qui rend ce type d'oubli difficile à repérer par simple relecture.

Correction apportée : deux sections ont été ajoutées et la conclusion remaniée pour aboutir à une liste argumentée des cinq modèles retenus.

Ce qu'elle apprend : relire un livrable en se demandant s'il est bon ne suffit pas. Il faut le relire en tenant à côté la liste des exigences qu'il doit couvrir, et vérifier chacune séparément.

*Temps passé et remarques :*

**M-04. Un raisonnement juste, non appliqué à sa propre recommandation.**

Le livrable D2 explique correctement, dans une section, pourquoi rééquilibrer les données déforme les probabilités produites par le modèle et oblige à les corriger avant d'appliquer un seuil de décision. Deux sections plus loin, il recommande pourtant d'appliquer systématiquement les deux corrections en même temps, ce qui revient à compter deux fois l'asymétrie des coûts.

Le mécanisme avait donc été compris, mais il n'a pas été appliqué à la recommandation formulée par le document lui-même.

Cette difficulté reste ouverte à ce jour. Elle doit être tranchée avant que le protocole de comparaison ne soit figé, faute de quoi tous les résultats seraient invalides.

Ce qu'elle apprend : la cohérence entre les sections d'un long document ne se vérifie pas en le relisant dans l'ordre. Elle se vérifie en confrontant directement les passages qui traitent d'un même sujet.

*Temps passé et remarques :*

**M-05. Une décision validée renversée sans être nommée.**

La première version du livrable D2 proposait d'imposer un seuil minimal de fiabilité des alertes. Cette proposition revenait sur une décision prise et validée en réunion trois jours plus tôt, sans le mentionner.

Sur le fond, la proposition était par ailleurs inutile : le calcul montre qu'elle aurait été plus permissive que l'objectif de coût fixé par ailleurs, donc sans effet.

Correction apportée : la proposition a été retirée, la décision antérieure confirmée, et une obligation de restitution a été proposée à la place, qui n'exclut aucun modèle.

Ce qu'elle apprend : dans un projet suivi, une décision prise devient une référence. La contredire est possible, mais cela doit être écrit et argumenté, sinon l'historique des décisions cesse d'être fiable.

*Temps passé et remarques :*

**M-06. Une inversion recopiée depuis une source officielle.**

Les résultats du concours de 2016 ont d'abord été notés avec les deux types d'erreurs inversés, en recopiant une documentation qui les désigne par des termes ambigus. Le recalcul a révélé l'erreur : la version notée donnait un total de 199 150 au lieu des 11 480 annoncés.

Ce qu'elle apprend, et c'est devenu une règle de travail : lorsqu'une source fournit à la fois un total et son détail, il faut refaire le calcul. Une source officielle n'est pas une garantie. Le même principe a permis, plus tard, de détecter une référence erronée dans une revue scientifique à comité de lecture.

*Temps passé et remarques :*

**M-07. Un registre d'écriture inadapté aux livrables.**

Les premières fiches de données et la première bibliographie étaient rédigées à la deuxième personne, s'adressant à leur propre auteur. Un document versé au dépôt et destiné à nourrir le rapport final ne s'adresse pas à celui qui l'écrit.

Le problème a dû être signalé deux fois avant d'être entièrement corrigé.

Ce qu'elle apprend : un livrable se relit en se demandant à qui il parle. Si la réponse est "à moi", il n'est pas prêt.

*Temps passé et remarques :*

## C. Obstacles techniques

**T-01. Incompatibilité entre la version de Python et TensorFlow.**

Ubuntu 26.04 est livré avec Python en version 3.14, alors que TensorFlow s'arrête à la version 3.13. Or l'entraînement d'un réseau de neurones sous TensorFlow est une exigence essentielle du cahier des charges, donc non abandonnable.

Sans détection, le blocage serait survenu en semaine 6, après deux mois de travail, et sans solution de repli puisque l'exigence ne peut pas être écartée.

Résolution : installation de Python 3.13 en parallèle, sans toucher à la version du système dont Ubuntu dépend pour fonctionner. L'incident a été signalé à l'encadrant dans les vingt-quatre heures et acté comme décision de réunion.

Ce qu'il apprend : une distribution récente n'est pas toujours un avantage. Les bibliothèques scientifiques suivent les nouvelles versions de langage avec plusieurs mois de retard, et il faut vérifier la compatibilité avant de commencer, pas au moment de s'en servir.

*Temps passé et remarques :*

**T-02. Échec du premier chargement du fichier de données.**

La première tentative de lecture du fichier Scania a échoué sur un message d'erreur signalant une incohérence dès la huitième ligne. Deux causes se cumulaient. Le fichier commence par une vingtaine de lignes de commentaires descriptifs avant le tableau proprement dit. Et les valeurs absentes y sont écrites sous forme de texte, ce que le programme ne devine pas seul.

La seconde cause était la plus dangereuse, car elle ne provoque pas d'erreur visible. Sans le réglage correspondant, le fichier se serait chargé sans message, toutes les colonnes auraient été traitées comme du texte, et le comptage des valeurs absentes aurait renvoyé zéro partout. L'analyse aurait donc été entièrement fausse, sans le moindre signe d'alerte.

Ce qu'il apprend : un fichier de données réelles ne s'ouvre presque jamais correctement du premier coup. Et une lecture qui réussit sans message d'erreur n'est pas nécessairement une lecture correcte. Il faut vérifier les dimensions et les types obtenus.

*Temps passé et remarques :*

**T-03. Une moyenne qui masquait la réalité des données.**

Le taux moyen de valeurs absentes du jeu Scania est de 8,3 pour cent, ce qui suggère un jeu de données propre. La lecture colonne par colonne montre autre chose : huit colonnes dépassent 65 pour cent de valeurs absentes, dont une à 82 pour cent, tandis que la plupart des autres sont presque complètes.

Les deux situations n'ont rien de comparable en termes de travail de préparation, et le barème de la grille, qui reposait sur la moyenne seule, aurait attribué la meilleure note possible à ce jeu.

Le résultat détaillé figurait dans le carnet d'analyse mais n'avait pas été exploité.

Ce qu'il apprend : une moyenne résume une distribution en l'écrasant. Devant un indicateur agrégé, il faut regarder la distribution qui se cache derrière avant de conclure.

*Temps passé et remarques :*

**T-04. Un jeu de données diffusé sous un faux nom.**

Le fichier diffusé sur Kaggle sous le nom "Automotive Vehicles Engine Health" décrit en réalité un moteur principal de navire. La vérification jusqu'à la source d'origine a permis de l'établir.

Deux conséquences. La solution de repli prévue par le cahier des charges reposait sur une information erronée, ce qui n'aurait été découvert qu'au moment d'en avoir besoin. Et la section correspondante du document contractuel doit être corrigée.

Ce qu'il apprend : une plateforme de diffusion n'est pas une source. Le nom sous lequel un jeu de données circule ne garantit ni son contenu ni son domaine d'application.

*Temps passé et remarques :*

**T-05. Un obstacle non technique mais structurant : la coexistence de deux systèmes.**

Le travail se répartit entre Windows pour les échanges et la réflexion, et Linux pour tout le code. Cette organisation est imposée par des contraintes extérieures au projet.

Le risque associé est réel. Les deux systèmes ne codent pas les fins de ligne de la même façon, et un fichier de programme qui passe de l'un à l'autre apparaît dans l'historique du dépôt comme entièrement modifié alors que rien n'a changé. L'historique du projet en deviendrait illisible, ce qui compromettrait une exigence du cahier des charges.

Règle adoptée : le dépôt de code est la seule référence, aucun fichier de programme ne transite par Windows, et seuls des textes sont recopiés d'un système à l'autre.

*Temps passé et remarques :*

## D. Bilan intermédiaire sur les difficultés

Sur les treize difficultés recensées au 9 août, deux relèvent de la compréhension, sept d'une erreur de méthode, et cinq d'un obstacle technique.

La répartition est instructive. Les obstacles techniques ont tous été résolus le jour même, à l'exception d'un seul qui a demandé l'installation d'une seconde version de Python. Les erreurs de méthode ont coûté beaucoup plus cher, puisqu'elles ont imposé de reprendre entièrement la grille de sélection et le livrable D2. Et surtout, aucune d'elles n'était visible dans le résultat produit : un document biaisé, un critère construit à l'envers ou une contradiction interne se lisent comme un travail abouti.

Une seule difficulté reste ouverte à ce jour, M-04, et c'est la plus grave, puisqu'elle invaliderait l'ensemble des comparaisons si elle n'était pas tranchée avant la construction du protocole.

---

# Partie IV. Règles de travail adoptées

**Le jeu de test ne s'ouvre qu'une seule fois, à la toute fin du projet.** Tous les réglages se font sur une partie des données d'entraînement mise de côté à cet effet. Cette règle existe parce que les réponses du jeu de test sont publiques : rien n'empêcherait techniquement de régler le modèle en regardant son score de test, puis d'annoncer un excellent résultat. Ce serait ce qu'on appelle une fuite de données, invisible dans le rapport final, et le score annoncé ne dirait plus rien des performances réelles. La règle est inscrite dans la documentation du dépôt.

**Les tirages aléatoires sont figés.** Un apprentissage comporte de nombreux tirages au sort : le découpage des données, l'ordre dans lequel elles sont présentées, les valeurs initiales d'un réseau de neurones. Les figer sert deux choses. D'abord permettre à quelqu'un d'autre de retrouver exactement les mêmes chiffres. Ensuite garantir que les cinq modèles sont comparés sur des données découpées à l'identique, faute de quoi on ne comparerait plus les modèles mais les tirages. Une limite à connaître : figer un tirage rend un résultat reproductible, pas robuste.

**Le dépôt de code est la seule référence.** Aucun fichier de programme ne transite par Windows.

**Les données brutes sont en lecture seule.** Chaque traitement produit un nouveau fichier.

**Les sources sont vérifiées jusqu'à l'origine** avant d'être citées, et tout total accompagné de son détail est recalculé.

**Les livrables sont rédigés de manière impersonnelle**, sans tutoiement ni adresse au lecteur, et de manière à rester compréhensibles par une personne extérieure au domaine.

---

# Partie V. Ce qui reste à faire

## A. Actions immédiates

| Numéro | Action | Échéance |
|---|---|---|
| 1 | Trancher la contradiction entre pondération des classes et seuil de décision, et écrire la décision | avant de figer le protocole |
| 2 | Ajouter au livrable D2 la réserve sur la fiabilité des résultats publiés | avant le 15 août |
| 3 | Reformuler l'affirmation sur les probabilités de la régression logistique | avant le 15 août |
| 4 | Corriger l'inversion des deux types d'erreurs dans la fiche du jeu Scania | avant le 15 août |
| 5 | Vérifier que la règle du jeu de test figure bien dans la documentation du dépôt | immédiat |
| 6 | Mettre à jour le classeur de suivi (livrables D1 et D2, exigences couvertes) | samedi |
| 7 | Terminer l'analyse des valeurs absentes engagée en fin de séance | en cours |

## B. Points à porter à l'encadrant le samedi 15 août

Présentation du livrable D2 et demande de validation.

Demande de mise à jour du cahier des charges en version 1.1, portant sur six points : corriger l'identification du jeu Engine Health, acter le troisième candidat instruit et son élimination, acter le choix définitif du jeu de données, confirmer sans modification la décision sur l'absence de seuil de fiabilité, reconstruire la solution de repli sur le jeu de données, et annexer les trois niveaux d'objectif ainsi que la proposition de restitution.

Signalement que la solution de repli prévue par le cahier des charges reposait sur une information erronée.

Présentation spontanée de la remarque d'honnêteté méthodologique sur la grille de sélection, plutôt que d'attendre qu'elle soit soulevée.

## C. Feuille de route technique

**Semaine 3, du 15 au 21 août, livrable D3.** Analyse approfondie des données et construction de la chaîne de préparation. Il faudra décider par écrit du sort des huit colonnes presque vides, soit les supprimer soit les compléter. Il faudra comparer au moins deux méthodes de remplacement des valeurs absentes. Il faudra traiter les sept variables de type histogramme, qui décomposent une mesure en plusieurs tranches de valeurs. Il faudra enfin mettre en place le traitement de la rareté des pannes.

**Semaines 4 et 5, du 22 août au 4 septembre, livrable D6 partiel.** Comparaison des quatre modèles classiques dans des conditions identiques : régression logistique, forêt aléatoire, gradient boosting et machine à vecteurs de support. Le réglage du seuil de décision devient une étape obligatoire du protocole, appliquée de la même façon à tous les modèles. Un point de vigilance devra être repris : les pannes représentent 1,67 pour cent des données d'entraînement mais 2,34 pour cent des données de test, ce qui rend les scores obtenus en interne non directement comparables aux scores finaux. La revue de mi-parcours a lieu le 4 septembre.

**Semaines 6 et 7, du 5 au 18 septembre, livrable D5.** Construction du réseau de neurones. Écriture explicite d'un objectif d'apprentissage tenant compte du coût, qui est le levier identifié comme le plus important par l'état de l'art, et test de l'hypothèse formulée dans D2. Réglage des paramètres et enregistrement des modèles entraînés. Recours possible aux plateformes de calcul gratuites si la machine ne suffit pas.

**Semaine 8, du 19 au 25 septembre, livrables D6 et D7.** Comparaison finale et choix argumenté du modèle. Rédaction du rapport de comparaison avec tableaux, courbes et grilles d'erreurs. Trois points de repère externes y figureront : la règle naïve à 156 250, la valeur médiane des travaux publiés autour de 10 140, et le meilleur résultat publié à 3 440. Analyse des pannes que le modèle rate, et analyse des variables les plus influentes, sachant que leur signification physique restera inconnue puisque les noms de capteurs sont anonymisés. Développement du programme de démonstration.

**Semaine 9, du 26 septembre au 2 octobre, livrables D4 et D8.** Empaquetage du programme dans un conteneur Docker, rédaction de la notice d'installation, gel du code et publication finale du dépôt. La simulation d'un flux de données en temps réel ne sera réalisée que si le planning le permet, car c'est le premier élément à abandonner en cas de retard.

**Semaine 10, du 3 au 9 octobre, livrables D9 et D10.** Rédaction du rapport final et préparation de la soutenance, en reprenant un par un les six critères de réussite du cahier des charges.

**Du 10 au 18 octobre.** Marge de neuf jours, à consacrer aux répétitions de la soutenance.

## D. État des livrables

| Numéro | Livrable | Échéance | État |
|---|---|---|---|
| D1 | Cahier des charges validé par l'encadrant | S1 | acquis |
| D2 | État de l'art et choix du jeu de données justifié | S2 | version 1.1, à présenter le 15 août |
| D3 | Analyse des données et chaîne de préparation | S3 | entamé |
| D4 | Code source complet versionné | S9 | en continu |
| D5 | Modèles entraînés enregistrés | S7 | à venir |
| D6 | Rapport de comparaison des modèles | S8 | à venir |
| D7 | Programme de démonstration | S8 | à venir |
| D8 | Conteneur Docker et notice d'installation | S9 | à venir |
| D9 | Rapport final écrit | S10 | à venir |
| D10 | Support de soutenance | S10 | à venir |

## E. Questions de jury accumulées

Questions déjà travaillées : la valeur réelle d'un taux de bonnes réponses de 98 pour cent, la justification du choix du jeu de données, les garanties de reproductibilité, le rôle des tirages aléatoires figés, et le positionnement face au score de 9 920 des lauréats de 2016.

Questions restant à préparer : pourquoi trois candidats et non dix, comment le ré-étiquetage du jeu Engine Health a été découvert, pourquoi consacrer deux semaines à un réseau de neurones alors que la littérature donne l'avantage aux arbres sur ce type de données, pourquoi viser 20 000 quand le meilleur résultat publié est à 3 440, et comment savoir que les résultats publiés ne sont pas ajustés au jeu de test.

---

# Partie VI. Bilan d'étape

**Le projet est en avance.** Le premier livrable a été rendu dans les délais, le deuxième est achevé six jours avant son échéance, et une étape relevant de la semaine 3 est déjà engagée. Cette avance constitue une réserve, qui sera consommée par la comparaison des modèles en semaines 4 et 5, phase habituellement sous-estimée.

**Deux risques ont été neutralisés avant de coûter quoi que ce soit.** L'incompatibilité entre la version de Python installée et la bibliothèque TensorFlow aurait bloqué le projet en semaine 6, après deux mois de travail. Elle a été détectée au septième jour. La solution de repli prévue par le cahier des charges reposait sur un jeu de données mal identifié, ce qui a été découvert avant qu'on ait besoin d'y recourir.

**Un risque reste ouvert et prioritaire.** La contradiction entre les deux méthodes de correction du coût doit être tranchée avant que le protocole de comparaison ne soit figé. La laisser passer invaliderait l'ensemble des résultats.

**Ce que je retiens de ces neuf jours :**

*(à compléter)*

**Ce qui m'a le plus coûté :**

*(à compléter)*
