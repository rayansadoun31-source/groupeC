# Émissivité Atmosphérique

Ce dossier central regroupe l'ensemble des travaux, scripts et modélisations numériques dédiés à l'étude de l'épaisseur optique et de l'émissivité de l'atmosphère terrestre en fonction des gaz à effet de serre.

L'étude est structurée en trois grands volets (sous-dossiers) reflétant la progression et la validation de nos modèles.

---

## Structure du Dossier

### 1. [modèle1_empirique_emissivité](./modèle1_empirique_emissivité/)
Ce sous-dossier contient la première approche de modélisation. Les calculs y sont basés sur des approximations empiriques des spectres d'absorption.
* **Contenu clé :** Évolution des scripts Python (codes 1 à 4) intégrant progressivement les altitudes et les concentrations verticales réelles de $CO_2$, $CH_4$, $H_2O$ et $O_3$, ainsi que l'exportation d'une première table de données spectrale au format CSV.

### 2. [modèle2_hitran_emissivité](./modèle2_hitran_emissivité/)
Ce sous-dossier représente l'évolution haute résolution du modèle, s'appuyant sur les données quantiques officielles de la base internationale HITRAN via l'interface HAPI.
* **Contenu clé :** Scripts de téléchargement des raies spectrales en cache local (`donnees_hitran/`), calcul de la section efficace haute précision (notamment autour de la bande critique des 15 µm du $CO_2$) et génération d'une table d'émissivité de référence (altitudes de 0 à 100 km).

### 3. [comparaison_modeles_sections_efficaces](./comparaison_modeles_sections_efficaces/)
Ce sous-dossier est l'espace de validation scientifique du projet. Il permet de confronter directement les deux approches précédentes.
* **Contenu clé :** Script de diagnostic et graphiques de comparaison visuelle (`.png`) gaz par gaz ($CO_2$, $CH_4$, $H_2O$, $O_3$). Il met en évidence l'apport et la finesse des raies d'absorption obtenues avec HITRAN par rapport au modèle empirique.

---

## Logique de Lecture et Démarche Scientifique

Pour comprendre ou reprendre les travaux de ce dossier, il est recommandé de suivre cet ordre :
1. Consulter le **Modèle Empirique** pour assimiler les bases de la discrétisation de l'atmosphère en couches.
2. Étudier le **Modèle HITRAN** pour observer l'intégration des bases de données spectroscopiques haute résolution.
3. Analyser le dossier de **Comparaison** pour valider la fidélité mathématique et physique de nos simulations.
