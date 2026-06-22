# Innovations

Ce dossier principal regroupe l'ensemble des travaux, modélisations et simulations numériques dédiés à l'étude du climat terrestre, depuis l'analyse physique de l'atmosphère jusqu'à la simulation de l'équilibre radiatif de la Terre.

Le projet est découpé en trois grands volets complémentaires :

---

## Structure du Projet

### 1. [Températures et Concentrations Atmosphériques](./températures_et_concentrations/)
Ce premier dossier est dédié à l'étude de la structure verticale de l'atmosphère. Il pose les bases physiques du projet en modélisant l'évolution de la température et la répartition des profils de concentration des principaux gaz à effet de serre ($H_2O$, $CH_4$, $CO_2$, $O_3$) en fonction de l'altitude.

### 2. [Émissivité Atmosphérique](./émissivité_atmosphérique/)
Ce dossier central est consacré à l'étude quantitative de l'épaisseur optique et de l'émissivité de l'atmosphère terrestre. Il explore et compare deux approches numériques : une méthode empirique basée sur des approximations de spectres d'absorption, et une méthode haute résolution s'appuyant sur les données quantiques officielles de la base internationale HITRAN.

### 3. [Modélisation de la Couche Atmosphérique](./modélisation_couche_atmo/)
Ce dernier dossier se concentre sur l'équilibre radiatif global de la Terre. À partir des données de température et d'émissivité, il simule l'impact des gaz à effet de serre sur la température de surface en testant différentes configurations de découpage de l'atmosphère (modèles à 1 couche, 2 couches, puis généralisation à un nombre $N$ de couches).

---

## Logique de Progression

Pour naviguer efficacement dans ce projet, il est recommandé de suivre cette démarche :
1. Comprendre la structure physique de base et la répartition des gaz (**Températures et Concentrations**).
2. Analyser comment ces gaz absorbent et émettent l'énergie (**Émissivité Atmosphérique**).
3. Observer l'impact climatique global à travers les simulations radiatives (**Modélisation de la Couche Atmosphérique**).

*Note : Pour le détail des scripts, des rapports physiques et des instructions d'exécution, veuillez vous référer au fichier `README.md` spécifique présent à l'intérieur de chaque dossier.*
