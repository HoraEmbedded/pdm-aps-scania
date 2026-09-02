# Notes de méthode

Annexe méthodologique des semaines 1 et 2, condensée depuis le journal de
projet. Elle conserve ce qui a une valeur technique ou méthodologique et écarte
le suivi administratif. Elle sert de matière à la partie « difficultés
rencontrées » du rapport final.

## Cadrage du problème

**La nature des deux classes.** Les camions du jeu de données sont tous déjà en
panne et déjà en atelier. La question n'est pas « ce camion est-il en bon état
ou en panne » mais « la panne vient-elle du système d'air comprimé ou d'un autre
organe ». Cela change l'interprétation d'une fausse alerte : il ne s'agit pas
d'immobiliser inutilement un camion en service, mais de faire perdre du temps à
un mécanicien qui inspecte un circuit sain sur un véhicule déjà à l'atelier.

**La règle de référence.** Le jeu de test contient 16 000 camions, dont 375 avec
une panne APS. Deux règles constantes sont possibles.

| Règle | Calcul | Coût |
|---|---|---|
| Ne jamais signaler | 375 pannes ratées à 500 | 187 500 |
| Tout signaler | 15 625 fausses alertes à 10 | 156 250 |

La seconde est la moins chère, c'est donc elle qui devient la référence à
battre. Le résultat est contre-intuitif et mérite d'être retenu : compte tenu du
rapport de coût de 50 contre 1, envoyer toute la flotte au contrôle coûte moins
cher que de laisser des camions tomber en panne.

**Décomposition de l'objectif contractuel.** L'objectif fixé est un coût
inférieur de 50 % à la référence, soit 78 125. Décomposé : un modèle qui détecte
90 % des pannes en rate 38, ce qui consomme 19 000 du budget, et il lui reste de
quoi payer environ 5 900 fausses alertes. L'objectif accepte donc un modèle dont
94,6 % des alertes seraient fausses, ce qui serait inutilisable en atelier.
Conclusion retenue : l'objectif contractuel est un plancher à franchir, pas une
cible à viser. Trois niveaux ont été proposés à la place : plancher de
recevabilité à 78 125, objectif de travail à 20 000, niveau d'excellence à
10 000.

## Choix du jeu de données

Une grille à deux étages a été construite : trois filtres binaires éliminatoires
(données réelles, étiquetage exploitable, licence académique), puis une notation
pondérée sur cinq critères à échelle explicite de 1 à 5. Trois candidats ont été
instruits, avec mesures effectuées sur les fichiers et non reprises de leur
documentation.

| Candidat | Volume | Absences | Classes |
|---|---|---|---|
| APS Scania | 60 000 x 171 et 16 000 x 171 | 8,28 % | 1,67 % de positifs |
| MetroPT-3 | 1 516 948 x 17 | aucune | aucune colonne d'étiquette |
| Engine Health | 19 535 x 7 | aucune | 63 / 37, aucun déséquilibre |

**Le jeu Engine Health n'est pas automobile.** Une vérification de provenance
jusqu'à la source d'origine a établi que le fichier diffusé sur Kaggle sous le
nom « Automotive Vehicles Engine Health » correspond à un dépôt IEEE DataPort de
novembre 2022 décrivant un moteur principal de navire. Le nom employé sur Kaggle
est un ré-étiquetage sans fondement. Conséquence : la solution de repli prévue
par le cahier des charges reposait sur une information erronée, ce qui n'aurait
été découvert qu'au moment d'en avoir besoin.

**Le choix final a été arrêté par l'encadrant** sur APS Scania. La grille et les
trois fiches sont conservées comme annexe de justification.

## Bibliographie

Treize références réparties en quatre thèmes : travaux sur le jeu Scania,
comparaison arbres contre réseaux de neurones, traitement des classes rares,
interprétation des décisions d'un modèle. Méthode de recherche dans
`bibliography_protocol.md`, références dans `references.bib`.

**Vérification de la métrique.** Les trois scores du concours 2016 ont été
reconstitués depuis le détail des erreurs, avec la règle de coût de 10 et 500.
Les trois calculs tombent juste au chiffre près, puis la vérification a été
refaite sur les onze résultats du tableau élargi, toutes les lignes se
reconstituant. Cela permet d'affirmer, et non de supposer, que la manière de
compter les coûts dans ce projet est celle du concours, sur le même jeu de test.
Les résultats publiés sont donc directement comparables.

**Performances non publiées, déduites.** Les équipes lauréates n'ont publié ni
leur taux de détection ni leur proportion d'alertes justes. Déduits du détail des
erreurs : les trois lauréats détectent entre 96 et 97,6 % des pannes, avec entre
40 et 47 % d'alertes justes, pour un coût compris entre 6,3 et 7,3 % de la
référence constante.

**Panorama des résultats publiés.** Onze résultats de 2018 à 2024. Le pire coûte
69 270, le meilleur 3 440. Trois lectures : l'état de l'art se situe à 3 440 et
non à 9 920 comme le laisserait croire la seule lecture du concours 2016 ; le
coût ne suit pas la qualité des alertes, le modèle aux alertes les plus fiables
étant aussi le plus coûteux du classement parce qu'il laisse passer 137 pannes ;
un résultat annonçant zéro fausse alerte sur 15 625 camions sains est conservé
avec réserve explicite, un tel chiffre étant difficilement crédible sur des
capteurs industriels.

**Réserve sur les objectifs chiffrés.** Les réponses du jeu de test sont
publiques depuis 2016, et les scores publiés s'améliorent régulièrement sur ce
même jeu fixe : 10 140 en 2018, 6 050 en 2019, 3 440 en 2024. C'est la signature
d'un ajustement progressif de la communauté au jeu de test. Le projet, qui
s'impose de n'ouvrir ce jeu qu'une seule fois, compare donc un résultat honnête
à des résultats dont l'indépendance n'est pas garantie. Cette réserve est écrite
plutôt que passée sous silence.

## Difficultés rencontrées

Treize difficultés recensées au terme de la semaine 2. La lettre indique la
nature : C pour la compréhension, M pour une erreur de méthode, T pour un
obstacle technique.

### Erreurs de méthode

**M-01. Une grille construite pour favoriser un candidat.** La première version
comportait un critère récompensant un jeu de données de mauvaise qualité, au
motif que le nettoyer permettrait de démontrer des compétences. Formulé ainsi,
plus les données sont dégradées, mieux c'est. Ce n'était pas un critère de
qualité mais une justification construite après coup. Le critère a été retourné
pour mesurer la charge de préparation, qui est un coût. Enseignement : une
méthode d'évaluation doit être construite avant de connaître les candidats, et
testée en vérifiant qu'un candidat autre que le favori peut l'emporter sur au
moins un critère.

**M-02. Un candidat éliminé au mauvais étage.** Engine Health était éliminé dès
les filtres binaires, sur une réserve portée à la colonne « données réelles ». Or
ce sont bien des données réelles, et les trois motifs invoqués relevaient du
second étage. Le candidat a été rétabli au premier étage puis noté au second, où
il obtient 12 points contre 34. Enseignement : lorsqu'on écarte quelque chose, la
tentation est d'employer le motif le plus rapide plutôt que le motif correct.

**M-03. Un livrable qui oubliait son objectif principal.** La première version
de la note d'état de l'art traitait le choix du jeu de données mais pas la
sélection des familles de modèles, qui était sa première exigence. Trois des
quatre thèmes de la bibliographie avaient disparu, soit huit références
inutilisées. Enseignement : relire un livrable en tenant à côté la liste des
exigences qu'il doit couvrir, et vérifier chacune séparément.

**M-04. Un raisonnement juste, non appliqué à sa propre recommandation.** Le même
document expliquait correctement pourquoi rééquilibrer les données déforme les
probabilités, puis recommandait deux sections plus loin d'appliquer les deux
corrections simultanément, ce qui compte deux fois l'asymétrie. Le mécanisme
avait été compris mais pas appliqué à la recommandation du document lui-même.
C'est cette difficulté qui a conduit à la décision D-11. Enseignement : la
cohérence entre sections d'un long document se vérifie en confrontant les
passages qui traitent d'un même sujet, pas en relisant dans l'ordre.

**M-05. Une décision validée renversée sans être nommée.** Une proposition
revenait sur une décision prise en réunion trois jours plus tôt, sans la
mentionner. Elle était par ailleurs sans effet, le calcul montrant qu'elle
aurait été plus permissive que l'objectif de coût. Enseignement : contredire une
décision prise est possible, mais cela doit être écrit et argumenté, sinon
l'historique des décisions cesse d'être fiable.

**M-06. Une inversion recopiée depuis une source officielle.** Les résultats du
concours 2016 ont d'abord été notés avec les deux types d'erreurs inversés, en
recopiant une documentation aux termes ambigus (« erreur de type 1 » pour une
fausse alerte). Le recalcul a révélé l'erreur : 199 150 au lieu des 11 480
annoncés. Règle de travail adoptée : lorsqu'une source fournit un total et son
détail, refaire le calcul. Le même principe a permis ensuite de détecter une
référence erronée dans une revue à comité de lecture.

**M-07. Un registre d'écriture inadapté.** Les premières fiches étaient rédigées
à la deuxième personne, s'adressant à leur propre auteur. Enseignement : un
livrable se relit en se demandant à qui il parle.

### Obstacles techniques

**T-01. Incompatibilité Python et TensorFlow.** Ubuntu 26.04 livre Python 3.14,
TensorFlow s'arrête à 3.13, et le réseau de neurones est une exigence
essentielle donc non abandonnable. Sans détection, le blocage serait survenu en
semaine 6, après deux mois de travail. Résolution : installation de Python 3.13
en parallèle, sans toucher à la version dont le système dépend. Enseignement :
une distribution récente n'est pas toujours un avantage, les bibliothèques
scientifiques suivant les nouvelles versions de langage avec plusieurs mois de
retard.

**T-02. Échec du premier chargement du fichier.** Deux causes cumulées : une
vingtaine de lignes de commentaires avant le tableau, et des valeurs absentes
écrites `na` en texte. La seconde était la plus dangereuse parce qu'elle ne
provoque pas d'erreur visible : sans le réglage, toutes les colonnes auraient été
traitées comme du texte et le comptage des absences aurait renvoyé zéro partout.
Enseignement : une lecture qui réussit sans message d'erreur n'est pas
nécessairement une lecture correcte, il faut vérifier les dimensions et les
types obtenus.

**T-03. Une moyenne qui masquait la réalité.** Le taux moyen d'absences de 8,3 %
suggère un jeu propre. La lecture colonne par colonne montre huit colonnes
au-delà de 65 %, dont une à 82 %, le reste étant presque complet. Le barème de la
grille, fondé sur la moyenne seule, aurait attribué la meilleure note possible.
Un second indicateur a été ajouté : le nombre de colonnes dépassant un seuil
élevé. Enseignement : devant un indicateur agrégé, regarder la distribution qui
se cache derrière.

**T-04. Un jeu de données diffusé sous un faux nom.** Voir la section sur le
choix du jeu de données. Enseignement : une plateforme de diffusion n'est pas
une source.

**T-05. La coexistence de deux systèmes.** Windows et Linux ne codent pas les
fins de ligne de la même façon, et un fichier de programme qui passe de l'un à
l'autre apparaît dans l'historique comme entièrement modifié alors que rien n'a
changé. Règle adoptée : le dépôt est la seule référence, aucun fichier de
programme ne transite par Windows.

### Difficultés de compréhension

**C-01. La nature des deux classes.** Voir la section de cadrage.

**C-02. Le rôle du code dans la démarche.** L'utilité du code n'était pas claire
au moment de construire la grille. Le lien est le suivant : chaque case de la
grille demande un chiffre qui ne figure nulle part dans la documentation des
jeux de données, et sur un fichier de 60 000 lignes et 171 colonnes, l'obtenir
passe nécessairement par du code.

### Bilan

Deux difficultés relèvent de la compréhension, sept d'une erreur de méthode,
cinq d'un obstacle technique. La répartition est instructive : les obstacles
techniques ont tous été résolus le jour même, à une exception près, tandis que
les erreurs de méthode ont imposé de reprendre entièrement la grille de
sélection et la note d'état de l'art. Aucune d'elles n'était visible dans le
résultat produit : un document biaisé, un critère construit à l'envers ou une
contradiction interne se lisent comme un travail abouti.

## Règles de travail adoptées

**Le jeu de test ne s'ouvre qu'une seule fois, à la fin du projet.** Les
réponses étant publiques depuis 2016, rien n'empêcherait techniquement de régler
le modèle en regardant son score de test puis d'annoncer un excellent résultat.
Ce serait une fuite invisible dans le rapport final.

**Les tirages aléatoires sont figés.** Pour permettre à un tiers de retrouver
les mêmes chiffres, et pour garantir que les cinq modèles sont comparés sur des
données découpées à l'identique. Limite à connaître : figer un tirage rend un
résultat reproductible, pas robuste.

**Les données brutes sont en lecture seule.** Chaque traitement produit un
nouveau fichier ailleurs.

**Les sources sont vérifiées jusqu'à l'origine** avant d'être citées, et tout
total accompagné de son détail est recalculé.

**Les livrables sont rédigés de manière impersonnelle**, et de manière à rester
compréhensibles par une personne extérieure au domaine.
