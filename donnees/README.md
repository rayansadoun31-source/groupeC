# Base de Données et Visualisation - Modèle Atmosphérique

Ce répertoire regroupe les jeux de données brutes (matrices de forçage, cartographie d'émissivité, tables spectrales) ainsi que les outils de visualisation nécessaires à l'analyse de notre modèle atmosphérique.

---

##  Index des Fichiers

### Matrices de Forçage Atmosphérique (Fichiers NumPy)
Ces fichiers stockent les données vectorielles et les calculs de forçage atmosphérique évalués sur différents mois représentatifs de l'année.

* **[Forcage_Atmospherique_6_FEVRIER.npy](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/Forcage_Atmospherique_6_FEVRIER.npy)** : Matrice de données contenant les valeurs de forçage atmosphérique modélisées pour le mois de février.
* **[Forcage_Atmospherique_6_MAI.npy](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/Forcage_Atmospherique_6_MAI.npy)** : Matrice de données contenant les valeurs de forçage atmosphérique modélisées pour le mois de mai.
* **[Forcage_Atmospherique_6_AOUT.npy](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/Forcage_Atmospherique_6_AOUT.npy)** : Matrice de données contenant les valeurs de forçage atmosphérique modélisées pour le mois d'août.
* **[Forcage_Atmospherique_6_NOVEMBRE.npy](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/Forcage_Atmospherique_6_NOVEMBRE.npy)** : Matrice de données contenant les valeurs de forçage atmosphérique modélisées pour le mois de novembre.

### Cartographie Globale
* **[emissivite_mondiale_365jours.tif](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/emissivite_mondiale_365jours.tif)** : Fichier d'image géospatiale (TIFF) représentant la carte globale de l'émissivité terrestre simulée et consolidée sur une année complète de 365 jours.

### Tables de Données et Spectres (Fichiers CSV)
* **[longueurs_onde.csv](https://github.com/rayansadoun31-source/groupeC/blob/29de3dae707b782ee209fe97ac537b97f425532c/donnees/longueurs_onde.csv)** : Tableau listant les différentes longueurs d'onde (en µm) de la grille spectrale utilisées comme références pour les modélisations.
* **[table_emissivite_hitran_4_100um_0_100km.csv](https://github.com/rayansadoun31-source/groupeC/blob/29de3dae707b782ee209fe97ac537b97f425532c/donnees/table_emissivite_hitran_4_100um_0_100km.csv)** : Tableau de résultats exhaustif regroupant les émissivités pré-calculées avec la base HITRAN, couvrant une bande spectrale de 4 à 100 µm sur des tranches d'altitude de 0 à 100 km.

### 🖥️ Scripts et Outils
* **[visualiser_rendu_atm.py](https://github.com/rayansadoun31-source/groupeC/blob/29de3dae707b782ee209fe97ac537b97f425532c/donnees/visualiser_rendu_atm.py)** : Script Python dédié au traitement, à l'extraction et à la visualisation graphique des rendus atmosphériques issus des matrices `.npy`.
