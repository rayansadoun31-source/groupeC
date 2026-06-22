# Modèle d'Émissivité Haute Précision (HITRAN)

Ce dossier regroupe les scripts d'acquisition, de calcul et d'intégration basés sur la base de données spectroscopique internationale HITRAN. Ce modèle permet de simuler l'émissivité atmosphérique avec une précision moléculaire haute résolution.

---

## Index des Documents et Livrables

* **[`references_hitran.bib`](references_hitran.bib)** | *Contenu :* Fichier de bibliographie BibTeX contenant les références d'articles scientifiques officiels pour la base de données HITRAN et l'interface Python HAPI.

### Documentation 
* **[`documentation_1_section_efficace_CO2.pdf`](documentation_1_section_efficace_CO2.pdf)** | *Contenu :* présente le script Python [`1_section_efficace_CO2_15um.py`](1_section_efficace_CO2_15um.py) qui utilise la bibliothèque HAPI et la base spectroscopique HITRAN pour calculer et tracer la section efficace d'absorption du CO2​ autour de 15 μm.
*  **[`documentation_2_sections_efficaces_gaz_hitran.pdf`](documentation_2_sections_efficaces_gaz_hitran.pdf)** | *Contenu :* Ce projet contient un script Python réutilisable [`2_sections_efficaces_gaz_hitran.py`](2_sections_efficaces_gaz_hitran.py) permettant de calculer et de comparer les sections efficaces d'absorption de quatre gaz à effet de serre majeurs (H2​O, CO2, O3​ et CH4​) dans le domaine de l'infrarouge thermique ($4$ aˋ $100$ μm) à partir de la base HITRAN.
* 
### Scripts d'Acquisition et Calcul Spectral
* **[`1_section_efficace_CO2_15um.py`](1_section_efficace_CO2_15um.py)** | *Application :* Script Python téléchargeant les données de la base HITRAN et calculant la section efficace d'absorption réelle du CO2 autour de sa bande principale à 15 µm.

* **[`2_sections_efficaces_gaz_hitran.py`](2_sections_efficaces_gaz_hitran.py)** | *Application :* Script Python téléchargeant les raies spectrales depuis HITRAN et traçant les graphiques des sections efficaces d'absorption réelles de quatre gaz (CO2, CH4, O3 et H2O) sur une large plage infrarouge.

### Intégration et Modélisation de l'Émissivité
* **[`code_final_emissivite_avec_sections_hitran.py`](code_final_emissivite_avec_sections_hitran.py)** | *Application :* Script d'intégration calculant l'émissivité finale d'une couche atmosphérique en combinant les profils verticaux de concentration avec les sections efficaces d'absorption réelles importées.

### Génération et Stockage des Données
* **[`generer_table_emissivite_hitran.py`](generer_table_emissivite_hitran.py)** | *Application :* Script final calculant et exportant une table complète d'émissivités spectrales de l'atmosphère, couplant les profils d'altitude avec les sections efficaces haute précision.

* **[`table_emissivite_hitran_4_100um_0_100km.csv`](table_emissivite_hitran_4_100um_0_100km.csv)** | *Contenu :* Tableau de données final recensant les émissivités spectrales haute précision calculées pour des altitudes de 0 à 100 km et des longueurs d'onde de 4 à 100 µm.

* **[`donnees_hitran/`](donnees_hitran)** | *Contenu :* Dossier de cache local contenant les bases de données textuelles brutes (`.data`) regroupant les millions de raies spectrales individuelles téléchargées par HAPI, ainsi que leurs fichiers de configuration JSON (`.header`) associés.

---

## Remarques sur l'Exécution
Les scripts tirent parti de l'interface HAPI (HITRAN Application Programming Interface). Le dossier `donnees_hitran` sert de mémoire tampon locale pour éviter de retélécharger les millions de raies de paramètres quantiques des gaz (CH4, CO2, O3 et H2O) à chaque exécution.

Installation préalable des imports externes :

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Le paquet `hitran-api` s'importe dans les scripts sous le nom `hapi`. Le modèle dépend aussi du fichier `../../temperatures_et_concentrations/code_H20_CH4_CO2_O3.py`. La liste exhaustive des imports, la documentation des fonctions et les commandes d'exécution figurent dans les cinq documentations LaTeX autonomes listées ci-dessus.
