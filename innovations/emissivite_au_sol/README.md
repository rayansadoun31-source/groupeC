# Modélisation de l'Émissivité au Sol 

Ce sous-répertoire contient le script nécessaire pour générer une climatologie mondiale de l'émissivité de surface en s'appuyant sur l'imagerie satellitaire et le calcul cloud.

### Script d'Extraction et de Calcul
* **[code_emissivite_sol.py](https://github.com/rayansadoun31-source/groupeC/blob/5ed8d50fa2529dfe34c8ab9ae9ee62d145219cd7/innovations/emissivite_au_sol/code_emissivite_sol.py)** : Script Python exploitant l'API Google Earth Engine pour extraire les données satellitaires MODIS (bande d'émissivité 31). Il calibre les images, calcule une moyenne journalière sur une période de 5 ans (2020-2024) et exporte une cartographie mondiale consolidée sur 365 jours.
