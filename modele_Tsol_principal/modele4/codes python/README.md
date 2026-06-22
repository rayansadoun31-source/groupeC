# Modèle 4 : Simulation Thermique Globale et Cartographie Interactive

Ce dossier contient le cœur algorithmique du quatrième modèle de simulation. Il intègre des données géographiques, météorologiques et solaires pour modéliser l'évolution temporelle et spatiale des températures de surface de la Terre sous forme de cartes interactives.

---

## Index des Documents et Livrables

### Bibliothèques et Moteurs de Calcul
* **[`fonctions.py`](fonctions.py)** | *Contenu :* Boîte à outils logicielle contenant les fonctions nécessaires pour charger, traiter et préparer les données géographiques, météorologiques et solaires indispensables au lancement de la simulation.

* **[`lib.py`](lib.py)** | *Contenu :* Constantes physiques universelles et formules mathématiques fondamentales pour le calcul des flux d'énergie (rayonnement solaire, chaleur thermique et évaporation).

* **[`modele_courbe.py`](modele_courbe.py)** | *Application :* Programme principal pilotant la simulation. Il configure le lieu d'étude, calcule l'évolution de la température heure par heure sur deux ans et affiche les graphiques des résultats.

### Visualisations Cartographiques Globales

* **[`modele_planisphere_basse_res`](modele_planisphere_basse_res)** | *Application :* Script de simulation globale sans considérer l'innovation de l'atmosphère en basse résolution. Il permet de cliquer sur n'importe quel point de la planisphère pour afficher l'évolution thermique locale au cours du temps.

* **[`modele_planisphere_haute_res`](modele_planisphere_haute_res)** | *Application :* Script de simulation planétaire sans considérer l'innovation de l'atmosphère en haute résolution spatiale (grille interpolée fine), offrant un rendu géographique précis et un suivi interactif de l'évolution thermique par clic utilisateur.

* **[`modele_planisphere_basse_res_avec_effet_gaz`](modele_planisphere_basse_res_avec_effet_atmosphere)** | *Application :* Script de simulation globale basse résolution qui intègre un forçage radiatif atmosphérique saisonnier (provenant d'un modèle atmosphérique externe).

* **[`modele_planisphere_haute_res_avec_effet_gaz`](modele_planisphere_haute_res_avec_effet_gaz)** | *Application :* Script de simulation planétaire haute résolution qui intègre un forçage radiatif atmosphérique saisonnier (provenant d'un modèle atmosphérique externe).

* **[`modele_tres_simplifie.py`](modele_tres_simplifie.py)** | *Application :* Squelette logiciel ultra-simplifié à vocation pédagogique. 

### Outils de Post-Traitement et Couplage
* **[`generer_donnees_sol.py`](generer_donnees_sol.py)** | *Application :* Script d'extraction et d'ingénierie de données. Il lit la matrice thermique issue de la simulation basse résolution, calcule les moyennes journalières, étend les températures sur des carrés de 1°/1° et exporte une base de données CSV prête à être ingérée par le modèle des couches atmosphériques.
---

## Utilisation
Pour une analyse locale, utilisez `modele_courbe.py`. Pour des rendus visuels globaux, choisissez le script de planisphère correspondant à la résolution. Les fichiers `fonctions.py` et `lib.py` doivent impérativement rester dans le même répertoire pour assurer le bon fonctionnement des simulations.
