# Codes
Ce dossier regroupe les différnets codes modélisant les couches atmosphériques.

## Scripts 

### 1. [Modèle à 1 couche (`atmosphere_1_couche_tropausphere_8km.py`)](./atmosphere_1_couche_tropausphere_8km.py)
Simulation numérique de l'équilibre radiatif et du bilan thermique de la Terre à l'aide d'un modèle d'atmosphère simplifié à une seule couche.

### 2. [Modèle à 2 couches (`atmosphere_2_couche_tropausphere_8km.py`)](./atmosphere_2_couche_tropausphere_8km.py)
Résolution du bilan énergétique terrestre via un découpage de l'atmosphère en deux couches de masses égales intégrant la loi de Beer-Lambert pour le $CO_2$.

### 3. [Modèle à N couches (`atmosphere_n_couches_1013hpa_a_0hpa.py`)](./atmosphere_n_couches_1013hpa_a_0hpa.py)
Généralisation algorithmique du modèle radiatif à un nombre arbitraire ($N$) de couches atmosphériques avec calcul des interactions d'absorption et de transmittance.

### 4. [Modèle de calcul pour le forçage radiatif (`Modele_calcul_forcage_radiatif.py`)](./Modele_calcul_forcage_radiatif.py)
Code simulant un modèle de bilan radiatif de l'atmosphère terrestre en 1D (à 100 couches) extrapolé à l'échelle globale en 4D, afin de calculer l'équilibre thermique de la Terre, le flux d'énergie net et le forçage atmosphérique (rayonnement descendant) pour un jour spécifique de l'année.

### 5. [Modèle de calcul de forçage radiatif arborescence (`Modele_calcul_forcage_radiatif_arborescence.py`)](./Modele_calcul_forcage_radiatif_arborescence.py)
Code reprenant le même modèle de bilan radiatif global en 4D, mais intègre une gestion dynamique des chemins système afin de charger automatiquement les données et les concentrations de gaz depuis une arborescence de dossiers spécifique.

### 6. [Créer un fichier albédo de bonne taille (`creer_fichier_albedo_bonne_taille.py`)](./creer_fichier_albedo_bonne_taille.py)
Code effectuant un prétraitement optimisé en mémoire (RAM) d'un fichier NetCDF pour interpoler spatialement et verticalement les données d'albédo atmosphérique, avant de les sauvegarder jour par jour dans un fichier binaire .npy directement sur le disque dur.
