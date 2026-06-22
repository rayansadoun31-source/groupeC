# generer_donnees_sol.py
# ==============================================================================
# POST-TRAITEMENT : EXPORTATION DES TEMPÉRATURES DE SURFACE 1°x1°
# ==============================================================================

import numpy as np
import pandas as pd
import pathlib
import os
from scipy.interpolate import RegularGridInterpolator
from tqdm import tqdm

# Sécurisation du répertoire de travail
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("--- Initialisation de l'exportation des données ---")

# 1. Définition des chemins
# On cible le fichier stabilisé de la HAUTE résolution (le plus précis)
FICHIER_SOURCE = pathlib.Path("ressources/npy/grid_hires_stabilized.npy")
FICHIER_SORTIE = pathlib.Path("temperatures_sol_degre_par_degre.csv")

if not FICHIER_SOURCE.exists():
    print(f"ERREUR FATALE : Le fichier {FICHIER_SOURCE} est introuvable.")
    print("Veuillez d'abord faire tourner 'modele_planisphere_haute_res.py' avec l'option 2 (stabilisée).")
    exit()

# 2. Chargement des données
print("Chargement de la matrice thermique...")
T_grid = np.load(FICHIER_SOURCE)
N_steps, nlat_or, nlon_or = T_grid.shape

# 3. Paramètres temporels (On suppose un pas de temps de 3600s, soit 24 steps/jour)
STEPS_PER_DAY = 24
N_DAYS = N_steps // STEPS_PER_DAY
print(f"Détection de {N_DAYS} jours de simulation.")

# Définition des grilles d'origine (Grille Haute Résolution 70x140)
# Attention: Ajustez ces valeurs si votre script source utilise d'autres bornes exactes
lat_or = np.linspace(-90, 90, nlat_or)
lon_or = np.linspace(-180, 180, nlon_or)

# 4. Création de la grille cible (Degré par degré : 181x361)
lat_cible = np.linspace(-90, 90, 181)
lon_cible = np.linspace(-180, 180, 361)
grille_points_cible = np.array(np.meshgrid(lat_cible, lon_cible, indexing="ij"))
points_aplatis = np.moveaxis(grille_points_cible, 0, -1)

lat_flat = grille_points_cible[0].flatten()
lon_flat = grille_points_cible[1].flatten()

liste_dataframes_jours = []

# 5. Boucle de calcul des moyennes journalières et interpolation
print("Calcul des moyennes et interpolation spatiale (1°x1°)...")
for jour in tqdm(range(N_DAYS), desc="Traitement des jours"):
    start_idx = jour * STEPS_PER_DAY
    end_idx = start_idx + STEPS_PER_DAY
    
    # Extraction des 24 heures du jour et calcul de la moyenne (axe 0)
    bloc_jour = T_grid[start_idx:end_idx, :, :]
    moyenne_jour_grille_origine = np.mean(bloc_jour, axis=0)
    
    # Interpolation mathématique sur la nouvelle grille 1°x1°
    interp_fonction = RegularGridInterpolator((lat_or, lon_or), moyenne_jour_grille_origine, bounds_error=False, fill_value=None)
    grille_1deg = interp_fonction(points_aplatis)
    t_flat = grille_1deg.flatten()
    
    # Création ultra-rapide du tableau pour ce jour
    df_jour = pd.DataFrame({
        'Jour': jour + 1,
        'Latitude': lat_flat.round(1),
        'Longitude': lon_flat.round(1),
        'T_sol_K': t_flat.round(2)
    })
    liste_dataframes_jours.append(df_jour)

# 6. Assemblage final et sauvegarde CSV
print("\nAssemblage du fichier global...")
df_final = pd.concat(liste_dataframes_jours, ignore_index=True)

print(f"Sauvegarde en cours dans {FICHIER_SORTIE.name} (Cela peut prendre quelques secondes)...")
df_final.to_csv(FICHIER_SORTIE, index=False)

print(f"Succès ! Le fichier est prêt à être utilisé par le modèle d'atmosphère.")