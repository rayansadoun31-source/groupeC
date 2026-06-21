import numpy as np
from scipy.optimize import fsolve

# =============================================================================
# 1. PARAMÈTRES, CONSTANTES ET DONNÉES CLIMATIQUES
# =============================================================================
S0 = 1361.0      # Constante solaire en W/m^2 [Source: GIEC AR6]
albedo = 0.3     # Albédo moyen terrestre [Source: GIEC AR6]
sigma = 5.67e-8  # Constante de Stefan-Boltzmann [Source: CODATA 2018]
P0 = 1013.25     # Pression atmosphérique de surface en hPa [Source: US Standard Atmosphere]

# Données liées aux gaz à effet de serre
C_CO2 = 415.0    # Concentration en CO2 en ppm [Source: NOAA, données récentes]
k_CO2 = 0.0035   # Constante d'absorption effective (ppm^-1) calibrée pour le modèle

# =============================================================================
# 2. DÉCOUPAGE DE L'ATMOSPHÈRE EN TRANCHES DE PRESSION (MASSE)
# =============================================================================
# Nous créons 2 couches de masse égale.
delta_P1 = P0 / 2.0  # Couche basse (1013.25 -> 506.6 hPa)
delta_P2 = P0 / 2.0  # Couche haute (506.6 -> 0 hPa)

# Calcul des émissivités via la loi de Beer-Lambert
# epsilon = 1 - exp(-k * C * fraction_de_masse)
eps1 = 1.0 - np.exp(-k_CO2 * C_CO2 * (delta_P1 / P0))
eps2 = 1.0 - np.exp(-k_CO2 * C_CO2 * (delta_P2 / P0))

# =============================================================================
# 3. DÉFINITION DU SYSTÈME D'ÉQUATIONS À 2 COUCHES
# =============================================================================
def bilan_radiatif_2_couches(T):
    # T0: Surface, T1: Couche Basse, T2: Couche Haute
    T0, T1, T2 = T 
    
    # Flux solaire absorbé par la surface
    F_sol = (S0 / 4.0) * (1.0 - albedo)
    
    # Raccourcis pour les lois de Stefan-Boltzmann (flux émis par chaque corps noir)
    U0 = sigma * T0**4
    U1 = sigma * T1**4
    U2 = sigma * T2**4
    
    # Équation 1 : Bilan de la surface
    # Entrant : Solaire + Infrarouge émis par C1 + Infrarouge émis par C2 (transmis par C1)
    # Sortant : Infrarouge émis par la surface
    bilan_surf = F_sol + (eps1 * U1) + (eps2 * U2 * (1.0 - eps1)) - U0
    
    # Équation 2 : Bilan de la Couche 1 (basse)
    # Entrant : Infrarouge surface absorbé par C1 + Infrarouge C2 absorbé par C1
    # Sortant : Infrarouge émis vers le haut ET vers le bas (2 * eps1 * U1)
    bilan_c1 = (eps1 * U0) + (eps1 * eps2 * U2) - (2.0 * eps1 * U1)
    
    # Équation 3 : Bilan de la Couche 2 (haute)
    # Entrant : IR surface (transmis par C1 puis absorbé par C2) + IR C1 absorbé par C2
    # Sortant : Infrarouge émis vers le haut ET vers le bas (2 * eps2 * U2)
    bilan_c2 = (eps2 * U0 * (1.0 - eps1)) + (eps1 * eps2 * U1) - (2.0 * eps2 * U2)
    
    return [bilan_surf, bilan_c1, bilan_c2]

# =============================================================================
# 4. RÉSOLUTION NUMÉRIQUE ET AFFICHAGE
# =============================================================================
# Devinette initiale : 15°C surface, -13°C couche basse, -43°C couche haute
T_guess = [288.0, 260.0, 230.0]

# Résolution
T_equilibre = fsolve(bilan_radiatif_2_couches, T_guess)

print("--- RÉSULTATS DU MODÈLE À 2 COUCHES ---")
print(f"Concentration CO2 : {C_CO2} ppm")
print(f"Émissivité (calculée) par couche : {eps1:.3f}")
print("-" * 40)
print(f"T_Surface (T0)      : {T_equilibre[0]:.2f} K  soit  {T_equilibre[0] - 273.15:.2f} °C")
print(f"T_Couche Basse (T1) : {T_equilibre[1]:.2f} K  soit  {T_equilibre[1] - 273.15:.2f} °C")
print(f"T_Couche Haute (T2) : {T_equilibre[2]:.2f} K  soit  {T_equilibre[2] - 273.15:.2f} °C")