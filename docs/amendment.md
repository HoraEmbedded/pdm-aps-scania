# Avenant au cahier des charges

## Version 1.1

**Objet.** Réintégration au périmètre de l'exigence non fonctionnelle ENF05,
démonstrateur livré sous forme d'image Docker, et du livrable D8 qui en dépend.

**Motif du retrait initial.** Ces éléments avaient été retirés en application du
plan de repli de la section 13 du cahier des charges, qui désigne l'ordre
d'abandon en cas de retard : d'abord la simulation de flux, ensuite la
conteneurisation. Le retrait répondait à une contrainte de calendrier.

**Motif de la réintégration.** La contrainte de calendrier ayant disparu, le
motif du retrait n'existe plus. Le maintien de la conséquence ne se justifie
donc pas.

**Ce que la réintégration ajoute.** L'exigence ENF05, classée Importante, et le
livrable D8. Le critère de validation portant sur la reproductibilité par une
tierce personne s'en trouve par ailleurs mieux servi, l'image constituant un
environnement d'exécution identique sur toute machine.

**Ce qui reste hors périmètre.** L'exigence EF09, simulation d'un flux de
données temps réel, classée Optionnelle. Elle sera traitée si le planning le
permet, et son abandon reste conforme au plan de repli.

**Compromis assumé sur le livrable D8.** Les poids des modèles ne sont pas
versionnés dans le dépôt Git, pour des raisons de volume, de licence et de
principe. Ils sont copiés dans l'image et publiés séparément dans une
distribution GitHub, récupérable par `scripts/fetch_models.sh`. En contexte
industriel, un registre de modèles et un versionnage de données de type DVC
rempliraient cette fonction.
