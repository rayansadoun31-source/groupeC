# Modélisation de l'Albédo Atmosphérique

Ce dossier rassemble les scripts d'acquisition de données, les modèles physiques et les outils de visualisation permettant de calculer et de cartographier dynamiquement l'albédo des nuages à l'échelle mondiale.

---

## Index des Documents et Livrables

### Documentation Technique et Scientifique
* **[`albédo.pdf`](albédo.pdf)** | *Contenu :* Rapport d'étude officiel du groupe de projet décrivant la méthodologie physique, les équations fondamentales (Liquid Water Path - LWP, approximation d'Eddington) et l'exploitation des réanalyses ERA5 pour modéliser dynamiquement l'albédo atmosphérique.

### Scripts de Calcul et d'Acquisition
* **[`albedo_calcul.py`](albedo_calcul.py)** | *Application :* Script Python de traitement climatique qui télécharge les données d'humidité et d'eau liquide depuis le serveur Copernicus (via l'API CDS), calcule vectoriellement l'épaisseur optique ainsi que l'albédo dynamique des nuages (approximation d'Eddington) et génère les matrices 4D d'albédo.

### Outils de Visualisation
* **[`trace_albedo.py`](trace_albedo.py)** | *Application :* Script Python de visualisation cartographique qui charge les résultats de l'albédo atmosphérique (à partir du fichier NetCDF `alb.nc`) pour cartographier à l'échelle mondiale la réflectivité d'une couche nuageuse spécifique à un jour précis de l'année.

---

## Flux de Travail
1. Le script `albedo_calcul.py` s'interface avec Copernicus pour récupérer les données météorologiques réelles et produit les fichiers de résultats au format standardisé NetCDF.
2. Le script `trace_albedo.py` permet ensuite d'exploiter visuellement ces résultats sous forme de cartes géospatiales.
