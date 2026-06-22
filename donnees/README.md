### Matrices de Forçage Atmosphérique et Modèles (Fichiers NumPy)
Ces fichiers stockent les données vectorielles et les calculs de forçage atmosphérique évalués sur différents mois représentatifs de l'année, ainsi que les matrices globales.

* **[Forcage_Atmospherique_6_FEVRIER.npy](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/Forcage_Atmospherique_6_FEVRIER.npy)** : Matrice de données contenant les valeurs de forçage atmosphérique modélisées pour l'hiver.
* **[Forcage_Atmospherique_6_MAI.npy](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/Forcage_Atmospherique_6_MAI.npy)** : Matrice de données contenant les valeurs de forçage atmosphérique modélisées pour le printemps.
* **[Forcage_Atmospherique_6_AOUT.npy](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/Forcage_Atmospherique_6_AOUT.npy)** : Matrice de données contenant les valeurs de forçage atmosphérique modélisées pour l'été.
* **[Forcage_Atmospherique_6_NOVEMBRE.npy](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/Forcage_Atmospherique_6_NOVEMBRE.npy)** : Matrice de données contenant les valeurs de forçage atmosphérique modélisées pour l'automne.

> **⚠️ ATTENTION** pour le fichier qui suit, le fichier dans le github est vide. Il faut récupérer ce fichier via la plateforme de tranfert de fichier de gros volume de Centrale Lyon.
* **[albedo_atm_pret_100c_180x360.npy](https://github.com/rayansadoun31-source/groupeC/blob/8acc1f6a3790d7774b216590130f2ca88d34796b/donnees/albedo_atm_pret_100c_180x360.npy)** : Matrice pré-calculée stockant la cartographie globale de l'albédo atmosphérique avec une résolution spatiale de 180x360.

### Cartographie Globale
* **[emissivite_mondiale_365jours.tif](https://github.com/rayansadoun31-source/groupeC/blob/aaed69dab74f0fb55a43cb3cb4ec3c708dbccf4e/donnees/emissivite_mondiale_365jours.tif)** : Fichier d'image géospatiale (TIFF) représentant la carte globale de l'émissivité terrestre simulée et consolidée sur une année complète de 365 jours.

### Tables de Données et Spectres (Fichiers CSV)
* **[longueurs_onde.csv](https://github.com/rayansadoun31-source/groupeC/blob/29de3dae707b782ee209fe97ac537b97f425532c/donnees/longueurs_onde.csv)** : Tableau listant les différentes longueurs d'onde (en µm) de la grille spectrale utilisées comme références pour les modélisations.
> **⚠️ ATTENTION** pour le fichier qui suit, le fichier dans le github est vide. Il faut récupérer ce fichier via la plateforme de tranfert de fichier de gros volume de Centrale Lyon.
* **[table_emissivite_hitran_4_100um_0_100km.csv](https://github.com/rayansadoun31-source/groupeC/blob/29de3dae707b782ee209fe97ac537b97f425532c/donnees/table_emissivite_hitran_4_100um_0_100km.csv)** : Tableau de résultats exhaustif regroupant les émissivités pré-calculées avec la base HITRAN, couvrant une bande spectrale de 4 à 100 µm sur des tranches d'altitude de 0 à 100 km.
* **[temperatures_sol_degre_par_degre.csv](https://github.com/rayansadoun31-source/groupeC/blob/8acc1f6a3790d7774b216590130f2ca88d34796b/donnees/temperatures_sol_degre_par_degre.csv)** : Tableau recensant les températures de surface de la Terre avec un maillage spatial d'une précision de un degré par un degré.

### Scripts et Outils
* **[visualiser_rendu_atm.py](https://github.com/rayansadoun31-source/groupeC/blob/29de3dae707b782ee209fe97ac537b97f425532c/donnees/visualiser_rendu_atm.py)** : Script Python dédié au traitement, à l'extraction et à la visualisation graphique des rendus atmosphériques issus des matrices `.npy`.
