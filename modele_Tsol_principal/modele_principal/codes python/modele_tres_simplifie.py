# modele_tres_simplifie.py
# ==============================================================================
# MODÈLE 0-D DE TEMPÉRATURE DE SURFACE - SQUELETTE PÉDAGOGIQUE MODULAIRE
#
# BUT : Comprendre l'architecture d'un modèle climatique sur grille.
# ARCHITECTURE : La boucle temporelle appelle des fonctions physiques "boîtes noires".
# PHYSIQUE : Simplifiée à l'extrême (les fonctions renvoient des constantes ou des calculs basiques).
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# --- IMPORT CARTOPY (Moteur de rendu cartographique) ---
try:
    import cartopy.crs as ccrs
    USE_CARTOPY = True
except ImportError:
    USE_CARTOPY = False
    print("Cartopy non détecté. Rendu basique.")

# ────────────────────────────────────────────────
# 1. PARAMÈTRES ET CONSTANTES GLOBALES (UNITÉS SI)
# ────────────────────────────────────────────────
# Paramètres spatio-temporels de base
NLAT = 36               # Résolution latitude (5°)
NLON = 72               # Résolution longitude (5°)
DAYS_TO_SIMULATE = 30   # Durée de la simulation (jours)
DT = 3600               # Pas de temps d'intégration (1 heure)
N_STEPS = int(DAYS_TO_SIMULATE * 24 * 3600 / DT)

# Constantes physiques
SIGMA = 5.67e-8         # Constante de Stefan-Boltzmann
S0 = 1361.0             # Irradiance Solaire
C_CONST = 2e7           # Capacité thermique fixe

# Paramètres climatiques "Boîtes Noires"
ALBEDO_MOYEN = 0.30     
FLUX_LATENT = 20.0      

# ──────────────────────────────────────────────────
# 2. FONCTIONS PHYSIQUES (APPROCHES DÉDIÉES À L'APPRENTISSAGE)
# ──────────────────────────────────────────────────

def calculer_albedo(lat_rad, lon_deg):
    """Boîte noire : Dans le vrai modèle, cette fonction lit une base de données. Ici, c'est une constante."""
    return 0.30

def calculer_chaleur_latente(lat_rad, lon_deg):
    """Boîte noire : Simule une perte d'énergie par évaporation fixe pour tous les pixels."""
    return 20.0

def flux_solaire_entrant(lat_rad, lon_deg, heure_universelle, albedo):
    """Calcule l'alternance jour/nuit et la puissance reçue selon l'angle d'inclinaison du soleil."""
    heure_solaire = (heure_universelle + lon_deg / 15) % 24
    cos_zenith = np.cos((heure_solaire - 12) * np.pi / 12) * np.cos(lat_rad)
    return S0 * (1 - albedo) * max(cos_zenith, 0)

def flux_infrarouge_sortant(T_actuelle):
    """Simule la perte d'énergie par rayonnement de la surface terrestre vers l'espace."""
    return SIGMA * (T_actuelle ** 4)

def appliquer_methode_euler(T_actuelle, flux_in, flux_out):
    """
    Méthode d'intégration numérique d'Euler explicite. 
    Convertit le bilan d'énergie (Flux In - Flux Out) en variation de température (dT).
    """
    dT = (flux_in - flux_out) * DT / C_CONST
    return T_actuelle + dT

# ────────────────────────────────────────────────
# 3. INITIALISATION ET BOUCLE PRINCIPALE
# ────────────────────────────────────────────────
print("Initialisation du modèle...")
T_grid = np.zeros((N_STEPS + 1, NLAT, NLON))

# Double boucle spatiale : On parcourt chaque latitude et longitude
for i in range(NLAT):
    lat_rad = np.radians(-90 + i * (180 / NLAT))
    
    for j in range(NLON):
        lon_deg = -180 + j * (360 / NLON)
        
        # Initialisation : Équateur chaud, Pôles froids
        T_grid[0, i, j] = 288.15 - 30 * np.sin(lat_rad)**2
        
        # Boucle temporelle : On calcule l'évolution de CE pixel précis sur 30 jours
        for k in range(N_STEPS):
            T_act = T_grid[k, i, j]
            heure_universelle = (k * DT / 3600) % 24
            
            # --- APPEL DES MODULES PHYSIQUES ---
            alb = calculer_albedo(lat_rad, lon_deg)
            q_lat = calculer_chaleur_latente(lat_rad, lon_deg)
            
            phi_in = flux_solaire_entrant(lat_rad, lon_deg, heure_universelle, alb)
            phi_out = flux_infrarouge_sortant(T_act) + q_lat
            
            # --- MISE À JOUR ET SAUVEGARDE DU PAS DE TEMPS ---
            T_grid[k + 1, i, j] = appliquer_methode_euler(T_act, phi_in, phi_out)

print("Simulation terminée !")

# ────────────────────────────────────────────────
# 4. AFFICHAGE (Visualisation des matrices)
# ────────────────────────────────────────────────
print("Génération de la carte spatio-temporelle...")

plt.close("all")
fig = plt.figure(figsize=(12, 7))

if USE_CARTOPY:
    proj = ccrs.PlateCarree()
    ax = plt.axes(projection=proj)
    transform = ccrs.PlateCarree()
else:
    ax = plt.axes()
    transform = ax.transData

im = ax.imshow(
    T_grid[0, :, :] - 273.15,
    origin="lower",
    extent=[-180, 180, -90, 90],
    transform=transform,
    cmap="inferno",
    vmin=-30,
    vmax=40,
)

if USE_CARTOPY:
    ax.coastlines(color='black', linewidth=1)
    ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
else:
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle='--', alpha=0.5)

cb = fig.colorbar(im, ax=ax, orientation="vertical", fraction=0.03, pad=0.04)
cb.set_label("Température de surface (°C)", fontsize=12)

plt.subplots_adjust(bottom=0.25, top=0.95)
title = ax.set_title("Température de surface - Jour 0, Heure 0", fontsize=14)

# Définition des sliders de navigation temporelle
ax_slider_day = plt.axes([0.2, 0.1, 0.6, 0.03])
slider_day = Slider(ax_slider_day, "Jour", 0, DAYS_TO_SIMULATE - 1, valinit=0, valstep=1)

ax_slider_hour = plt.axes([0.2, 0.05, 0.6, 0.03])
slider_hour = Slider(ax_slider_hour, "Heure", 0, 23, valinit=0, valstep=1)

def _refresh(val):
    """Fonction IHM : Rafraîchit l'image affichée selon la valeur sélectionnée par l'utilisateur."""
    day = int(slider_day.val)
    hour = int(slider_hour.val)
    time_idx = min(day * int(24 * 3600 / DT) + hour * int(3600 / DT), T_grid.shape[0] - 1)
    
    im.set_data(T_grid[time_idx, :, :] - 273.15)
    title.set_text(f"Température de surface - Jour {day}, Heure {hour}")
    fig.canvas.draw_idle()

slider_day.on_changed(_refresh)
slider_hour.on_changed(_refresh)
plt.show()