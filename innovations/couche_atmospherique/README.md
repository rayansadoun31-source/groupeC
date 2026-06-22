# Innovation : Modélisation de la Couche Atmosphérique

Ce dossier rassemble les documents d'étude et les scripts de simulation numérique permettant de modéliser l'équilibre radiatif de la Terre à travers différentes configurations de couches atmosphériques.

---

## Index des Documents et Livrables

### Documentation Technique et Scientifique
* **[Documentation_1_couche.pdf](https://github.com/rayansadoun31-source/groupeC/blob/3540167616d9941ed9b71325e53ea689fa27dbe9/innovations/couche_atmospherique/Documentation/modelisation1couche.pdf)** | *Contenu :* Rapport technique explicitant les calculs physiques du premier modèle à une seule couche atmosphérique.

* **[`Documentation_2_couche.pdf`](Documentation_2_couche.pdf)** | *Contenu :* Document détaillant la physique, les développements mathématiques et l'application de la loi de Beer-Lambert pour le modèle à deux couches, puis généralisation à un nombre K de couches.

### Scripts de Simulation Numérique (Python)
* **[`atmosphere_1_couche_tropausphere_8km.py`](atmosphere_1_couche_tropausphere_8km.py)** | *Application :* Simulation de l'équilibre radiatif de la Terre avec une couche atmosphérique globale simple.

* **[`atmosphere_2_couche_tropausphere_8km.py`](atmosphere_2_couche_tropausphere_8km.py)** | *Application :* Calcul de l'impact de la concentration de CO2 sur la température de surface en divisant l'atmosphère en deux couches de masses égales.

* **[`atmosphere_n_couches_1013hpa_a_0hpa.py`](atmosphere_n_couches_1013hpa_a_0hpa.py)** | *Application :* Code de simulation le plus avancé, permettant de découper l'atmosphère en un nombre arbitraire de couches (N-couches) pour une résolution numérique plus précise.

---

## Utilisation
Les scripts Python peuvent être exécutés individuellement pour générer les profils thermiques et les courbes d'équilibre radiatif correspondant à chaque modèle théorique présenté dans les documentations.
