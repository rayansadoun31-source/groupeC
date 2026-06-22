# Codes
Ce dossier regroupe les différnets codes modélisant les couches atmosphériques.

## Scripts 

### 1. [Modèle à 1 couche (`atmosphere_1_couche_troposphere_8km.py`)](./atmosphere_1_couche_troposphere_8km.py)
Simulation numérique de l'équilibre radiatif et du bilan thermique de la Terre à l'aide d'un modèle d'atmosphère simplifié à une seule couche.

### 2. [Modèle à 2 couches (`atmosphere_2_couche_troposphere_8km.py`)](./atmosphere_2_couche_troposphere_8km.py)
Résolution du bilan énergétique terrestre via un découpage de l'atmosphère en deux couches de masses égales intégrant la loi de Beer-Lambert pour le $CO_2$.

### 3. [Modèle à N couches (`atmosphere_n_couches_1013hpa_a_0hpa.py`)](./atmosphere_n_couches_1013hpa_a_0hpa.py)
Généralisation algorithmique du modèle radiatif à un nombre arbitraire ($N$) de couches atmosphériques avec calcul des interactions d'absorption et de transmittance.

### 4. [Modèle de calcul pour le forçage radiatif (`Modele_forcage_radiatif_final.py`)](./Modele_forcage_radiatif_final.py)
Code simulant un modèle de bilan radiatif de l'atmosphère terrestre en 1D (à 100 couches), afin de calculer l'équilibre thermique de la Terre, le flux d'énergie net et le forçage atmosphérique (rayonnement descendant) pour un jour spécifique de l'année. 

> **⚠️ ATTENTION** Le fichier qui suit est le code final de la modélisation de l'effet de l'atmosphère. Pour pouvoir le lancer correctement, il faut s'assurer d'avoir la même arborescence que le github et s'assurer d'avoir récupérer les deux fichiers trop volumineux (cf dossier donnees)

### 5. [Planisphère du forçage radiatif (`visualiser_rendu_atm.py`)](./visualiser_rendu_atm.py)
Code qui permet de voir un planisphère avec la valeur du forçage radiatif sur toute la Terre. Prend un fichier du type **Forcage_Atmospherique_6_AOUT.npy**, où seul la date change. Ces fichiers sont générer par **Modele_forcage_radiatif_final.py**

### 6. [Bibliothèque à télécharger (`requirements.txt`)](./requirements.txt)
Pour voir l'ensemble des bibliothèques python à télécharger nécessaire pour executé le code **Modele_forcage_radiatif_final.py**. Il faut s'assurer d'avoir la version python: Python 3.12.10
