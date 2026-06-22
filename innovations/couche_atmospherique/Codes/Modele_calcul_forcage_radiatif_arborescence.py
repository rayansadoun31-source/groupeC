import os
import sys
import numpy as np
from scipy.optimize import least_squares
import scipy.constants as const
import pandas as pd
import tifffile
import xarray as xr
from tqdm import tqdm
import datetime

# =============================================================================
# 0. GESTION DYNAMIQUE DE L'ARBORESCENCE
# =============================================================================
# 2. On calcule les chemins
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_RACINE = os.path.abspath(os.path.join(DOSSIER_SCRIPT, '..', '..', '..'))

# On pointe vers le dossier où se trouve votre code de gaz
DOSSIER_TEMP_CONC = os.path.join(DOSSIER_RACINE, 'innovations', 'temperatures_et_concentrations')

# 3. ON AJOUTE LE DOSSIER À PYTHON
# Cette ligne est magique : elle dit à Python "regarde aussi dans ce dossier quand je te demande d'importer un truc"
sys.path.append(DOSSIER_TEMP_CONC)

# 4. MAINTENANT SEULEMENT on peut importer votre fonction !
# (Python va la trouver car on vient juste de lui donner le chemin juste au-dessus)
from code_H20_CH4_CO2 import get_gases_ppm


# =============================================================================
# 1. PARAMÈTRES ET CONSTANTES GLOBALES
# =============================================================================
S0 = 1361.0      
albedo_surface = 0.3 
sigma = 5.67e-8  

N_couches = 100  

section_efficace_absorption_CO2 = 1e-25
section_efficace_absorption_H2O = 1e-25
section_efficace_absorption_CH4 = 1e-25

# =============================================================================
# 2. PRÉPARATION DE L'ATMOSPHÈRE (100 KM / COORDONNÉES ISOBARES)
# =============================================================================
P0_Pa = 101325.0  
H_scale = 8.5     

P_TOA_Pa = P0_Pa * np.exp(-100.0 / H_scale)

pressions_edges_Pa = np.linspace(P0_Pa, P_TOA_Pa, N_couches + 1)
delta_P = pressions_edges_Pa[0] - pressions_edges_Pa[1] 

P_layers_Pa = (pressions_edges_Pa[:-1] + pressions_edges_Pa[1:]) / 2.0
altitudes_edges_km = -H_scale * np.log(pressions_edges_Pa / P0_Pa)
z_layers_km = (altitudes_edges_km[:-1] + altitudes_edges_km[1:]) / 2.0
dz_layers_m = (altitudes_edges_km[1:] - altitudes_edges_km[:-1]) * 1000.0

print(f"Modèle isobare prêt. Sommet à {altitudes_edges_km[-1]:.1f} km.")
print(f"Chaque couche pèse exactement {delta_P:.1f} Pascals.")

# =============================================================================
# 3. FONCTIONS PHYSIQUES DES GAZ (Uniquement pour les LW) - OPTIMISÉES
# =============================================================================
print("\nPré-chargement des concentrations de gaz...")
profil_gaz = []
for z in z_layers_km:
    profil_gaz.append(get_gases_ppm(z))

def calculer_densite_moleculaire_air(pression, temperature):
    kB = 1.380649e-23  
    return pression / (kB * abs(temperature)) 

def convertir_ppm_en_fraction_molaire(valeur_ppm):
    return valeur_ppm * 1e-6

def calculer_epaisseur_optique_gaz(pression, temperature, fraction_molaire_gaz, epaisseur_couche, section_efficace_absorption_gaz):
    densite_air = calculer_densite_moleculaire_air(pression, temperature)
    densite_gaz = fraction_molaire_gaz * densite_air
    return section_efficace_absorption_gaz * densite_gaz * epaisseur_couche

def calculer_emissivite_une_couche(pression, temperature, epaisseur_couche, idx_couche):
    concentrations = profil_gaz[idx_couche]
    
    frac_CO2 = convertir_ppm_en_fraction_molaire(concentrations["CO2 de mélange (Proportion)"])
    frac_H2O = convertir_ppm_en_fraction_molaire(concentrations["H2O de mélange (Proportion)"])
    frac_CH4 = convertir_ppm_en_fraction_molaire(concentrations["CH4 de mélange (Proportion)"])
    
    tau_CO2 = calculer_epaisseur_optique_gaz(pression, temperature, frac_CO2, epaisseur_couche, section_efficace_absorption_CO2)
    tau_H2O = calculer_epaisseur_optique_gaz(pression, temperature, frac_H2O, epaisseur_couche, section_efficace_absorption_H2O)
    tau_CH4 = calculer_epaisseur_optique_gaz(pression, temperature, frac_CH4, epaisseur_couche, section_efficace_absorption_CH4)
    
    tau_total = tau_CO2 + tau_H2O + tau_CH4
    return 1.0 - np.exp(-tau_total)

def calculer_transmittance(idx_source, idx_dest, eps_array):
    start = min(idx_source, idx_dest) + 1
    end = max(idx_source, idx_dest)
    if start >= end: return 1.0
    trans = 1.0
    for k in range(start, end):
        trans *= (1.0 - eps_array[k])
    return trans

# =============================================================================
# 4. LE MOTEUR DU MODÈLE À N COUCHES (SÉPARATION SW / LW)
# =============================================================================
def bilan_radiatif_N_couches(T):
    bilan = np.zeros(N_couches + 1)
    
    SW_atteignant_le_sol = S0 / 4.0
    F_sol_absorbe_par_surface = SW_atteignant_le_sol * (1.0 - albedo_surface)
    bilan[0] += F_sol_absorbe_par_surface
    
    eps_full = np.zeros(N_couches + 1)
    eps_full[0] = 1.0 
    
    for i in range(1, N_couches + 1):
        idx = i - 1 
        eps_full[i] = calculer_emissivite_une_couche(
            pression=P_layers_Pa[idx],
            temperature=T[i],
            epaisseur_couche=dz_layers_m[idx],
            idx_couche=idx # Correction de l'index
        )
        
    U = np.zeros(N_couches + 1)
    for i in range(N_couches + 1):
        U[i] = eps_full[i] * sigma * T[i]**4
        
    bilan[0] -= U[0]
    for i in range(1, N_couches + 1):
        bilan[i] -= 2.0 * U[i]
        
    for i in range(N_couches + 1):
        for j in range(N_couches + 1):
            if i == j: continue 
            transmittance = calculer_transmittance(i, j, eps_full)
            energie_absorbee = U[i] * transmittance * eps_full[j]
            bilan[j] += energie_absorbee
            
    return bilan

# =============================================================================
# 5. RÉSOLUTION SÉCURISÉE (least_squares) - ACCÉLÉRÉE
# =============================================================================
print(f"\nLancement du solveur pour {N_couches} couches (Jusqu'à 100 km)...")

T_guess = np.linspace(288.15, 193.15, N_couches + 1)

res = least_squares(
    bilan_radiatif_N_couches,
    x0=T_guess,
    bounds=(100.0, 450.0), 
    loss='soft_l1',
    xtol=1e-3, # Relâchement pour la vitesse
    ftol=1e-3, 
    max_nfev=500
)

T_equilibre = res.x

# =============================================================================
# 6. CALCUL DES ÉMISSIVITÉS FINALES ET AFFICHAGE
# =============================================================================
eps_finaux = np.zeros(N_couches + 1)
eps_finaux[0] = 1.0 

for i in range(1, N_couches + 1):
    idx = i - 1
    eps_finaux[i] = calculer_emissivite_une_couche(
        pression=P_layers_Pa[idx],
        temperature=T_equilibre[i],
        epaisseur_couche=dz_layers_m[idx],
        idx_couche=idx
    )

print(f"\n--- RÉSULTATS DU MODÈLE À {N_couches} COUCHES ---")
if res.success:
    print("[SUCCÈS] Équilibre thermodynamique trouvé.")
else:
    print("[ATTENTION] Résultat approché.")

print(f"Surface   : {T_equilibre[0] - 273.15:>6.2f} °C | Émissivité : {eps_finaux[0]:.4f}")

# ====================================
# 7. CHARGEMENT DE VOS DONNÉES RÉELLES (Mis à jour avec l'arborescence)
# ====================================
print("\nChargement des données réelles...")

# 1. Longueurs d'onde
chemin_ondes = os.path.join(DOSSIER_DONNEES, 'longueurs_onde.csv')
longueurs_onde = np.loadtxt(chemin_ondes, skiprows=1) 
d_lambda = np.gradient(longueurs_onde)

# 2. Températures de surface (Coupure à 1 an)
print("Lecture de temperatures_sol_degre_par_degre.csv en cours...")
chemin_temperatures = os.path.join(DOSSIER_DONNEES, 'temperatures_sol_degre_par_degre.csv')
df_T_total = pd.read_csv(chemin_temperatures)

# --- CORRECTION DU GLISSEMENT DES CONTINENTS ---
print("Alignement spatial de la carte des températures...")
# On trie parfaitement par sécurité
df_T_total = df_T_total.sort_values(by=['Jour', 'Latitude', 'Longitude'])

# On détecte automatiquement la vraie taille de votre grille (ex: 365x181x361)
N_jours_csv = df_T_total['Jour'].nunique()
N_lats_csv = df_T_total['Latitude'].nunique()
N_lons_csv = df_T_total['Longitude'].nunique()

# On plie avec la vraie taille (Finis les décalages entre les jours !)
T_brut_3D = df_T_total['T_sol_K'].values.reshape((N_jours_csv, N_lats_csv, N_lons_csv))

# On convertit en objet xarray pour le redimensionnement spatial
lats_csv = np.sort(df_T_total['Latitude'].unique())
lons_csv = np.sort(df_T_total['Longitude'].unique())

da_T = xr.DataArray(
    T_brut_3D,
    coords=[np.arange(N_jours_csv), lats_csv, lons_csv],
    dims=['jour', 'lat', 'lon']
)

# On interpole proprement pour que ça rentre exactement dans notre grille 180x360
lats_cibles = np.linspace(-90, 90, 180)
lons_cibles = np.linspace(-180, 180, 360)

T_surface_reelle_3D = da_T.interp(lat=lats_cibles, lon=lons_cibles).values

# Si l'année fait plus de 365 jours, on coupe à 365
if T_surface_reelle_3D.shape[0] > 365:
    T_surface_reelle_3D = T_surface_reelle_3D[:365, :, :]
    
print(f"Dimensions de la température prêtes et alignées : {T_surface_reelle_3D.shape}")

# 3. Émissivité du sol (TIFF)
print("Lecture de l'émissivité spatiale (TIFF)...")
chemin_emissivite = os.path.join(DOSSIER_DONNEES, 'emissivite_mondiale_365jours.tif')
emissivite_sfc_3D = tifffile.imread(chemin_emissivite)

if emissivite_sfc_3D.shape == (180, 360, 365):
    emissivite_sfc_3D = np.transpose(emissivite_sfc_3D, (2, 0, 1))

# 4. Albédo des couches atmosphériques (CHARGEMENT DIRECT VIA MEMMAP)
print("Chargement direct du fichier d'albédo pré-calculé (.npy)...")
chemin_albedo_pret = os.path.join(DOSSIER_DONNEES, 'albedo_atm_pret_100c_180x360.npy')

albedo_atm_4D = np.memmap(
    chemin_albedo_pret, 
    dtype='float32', 
    mode='r', 
    shape=(365, N_couches, 180, 360)
)

# 5. Émissivité atmosphérique (CONSTANTE TEMPORAIRE)
N_lambda = len(longueurs_onde)
emissivite_atm = np.full((N_couches, N_lambda), 0.05) 

latitudes_vecteur = np.linspace(-90, 90, 180)

# =============================================================================
# 8. EXTRAPOLATION VERS LE MODÈLE GLOBAL 4D
# =============================================================================
if res.success:
    T_surface_1D = T_equilibre[0]
    T_couches_1D = T_equilibre[1:]
    delta_T_profil = T_couches_1D - T_surface_1D
else:
    raise ValueError("Le solveur n'a pas convergé.")

print("Création du tableau 4D de l'atmosphère terrestre en cours...")
T_atm_4D = T_surface_reelle_3D[:, np.newaxis, :, :] + delta_T_profil[np.newaxis, :, np.newaxis, np.newaxis]
print("Terminé ! Le tableau 4D T_atm_4D est prêt.")

# =============================================================================
# 9. PRÉPARATION DES FONCTIONS FINALES (Planck & Soleil)
# =============================================================================
def planck_radiance(lam, T):
    if lam == 0: return np.zeros_like(T)
    terme1 = (2 * const.h * const.c**2) / (lam**5)
    terme2 = np.exp((const.h * const.c) / (lam * const.k * T)) - 1.0
    return terme1 / terme2

def calculer_insolation_TOA(latitudes_deg, jour_annee, S0=1361.0):
    lat_rad = np.radians(latitudes_deg)
    angle_jour = 2.0 * np.pi * (jour_annee - 1) / 365.25
    declinaison = 0.4093 * np.sin(angle_jour - 1.39) 
    
    tan_lat = np.tan(lat_rad)
    tan_dec = np.tan(declinaison)
    
    cos_H = -tan_lat * tan_dec
    cos_H = np.clip(cos_H, -1.0, 1.0)
    H = np.arccos(cos_H)
    
    terme1 = H * np.sin(lat_rad) * np.sin(declinaison)
    terme2 = np.cos(lat_rad) * np.cos(declinaison) * np.sin(H)
    
    insolation = (S0 / np.pi) * (terme1 + terme2)
    return insolation[:, np.newaxis]

# =============================================================================
# CHOIX DU JOUR À SIMULER (AUTOMATISATION)
# =============================================================================
# ⚠️ MODIFIEZ UNIQUEMENT CE NOMBRE (De 1 à 365) :
JOUR_DE_L_ANNEE = 37 

# --- La magie de Python : Conversion automatique en date et nom ---
date_calc = datetime.datetime(2026, 1, 1) + datetime.timedelta(days=JOUR_DE_L_ANNEE - 1)
mois_fr = ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"]
nom_mois = mois_fr[date_calc.month - 1]

DATE_AFFICHEE = f"{date_calc.day} {nom_mois}"
SUFFIXE_FICHIER = f"{date_calc.day}_{nom_mois.upper()}"
jour_cible = JOUR_DE_L_ANNEE - 1 # L'index mathématique (0 à 364)

# =============================================================================
# 10. CALCUL DU BILAN RADIATIF ET DU DLR (FORÇAGE) - JOUR UNIQUE
# =============================================================================
print(f"\nLancement du calcul global (Jour unique : {DATE_AFFICHEE} - Jour {JOUR_DE_L_ANNEE}/365)...")

Bilan_Radiatif_Net_3D = np.zeros((1, 180, 360))
Forcage_Atmospherique_3D = np.zeros((1, 180, 360))

# --- A. SW (Solaire) ---
SW_in = calculer_insolation_TOA(latitudes_vecteur, jour_cible)
SW_descendant = np.repeat(SW_in, 360, axis=1) 

albedo_atm_jour = albedo_atm_4D[jour_cible, :, :, :] 

for c in range(99, -1, -1):
    SW_descendant = SW_descendant * (1.0 - albedo_atm_jour[c, :, :])
    
SW_absorbe_systeme = SW_descendant * (1.0 - albedo_surface)

# --- B. LW (Thermique) ---
LW_sortant_jour = np.zeros((180, 360))
LW_descendant_jour = np.zeros((180, 360))

T_sfc_jour = T_surface_reelle_3D[jour_cible, :, :]
T_atm_jour = T_atm_4D[jour_cible, :, :, :] 
eps_sfc_jour = emissivite_sfc_3D[jour_cible, :, :]

# --- BARRE DE PROGRESSION SPECTRALE ---
for w_idx, lam in enumerate(tqdm(longueurs_onde, desc=f"Spectre ({DATE_AFFICHEE})", position=0, leave=True)):
    
    planck_sfc_2D = planck_radiance(lam, T_sfc_jour)
    planck_atm_3D = planck_radiance(lam, T_atm_jour) 
    
    I_sfc = eps_sfc_jour * planck_sfc_2D
    
    I_descendant = np.zeros((180, 360))
    for c in range(99, -1, -1):
        eps = emissivite_atm[c, w_idx]
        emission_vers_le_bas = eps * planck_atm_3D[c, :, :] 
        I_descendant = I_descendant * (1.0 - eps) + emission_vers_le_bas
        
    I_remontant = I_sfc
    for c in range(100):
        eps = emissivite_atm[c, w_idx]
        emission_vers_le_haut = eps * planck_atm_3D[c, :, :]
        I_remontant = I_remontant * (1.0 - eps) + emission_vers_le_haut
        
    LW_descendant_jour += I_descendant * d_lambda[w_idx] * np.pi
    LW_sortant_jour += I_remontant * d_lambda[w_idx] * np.pi
    
Bilan_Radiatif_Net_3D[0, :, :] = SW_absorbe_systeme - LW_sortant_jour
Forcage_Atmospherique_3D[0, :, :] = LW_descendant_jour

# =============================================================================
# 11. SAUVEGARDE (Mis à jour avec l'arborescence)
# =============================================================================
nom_fichier_bilan = os.path.join(DOSSIER_SCRIPT, f'Bilan_Radiatif_Net_Global_{SUFFIXE_FICHIER}.npy')
nom_fichier_forcage = os.path.join(DOSSIER_SCRIPT, f'Forcage_Atmospherique_{SUFFIXE_FICHIER}.npy')

np.save(nom_fichier_bilan, Bilan_Radiatif_Net_3D)
np.save(nom_fichier_forcage, Forcage_Atmospherique_3D)

print(f"\nCalculs terminés. Fichiers générés avec succès dans le dossier courant :")
print(f"- {nom_fichier_bilan}")
print(f"- {nom_fichier_forcage}")