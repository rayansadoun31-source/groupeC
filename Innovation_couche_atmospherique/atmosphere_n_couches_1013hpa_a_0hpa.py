import numpy as np
from scipy.optimize import fsolve

# =============================================================================
# 1. PARAMÈTRES ET CONSTANTES
# =============================================================================
S0 = 1361.0      
albedo = 0.3     
sigma = 5.67e-8  
P0 = 1013.25     

C_CO2 = 415.0    
k_CO2 = 0.0035   

# ---> CHOISISSEZ LE NOMBRE DE COUCHES ICI <---
N_couches = 12  

# =============================================================================
# 2. PRÉPARATION DE L'ATMOSPHÈRE
# =============================================================================
# Chaque couche a la même épaisseur de pression (même masse)
delta_P = P0 / N_couches

# Émissivité d'une couche (Loi de Beer-Lambert)
eps_couche = 1.0 - np.exp(-k_CO2 * C_CO2 * (delta_P / P0))

# On crée un tableau d'émissivités de taille N+1 (Indice 0 = Surface)
# La surface est un corps noir parfait (eps = 1.0)
eps_full = np.zeros(N_couches + 1)
eps_full[0] = 1.0
eps_full[1:] = eps_couche

# =============================================================================
# 3. FONCTIONS OUTILS
# =============================================================================
def calculer_transmittance(idx_source, idx_dest):
    """Calcule la fraction de rayonnement qui survit entre deux indices."""
    start = min(idx_source, idx_dest) + 1
    end = max(idx_source, idx_dest)
    
    # S'ils sont adjacents, il n'y a rien entre eux, transmittance = 100%
    if start >= end:
        return 1.0
    
    # Sinon, on multiplie les transparences (1 - eps) des couches intermédiaires
    trans = 1.0
    for k in range(start, end):
        trans *= (1.0 - eps_full[k])
    return trans

# =============================================================================
# 4. LE MOTEUR DU MODÈLE À N COUCHES
# =============================================================================
def bilan_radiatif_N_couches(T):
    # T est un tableau de taille N+1 : [T_surface, T_couche1, ..., T_coucheN]
    
    # 1. Calcul du rayonnement émis par chaque élément (U = eps * sigma * T^4)
    U = np.zeros(N_couches + 1)
    for i in range(N_couches + 1):
        U[i] = eps_full[i] * sigma * T[i]**4
        
    # 2. Initialisation des bilans nets
    bilan = np.zeros(N_couches + 1)
    
    # Solaire absorbé par la surface
    F_sol = (S0 / 4.0) * (1.0 - albedo)
    bilan[0] += F_sol
    
    # Pertes par émission (La surface émet vers le haut, l'atmosphère vers le haut ET le bas)
    bilan[0] -= U[0]
    for i in range(1, N_couches + 1):
        bilan[i] -= 2.0 * U[i]
        
    # 3. Distribution de l'énergie (Qui éclaire qui ?)
    # On fait interagir chaque source i avec chaque destination j
    for i in range(N_couches + 1):
        for j in range(N_couches + 1):
            if i == j: 
                continue # On ne s'éclaire pas soi-même
            
            # Fraction de l'énergie de 'i' qui atteint 'j'
            transmittance = calculer_transmittance(i, j)
            
            # Énergie absorbée par 'j'
            energie_absorbee = U[i] * transmittance * eps_full[j]
            bilan[j] += energie_absorbee
            
    return bilan

# =============================================================================
# 5. RÉSOLUTION
# =============================================================================
# Devinette initiale : on génère un gradient linéaire (ex: de 15°C à -60°C)
T_guess = np.linspace(288.0, 210.0, N_couches + 1)

T_equilibre = fsolve(bilan_radiatif_N_couches, T_guess)

print(f"--- MODÈLE À {N_couches} COUCHES ---")
print(f"T_Surface : {T_equilibre[0] - 273.15:.2f} °C")
for i in range(1, N_couches + 1):
    print(f"T_Couche {i}  : {T_equilibre[i] - 273.15:.2f} °C")