import numpy as np
import xarray as xr
from scipy.interpolate import interp1d
from tqdm import tqdm
import os

# =============================================================================
# PARAMÈTRES DE LA GRILLE CIBLE
# =============================================================================
N_couches_cible = 100
N_lat_cible = 180
N_lon_cible = 360

chemin_entree = r"C:\Projet_Climat\albedo_atm.nc"
chemin_sortie = r"C:\Projet_Climat\albedo_atm_pret_100c_180x360.npy"

print("=== SCRIPT DE PRÉTRAITEMENT DE L'ALBÉDO (VERSION ULTRA-BASSE RAM) ===")

# 1. Ouverture du fichier NetCDF (sans charger les données en mémoire grâce à xarray)
print(f"\n[1/4] Ouverture du fichier NetCDF : {chemin_entree}")
dataset = xr.open_dataset(chemin_entree)
variable_albedo = 'albedo_0'

# Détection dynamique du nombre de jours (gère 365 ou 366 jours)
N_jours = dataset.dims['dayofyear']
N_couches_origine = dataset.dims['pressure_level']
print(f"Détection : {N_jours} jours et {N_couches_origine} couches d'origine dans le fichier.")

# 2. Création du fichier de sortie directement sur le disque dur (Memory Map)
print(f"[2/4] Initialisation du fichier de sortie sur le disque (dtype=float32)...")
if os.path.exists(chemin_sortie):
    os.remove(chemin_sortie) # On efface l'ancien s'il existe

# On crée une matrice "virtuelle" sur le disque dur
albedo_final_disk = np.memmap(
    chemin_sortie, 
    dtype='float32', 
    mode='w+', 
    shape=(N_jours, N_couches_cible, N_lat_cible, N_lon_cible)
)

# 3. Définition des axes pour l'interpolation
lat_min, lat_max = dataset.latitude.min().item(), dataset.latitude.max().item()
lon_min, lon_max = dataset.longitude.min().item(), dataset.longitude.max().item()

lats_cibles = np.linspace(lat_min, lat_max, N_lat_cible)
lons_cibles = np.linspace(lon_min, lon_max, N_lon_cible)

axe_original = np.linspace(0, 1, N_couches_origine)
axe_cible = np.linspace(0, 1, N_couches_cible)

# 4. Boucle de traitement jour par jour (Consommation RAM proche de 0)
print(f"[3/4] Lancement de l'interpolation double (spatiale + verticale)...")

for j in tqdm(range(N_jours), desc="Prétraitement de l'albédo"):
    # Extraction d'un seul jour précis (3D : couches, lat, lon)
    albedo_jour_nc = dataset[variable_albedo].isel(dayofyear=j)
    
    # Interpolation horizontale pour ce jour uniquement
    albedo_jour_horiz = albedo_jour_nc.interp(
        latitude=lats_cibles, 
        longitude=lons_cibles,
        kwargs={"fill_value": "extrapolate"}
    )
    
    # Conversion en tableau numpy brut (shape: 16, 180, 360)
    matrice_3D_brute = albedo_jour_horiz.transpose('pressure_level', 'latitude', 'longitude').values
    
    # Interpolation verticale pour ce jour uniquement
    fonction_interp_verticale = interp1d(axe_original, matrice_3D_brute, axis=0, kind='linear', fill_value='extrapolate')
    matrice_3D_etiree = fonction_interp_verticale(axe_cible)
    
    # Sécurité physique et conversion en float32 pour économiser 50% d'espace
    matrice_3D_etiree = np.clip(matrice_3D_etiree, 0.0, 1.0).astype('float32')
    
    # Écriture immédiate du jour traité sur le disque dur
    albedo_final_disk[j, :, :, :] = matrice_3D_etiree

# 5. Fermeture et finalisation
print("\n[4/4] Écriture finale et fermeture du fichier...")
del albedo_final_disk # Force Python à fermer proprement le fichier sur le disque

print("\n=== PRÉTRAITEMENT TERMINÉ AVEC SUCCÈS ===")
print(f"Fichier compressé généré : {chemin_sortie}")