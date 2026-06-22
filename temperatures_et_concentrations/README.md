# Températures et Concentrations Atmosphériques

Ce dossier regroupe les scripts de modélisation, les codes d'étude et les documentations explicatives permettant d'analyser la structure verticale de l'atmosphère, notamment l'évolution de la température et la répartition des profils de concentration des gaz à effet de serre en fonction de l'altitude.

---

## Index des Documents et Livrables

### Documentation et Analyses Théoriques
* **[`Version_1-projet_climat`](Version_1-projet_climat)** | *Contenu :* Première version d'étude combinant les calculs de concentration de chaque gaz à effet de serre (GES) en fonction de l'altitude et des profils thermiques.

* **[`Commentaire_code.pdf`](Commentaire_code.pdf)** | *Contenu :* Rapport technique contenant les explications détaillées, la démarche physique et la structure algorithmique du programme de la version 1.

### Scripts de Modélisation (Python)
* **[`code_température_altitude.py`](code_température_altitude.py)** | *Application :* Script Python dédié à la modélisation mathématique et physique de la variation de la température en fonction de l'altitude au sein des différentes couches atmosphériques.

* **[`code_H20_CH4_CO2_O3.py`](code_H20_CH4_CO2_O3.py)** | *Application :* Script Python permettant de calculer et de tracer l'évolution des profils verticaux de concentration des principaux gaz de l'atmosphère (H2O, CH4, CO2 et O3) en fonction de l'altitude.

---

## Utilisation
Ces modules posent les bases de la discrétisation atmosphérique. Les données de concentration et de température générées par ces codes servent d'entrées physiques pour les modèles d'émissivité plus avancés du projet.
