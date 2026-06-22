import cdsapi
import xarray as xr
import numpy as np
import os
from tqdm import tqdm

# Configuration de votre badge d'accès Copernicus
URL = "https://cds.climate.copernicus.eu/api" 
CLE = "9f3dc3ba-3907-473a-b5bf-844926afbcd9" 

# Initialisation du client authentifié
c = cdsapi.Client(url=URL, key=CLE)

# =============================================================================
# 0. FONCTION OUTIL : CALCUL DE L'ALBEDO VECTORISÉ
# =============================================================================
def calculer_albedo_dynamique(tau_nuages_0, T_surf, delta_P):
    """
    Calcule l'albédo d'une couche atmosphérique (ondes courtes / SW) 
    en utilisant la rétroaction nuageuse et l'approximation d'Eddington à deux flux.
    """
    T_ref = 288.15           
    k_nuage = 0.1            
    P0 = 1013.25             
    tau_rayleigh_tot = 0.1   
    tau_aerosols = 0.0       
    
    tau_nuages_actuel = tau_nuages_0 + k_nuage * (T_surf - T_ref)
    
    if isinstance(tau_nuages_actuel, (xr.DataArray, np.ndarray)):
        tau_nuages_actuel = np.maximum(0.0, tau_nuages_actuel)
    else:
        tau_nuages_actuel = max(0.0, tau_nuages_actuel)
    
    tau_rayleigh_couche = tau_rayleigh_tot * (delta_P / P0)
    tau_SW = tau_rayleigh_couche + tau_aerosols + tau_nuages_actuel
    
    return tau_SW / (2.0 + tau_SW)

# =============================================================================
# 1. TÉLÉCHARGEMENT DÉCOUPÉ (Mois par Mois pour le nouveau serveur Copernicus)
# =============================================================================
annees = ['2018', '2019', '2020', '2021', '2022']
mois_liste = [f"{m:02d}" for m in range(1, 13)] # ['01', '02', ..., '12']

fichiers_mensuels = [] # On va stocker ici les noms de nos 60 petits fichiers

print("Début du téléchargement découpé (Mois par Mois)...")

for annee in annees:
    for mois in mois_liste:
        fichier_mois = f'era5_brut_{annee}_{mois}.nc'
        fichiers_mensuels.append(fichier_mois)
        
        # Si on a déjà téléchargé ce mois, on passe au suivant instantanément
        if not os.path.exists(fichier_mois):
            print(f"\n--- Téléchargement : {mois}/{annee} ---")
            c.retrieve(
                'reanalysis-era5-pressure-levels',
                {
                    'variable': 'specific_cloud_liquid_water_content',
                    'pressure_level': [
                        '1', '10', '50', '100', '200', '250', '300', '400', 
                        '500', '600', '700', '800', '850', '900', '950', '1000'
                    ],
                    'product_type': 'reanalysis',
                    'year': [annee], # <--- Une seule année
                    'month': [mois], # <--- Un seul mois ! (Garantit de ne jamais avoir l'erreur 403)
                    'day': [f"{d:02d}" for d in range(1, 32)],   
                    'time': '12:00',
                    'grid': ['2.0', '2.0'], 
                    'format': 'netcdf',
                },
                fichier_mois)
        else:
            print(f"[{mois}/{annee}] Déjà sur le disque, on passe.")

# =============================================================================
# 2. CALCUL MATRICIEL ET GROUPEMENT PAR JOUR AVEC BARRE DE PROGRESSION
# =============================================================================
fichier_final = 'forçage_tau_nuages_365_jours.nc'

print("\nFusion virtuelle des 60 fichiers mensuels en mémoire...")
# open_mfdataset rassemble tous nos petits fichiers comme un grand puzzle
ds = xr.open_mfdataset(fichiers_mensuels, combine='by_coords')

# Constantes physiques
g = 9.81
r_eff = 10e-6
rho_eau = 1000.0
delta_P_hPa = 50.0  
delta_P_pascals = delta_P_hPa * 100.0 

# Listes temporaires pour stocker les résultats de chaque couche
liste_tau_couches = []
liste_albedo_couches = []

print("Calcul des climatologies et des albédos en cours...")

# LA BARRE DE CHARGEMENT
for niveau in tqdm(ds['level'].values, desc="Progression par couche d'altitude"):
    
    # 1. On isole la couche d'altitude actuelle
    ds_couche = ds.sel(level=niveau)
    
    # 2. Calcul de la moyenne sur les 5 ans pour cette couche spécifique
    ds_clim_couche = ds_couche.groupby('time.dayofyear').mean('time')
    q_l_couche = ds_clim_couche['clwc']
    
    # 3. Traitement physique de l'eau liquide (Stephens)
    lwp_couche = q_l_couche * (delta_P_pascals / g)
    tau_couche = (3.0 * lwp_couche) / (2.0 * rho_eau * r_eff)
    
    # 4. Calcul de l'albédo de référence (Eddington)
    albedo_couche = calculer_albedo_dynamique(tau_couche, T_surf=288.15, delta_P=delta_P_hPa)
    
    # 5. On force Python à calculer et libérer la mémoire pour ne pas planter
    tau_couche = tau_couche.compute()
    albedo_couche = albedo_couche.compute()
    
    # Stockage temporaire
    liste_tau_couches.append(tau_couche)
    liste_albedo_couches.append(albedo_couche)

print("Fusion des couches d'altitude calculées...")
# Recombinaison de toutes les couches individuelles en matrices 4D complètes
tau_matrice_4D = xr.concat(liste_tau_couches, dim='level')
albedo_matrice_4D = xr.concat(liste_albedo_couches, dim='level')

# Attribution des métadonnées
tau_matrice_4D.name = "tau_0"
tau_matrice_4D.attrs['long_name'] = "Climatologie de l'epaisseur optique (Tau 0)"

albedo_matrice_4D.name = "albedo_0"
albedo_matrice_4D.attrs['long_name'] = "Climatologie de l'albedo de reference a T_surf = T_ref"

# =============================================================================
# 3. SAUVEGARDE DES DEUX MATRICES DANS LE FICHIER DE FORÇAGE
# =============================================================================
print("Création et sauvegarde du fichier de forçage final...")
ds_final = xr.Dataset({
    'tau_0': tau_matrice_4D,
    'albedo_0': albedo_matrice_4D
})

ds_final.to_netcdf(fichier_final)
ds.close()
print(f"\n[SUCCÈS] Fichier de forçage planétaire annuel créé : {fichier_final}")