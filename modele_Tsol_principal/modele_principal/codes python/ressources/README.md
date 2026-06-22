# Ressources de Simulation (Modèle 4)

Ce dossier regroupe l'ensemble des données d'entrée, des fichiers de géolocalisation, des configurations de cartes et des tableaux de données physiques indispensables au fonctionnement des scripts du Modèle 4.

---

## Index des Répertoires et Données

### Dossier `Cp_humidity/` (Propriétés du Sol)
* **[`average_rzsm_tout.csv`](Cp_humidity/average_rzsm_tout.csv)** | *Données :* Cartographie globale découpant la Terre en mailles de 0,25° de latitude et de longitude pour y associer une valeur locale de l'humidité du sol.

* **[`ZZ_cp.py`](Cp_humidity/ZZ_cp.py)** | *Application :* Script de calcul déterminant la capacité thermique massique ($C_p$) du sol en fonction des valeurs d'humidité extraites.

### Dossier `albedo/` (Réflectivité)
* **`albedo/`** | *Données :* Ensemble des fichiers regroupant les valeurs d'albédo de la surface terrestre indexées en fonction de la position géographique.

### Dossier `data/` (Géographie des Continents)
* **`data/`** | *Données :* Fichiers de coordonnées géospatiales permettant de délimiter précisément les contours des continents pour la simulation.

### Dossier `map/` (Propriétés Thermiques Régionales)
* **`map/`** | *Données :* Fichiers d'identification permettant d'associer à chaque coordonnée géographique le nom du continent correspondant et sa constante de chaleur latente associée.

### Dossier `npy/` (Matrices de Résultats Précalculées)
* **`npy/`** | *Données :* Fichiers binaires NumPy stockant les matrices précalculées pour les rendus de planisphères et de sphères, disponibles en basse et haute résolution sur des échelles de temps de 1 ou 2 ans de simulation.

---

## Documents d'Étude

### Rapport et Sources
* **[`données sourcées.pdf`](données%20sourcées.pdf)** | *Contenu :* Document de synthèse regroupant les données physiques, les constantes de référence et les publications scientifiques ayant servi à nourrir les paramètres de nos modèles.
