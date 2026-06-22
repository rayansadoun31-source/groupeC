# Modèle de Température du Sol Principal (modele_Tsol_principal)

Ce dossier central constitue le cœur de l'étude thermique au sol. Il regroupe les deux approches complémentaires développées pour modéliser, simuler et valider l'évolution des températures de surface et les flux d'énergie terrestres.

---

## Structure du Dossier

### 1. [Modèle 4 : Simulation Thermique Globale et Cartographie Interactive](./modele_4/)
Ce sous-dossier abrite le volet algorithmique et numérique le plus avancé pour la simulation des températures au sol.
* **Résumé du contenu :** Il rassemble les moteurs de calcul physique (flux d'énergie, rayonnement solaire, conduction, évaporation) couplés à des bases de données géographiques et météorologiques réelles. Ce modèle permet de générer des projections thermiques temporelles (évolutions heure par heure) ainsi que des visualisations cartographiques globales interactives sous forme de planisphères et de sphères 3D, en basse ou haute résolution.

### 2. [Convection et Conduction : Étude des Transferts Thermiques](./convection_et_conduction/)
Ce sous-dossier pose les fondements théoriques, physiques et mathématiques indispensables à la validation des modèles numériques du projet.
* **Résumé du contenu :** Il regroupe l'ensemble des rapports scientifiques, des démonstrations rigoureuses et des analyses quantitatives du groupe. Ces travaux visent à déterminer précisément la puissance surfacique liée aux phénomènes de convection et à apporter les preuves physiques justifiant le caractère négligeable de la conduction radiale et orthoradiale dans les modélisations globales.

---

## Démarche d'Utilisation
* Pour explorer les **fondements théoriques, physiques et les rapports de validation**, veuillez consulter le dossier `convection_et_conduction`.
* Pour exécuter les **simulations numériques, visualiser les courbes temporelles ou lancer les interfaces cartographiques mondiales**, veuillez vous diriger vers le dossier `modele_4`.
