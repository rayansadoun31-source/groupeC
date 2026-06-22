# Modèle Empirique d'Émissivité

Ce dossier regroupe les scripts de calcul, les documentations et les données permettant de modéliser l'épaisseur optique et l'émissivité de l'atmosphère en combinant les spectres d'absorption des principaux gaz à effet de serre et leurs profils de concentration verticaux.

---

## Index des Documents et Livrables

### Documentation Technique
* **[`Documentation_code1.pdf`](Documentation_code1.pdf)** | *Contenu :* Rapport technique explicitant la démarche physique et le fonctionnement du premier modèle à une seule couche.
* **[`Documentation_code2.pdf`](Documentation_code2.pdf)** | *Contenu :* Rapport technique détaillant la généralisation du modèle à une structure multicouche pour simuler l'ensemble de la colonne d'air.

* **[`Documentation_code3.pdf`](Documentation_code3.pdf)** | *Contenu :* Rapport technique sur l'intégration des profils de concentrations réelles et variables pour les 4 gaz.

* **[`Documentation_code4.pdf`](Documentation_code4.pdf)** | *Contenu :* Rapport technique présentant la résolution spectrale fine avec des sections efficaces d'absorption dépendantes de la longueur d'onde.

### Outils de Calcul Spectral et Préparatoires
* **[`calcul_section_efficace_CO2_CH4_H2O.py`](calcul_section_efficace_CO2_CH4_H2O.py)** | *Application :* Script Python calculant et traçant les spectres d'absorption (sections efficaces) du CO2, du CH4 et de l'H2O en fonction de la longueur d'onde.

### Scripts de Simulation Globale (Évolution du Modèle)
* **[`code1_emissivité_une_couche.py`](code1_emissivité_une_couche.py)** | *Application :* Modèle de base calculant l'épaisseur optique et l'émissivité d'une seule tranche d'air en fonction de sa pression, de sa température et de sa concentration en CO2.

* **[`code2_emissivité_n_couche.py`](code2_emissivité_n_couche.py)** | *Application :* Script calculant l'épaisseur optique globale et l'émissivité totale d'une couche d'air en cumulant l'impact simultané de plusieurs gaz à effet de serre (CO2, CH4 et H2O).

* **[`code3_emissivite_avec_concentrations.py`](code3_emissivite_avec_concentrations.py)** | *Application :* Script calculant l'émissivité d'une couche atmosphérique en récupérant dynamiquement les concentrations réelles de gaz (CO2, CH4 et H2O) en fonction de l'altitude.

* **[`code4_emissivite_avec_section_eff.py`](code4_emissivite_avec_section_eff.py)** | *Application :* Version la plus complète du modèle. Elle calcule l'émissivité d'une couche atmosphérique en combinant à la fois les profils de concentration verticaux et les spectres d'absorption (sections efficaces) de quatre gaz (CO2, H2O, CH4 et O3).

* **['code_sciences_etonnantes_co2_traverse_atmosphere.py'](code_sciences_etonnantes_co2_traverse_atmosphere.py)** | *Application :*Script proposant un modèle unidimensionnel de transfert radiatif simulant l'effet de serre terrestre, permettant de visualiser l'impact de différentes concentrations de CO2 sur le spectre du rayonnement infrarouge s'échappant de l'atmosphère vers l'espace.

### Génération et Exportation de Données
* **[`generer_table_emissivite.py`](generer_table_emissivite.py)** | *Application :* Script final configuré pour générer et exporter un fichier de données complet (CSV) recensant l'émissivité spectrale de l'atmosphère pour chaque altitude et chaque longueur d'onde.

* **[`table_emissivite_0_20um.csv`](table_emissivite_0_20um.csv)** | *Contenu :* Tableau de données généré contenant les valeurs numériques exactes de la pression, des concentrations de gaz et de l'émissivité calculées pour chaque altitude et longueur d'onde de 0 à 20 µm.

---

## Utilisation
La progression logique du projet suit l'ordre des codes (de 1 à 4). Le script de génération de table s'appuie sur le modèle le plus avancé (`code4`) pour exporter les résultats numériques exploitables au format CSV.
