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

**Distribution actuelle.** Les poids du modèle ne sont pas versionnés dans
Git. Le [guide de reproduction](reproduction.md) décrit la reconstruction
locale du modèle retenu et de son prétraitement à partir des données UCI, puis
la construction de l'image Docker.

**Essais de débit ajoutés après l'étude.** Le projet contient une
[simulation de requêtes](../scripts/flow_simulation.py) et des
[mesures sur Raspberry Pi](../reports/flow/pi/). Ces essais évaluent la
capacité de l'API. Ils ne constituent pas une acquisition de capteurs en temps
réel ni une validation sur des véhicules en circulation.
