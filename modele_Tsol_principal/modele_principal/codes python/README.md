# Modèle Principal : Simulation Thermique Globale et Cartographie Interactive

Ce dossier contient le cœur algorithmique du quatrième modèle de simulation. Il intègre des données géographiques, météorologiques et solaires pour modéliser l'évolution temporelle et spatiale des températures de surface de la Terre sous forme de cartes interactives.

---

## Index des Documents et Livrables

### Bibliothèques et Moteurs de Calcul
* **[`fonctions.py`](fonctions.py)** | *Contenu :* Boîte à outils logicielle contenant les fonctions nécessaires pour charger, traiter et préparer les données géographiques, météorologiques et solaires indispensables au lancement de la simulation.

* **[`lib.py`](lib.py)** | *Contenu :* Constantes physiques universelles et formules mathématiques fondamentales pour le calcul des flux d'énergie (rayonnement solaire, chaleur thermique et évaporation).

### Visualisations Cartographiques Globales

* **[`modele_planisphere_basse_res`](modele_planisphere_basse_res)** | *Application :* Script de simulation globale basse résolution.

* **[`modele_planisphere_haute_resz`](modele_planisphere_haute_res)** | *Application :* Script de simulation planétaire haute résolution.

* **[`modele_tres_simplifie.py`](modele_tres_simplifie.py)** | *Application :* Squelette logiciel ultra-simplifié à vocation pédagogique. 

### Outils de Post-Traitement et Couplage
* **[`generer_donnees_sol.py`](generer_donnees_sol.py)** | *Application :* Script d'extraction et d'ingénierie de données. Il lit la matrice thermique issue de la simulation basse résolution, calcule les moyennes journalières, étend les températures sur des carrés de 1°/1° et exporte une base de données CSV prête à être ingérée par le modèle des couches atmosphériques.
---

## Utilisation
Pour un rendu visuel global, choisissez le script de planisphère correspondant à la résolution désirée. Les fichiers `fonctions.py` et `lib.py` doivent impérativement rester dans le même répertoire pour assurer le bon fonctionnement des simulations.
