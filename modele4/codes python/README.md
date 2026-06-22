# Modèle 4 : Simulation Thermique Globale et Cartographie Interactive

Ce dossier contient le cœur algorithmique du quatrième modèle de simulation. Il intègre des données géographiques, météorologiques et solaires pour modéliser l'évolution temporelle et spatiale des températures de surface de la Terre sous forme de cartes interactives (planisphères et sphères).

---

## Index des Documents et Livrables

### Bibliothèques et Moteurs de Calcul
* **[`fonctions.py`](fonctions.py)** | *Contenu :* Boîte à outils logicielle contenant les fonctions nécessaires pour charger, traiter et préparer les données géographiques, météorologiques et solaires indispensables au lancement de la simulation.

* **[`lib.py`](lib.py)** | *Contenu :* Constantes physiques universelles et formules mathématiques fondamentales pour le calcul des flux d'énergie (rayonnement solaire, chaleur thermique et évaporation).

* **[`modele_courbe.py`](modele_courbe.py)** | *Application :* Programme principal pilotant la simulation. Il configure le lieu d'étude, calcule l'évolution de la température heure par heure sur deux ans et affiche les graphiques des résultats.

### Visualisations Cartographiques Globales
* **[`modele_planisphere_basse_res.py`](modele_planisphere_basse_res.py)** | *Application :* Simulation et affichage d'une carte mondiale (planisphère) des températures de surface en basse résolution, avec choix entre un modèle simplifié ou un modèle complet nourri par des données géospatiales.

* **[`modele_planisphere_haute_res.py`](modele_planisphere_haute_res.py)** | *Application :* Simulation et affichage d'une carte mondiale (planisphère) des températures de surface en haute résolution, avec choix entre un modèle simplifié ou un modèle complet nourri par des données géospatiales.

* **[`modele_sphere_basse_res.py`](modele_sphere_basse_res.py)** | *Application :* Simulation et affichage tridimensionnel d'une carte mondiale (sphère) des températures de surface en basse résolution.

* **[`modele_sphere_haute_res.py`](modele_sphere_haute_res.py)** | *Application :* Simulation et affichage tridimensionnel d'une carte mondiale (sphère) des températures de surface en haute résolution.

### Versions Interactives Avancées
* **[`modele_planisphere_basse_res_interactif`](modele_planisphere_basse_res_interactif)** | *Application :* Script de simulation globale interactive en basse résolution. Il permet de cliquer sur n'importe quel point de la planisphère pour afficher l'évolution thermique locale au cours du temps.

* **[`modele_planisphere_haute_res_interactif`](modele_planisphere_haute_res_interactif)** | *Application :* Script de simulation planétaire avancée en haute résolution spatiale (grille interpolée fine), offrant un rendu géographique précis et un suivi interactif de l'évolution thermique par clic utilisateur.

### Outils de Post-Traitement et Couplage
* **[`generer_donnees_sol.py`](generer_donnees_sol.py)** | *Application :* Script d'extraction et d'ingénierie de données. Il lit la matrice thermique issue de la simulation basse résolution, calcule les moyennes journalières, étend les températures sur des carrés de 1°/1° et exporte une base de données CSV prête à être ingérée par le modèle des couches atmosphériques.
---

## Utilisation
Pour une analyse locale, utilisez `modele_courbe.py`. Pour des rendus visuels globaux, choisissez le script de planisphère ou de sphère correspondant à la résolution et au niveau d'interactivité souhaités. Les fichiers `fonctions.py` et `lib.py` doivent impérativement rester dans le même répertoire pour assurer le bon fonctionnement des simulations.
