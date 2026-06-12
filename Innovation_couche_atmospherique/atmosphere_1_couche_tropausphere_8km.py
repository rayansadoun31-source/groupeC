import numpy as np
from scipy.optimize import fsolve

# =============================================================================
# 1. PARAMÈTRES ET CONSTANTES PHYSIQUES
# =============================================================================
S0 = 1361.0      # Constante solaire en W/m^2 [Source: GIEC AR6 / Mesures satellites]
albedo = 0.3     # Albédo moyen terrestre [Source: GIEC AR6]
sigma = 5.67e-8  # Constante de Stefan-Boltzmann en W/m^2/K^4 [Source: CODATA 2018]

# Émissivité de la couche atmosphérique (eps). 
# Une valeur de 0.78 reproduit approximativement l'effet de serre actuel (T_surf ~ 15°C).
eps = 0.78       

# =============================================================================
# 2. DÉFINITION DU SYSTÈME D'ÉQUATIONS
# =============================================================================
def bilan_radiatif_1_couche(T):
    """
    Fonction évaluant l'équilibre radiatif de la Terre avec 1 couche atmosphérique.
    Prend en entrée un tableau T = [T0, T1] (température de surface, température atmosphère).
    Retourne l'erreur des flux nets (doit valoir 0 à l'équilibre).
    """
    # Déballage des températures (en Kelvin)
    T0, T1 = T 
    
    # Énergie solaire absorbée par la surface (géométrie sphérique = S0/4)
    F_solaire = (S0 / 4.0) * (1.0 - albedo)
    
    # Équation 1 : Bilan de la surface terrestre
    # Flux net = (Solaire entrant + Infrarouge reçu de l'atmosphère) - Infrarouge émis par la surface
    bilan_surface = F_solaire + (eps * sigma * T1**4) - (sigma * T0**4)
    
    # Équation 2 : Bilan de la couche atmosphérique
    # Flux net = Infrarouge reçu de la surface - Infrarouge émis (vers le haut ET vers le bas, d'où le facteur 2)
    bilan_atmosphere = (eps * sigma * T0**4) - (2.0 * eps * sigma * T1**4)
    
    # On retourne les "erreurs". Le solveur va chercher T0 et T1 pour que ces 2 valeurs soient nulles.
    return [bilan_surface, bilan_atmosphere]

# =============================================================================
# 3. RÉSOLUTION NUMÉRIQUE
# =============================================================================
# Pour aider le solveur à converger rapidement, on lui donne une "devinette" 
# initiale raisonnable (K) : 15°C pour la surface, -23°C pour l'atmosphère.
T_guess = [288.15, 250.0]

# fsolve trouve les racines du système d'équations non linéaires
T_equilibre = fsolve(bilan_radiatif_1_couche, T_guess)

# =============================================================================
# 4. AFFICHAGE DES RÉSULTATS
# =============================================================================
print("--- RÉSULTATS DU MODÈLE À 1 COUCHE ---")
print(f"Paramètres : Émissivité = {eps}, Albédo = {albedo}")
print(f"Température de surface (T0)      : {T_equilibre[0]:.2f} K  soit  {T_equilibre[0] - 273.15:.2f} °C")
print(f"Température atmosphérique (T1)   : {T_equilibre[1]:.2f} K  soit  {T_equilibre[1] - 273.15:.2f} °C")