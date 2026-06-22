# Innovation : Modélisation de la Couche Atmosphérique

Ce dossier rassemble les documents d'étude et les scripts de simulation numérique permettant de modéliser l'équilibre radiatif de la Terre à travers différentes configurations de couches atmosphériques.

---

## Index des Documents et Livrables

### Documentation Technique et Scientifique
* **[modelisation1couche.pdf](https://github.com/rayansadoun31-source/groupeC/blob/3540167616d9941ed9b71325e53ea689fa27dbe9/innovations/couche_atmospherique/Documentation/modelisation1couche.pdf)** | *Contenu :* Rapport technique explicitant les calculs physiques du premier modèle à une seule couche atmosphérique.

* **[modelisation2etKcouches.pdf](https://github.com/rayansadoun31-source/groupeC/blob/b2a0e4a58ca989c7e2b82a61d1ae1cdd34478059/innovations/couche_atmospherique/Documentation/modelisation2etKcouches.pdf)** | *Contenu :* Document détaillant la physique, les développements mathématiques et l'application de la loi de Beer-Lambert pour le modèle à deux couches, puis généralisation à un nombre K de couches.

### Scripts de Simulation Numérique (Python)
* **[atmosphere_1_couche_tropausphere_8km.py](https://github.com/rayansadoun31-source/groupeC/blob/1522dc722c16e8cda4e66f158d191720cccb06ed/innovations/couche_atmospherique/Codes/atmosphere_1_couche_tropausphere_8km.py)** | *Application :* Simulation de l'équilibre radiatif de la Terre avec une couche atmosphérique globale simple.

* **[atmosphere_2_couche_tropausphere_8km.py](https://github.com/rayansadoun31-source/groupeC/blob/f279e82fc1263120dde300f40db239ca98f1a593/innovations/couche_atmospherique/Codes/atmosphere_2_couche_tropausphere_8km.py)** | *Application :* Calcul de l'impact de la concentration de CO2 sur la température de surface en divisant l'atmosphère en deux couches de masses égales.

* **[`atmosphere_n_couches_1013hpa_a_0hpa.py`](atmosphere_n_couches_1013hpa_a_0hpa.py)** | *Application :* Code de simulation le plus avancé, permettant de découper l'atmosphère en un nombre arbitraire de couches (N-couches) pour une résolution numérique plus précise.

---

## Utilisation
Les scripts Python peuvent être exécutés individuellement pour générer les profils thermiques et les courbes d'équilibre radiatif correspondant à chaque modèle théorique présenté dans les documentations.
