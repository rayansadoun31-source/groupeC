# Étude Thermique et Climatique Terrestre — Guide Global

Ce dépôt rassemble les outils de modélisation, de simulation numérique et d'analyse théorique dédiés à l'étude thermique du sol et à l'équilibre radiatif de l'atmosphère terrestre.

---

## 1. **[Modèle de Température du Sol Principal](https://github.com/rayansadoun31-source/groupeC/tree/aa3bf43b5cd8a6b7cbe0ac0e3ccbc495b7583dd5/modele_Tsol_principal)**

Ce dossier constitue le cœur de l'étude thermique au sol. Il regroupe les approches numériques et théoriques développées pour simuler et valider l'évolution des températures de surface ainsi que les flux d'énergie terrestres. Il permet à la fois de générer des projections thermiques temporelles (courbes heure par heure), de visualiser des cartographies mondiales interactives (2D et 3D), et de consulter les rapports scientifiques validant la physique du modèle (notamment sur la conduction et la convection).

---

## 2. **[Innovations](https://github.com/rayansadoun31-source/groupeC/tree/a837d0cbc8a54691fe11ba51e4b2b01bdc484cc4/innovations)**

Ce dossier regroupe l'ensemble des travaux, modélisations et simulations numériques dédiés à l'étude globale du climat terrestre. Il permet d'analyser la structure verticale de l'atmosphère, de quantifier l'émissivité et l'épaisseur optique des gaz à effet de serre (via des données empiriques ou la base de données quantiques HITRAN), d'intégrer l'albédo et la réflexion du rayonnement par les nuages à partir de données météo réelles, et enfin de simuler l'impact climatique global sur la température de surface à l'aide de modèles d'atmosphère à $N$ couches.

## 3. **[Données](https://github.com/rayansadoun31-source/groupeC/tree/main/donnees)**
Ce dossier centralise les ressources du modèle atmosphérique, regroupant les données brutes de simulation (matrices de forçage mensuelles .npy et carte globale d'émissivité .tif), les tables de référence spectrales .csv issues de la base HITRAN, ainsi qu'un script Python (visualiser_rendu_atm.py) permettant d'analyser et de visualiser graphiquement les résultats.
---

> **Note :** Chaque dossier principal contient sa propre documentation détaillée avec les instructions d'exécution et les rapports d'analyse associés.
