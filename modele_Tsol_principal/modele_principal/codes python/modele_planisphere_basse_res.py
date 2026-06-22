# modele_planisphere_basse_res.py
# ==============================================================================
# MODÈLE 0-D DE TEMPÉRATURE DE SURFACE - SIMULATION GLOBALE INTERACTIVE
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pathlib
from scipy.ndimage import gaussian_filter1d
from tqdm import tqdm
import os
import sys

# --- Import des modules locaux ---
import fonctions as f
import lib

# Transformation directe de l'entrée utilisateur en vrai booléen
choix_utilisateur = input("Quel modèle lancer ?\n  1. simplifié \n  2. modèle complet \nVotre choix [1/2]: ").strip()
est_modele_simplifie = (choix_utilisateur == '1')

# --- INITIALISATION CARTOPY ---
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    USE_CARTOPY = True
    print("Cartopy détecté. Rendu de la carte optimal.")
except ImportError:
    USE_CARTOPY = False
    print("AVERTISSEMENT: Cartopy non trouvé. Utilisation du rendu Matplotlib standard.")


if est_modele_simplifie:
    # ────────────────────────────────────────────────
    # BRANCHE 1 : MODÈLE SIMPLIFIÉ (PROTOTYPAGE)
    # ────────────────────────────────────────────────
    NLAT = 36               
    NLON = 72               
    DAYS_TO_SIMULATE = 30   
    DT = 3600               
    N_STEPS = int(DAYS_TO_SIMULATE * 24 * 3600 / DT)

    SIGMA = 5.67e-8         
    S0 = 1361.0             
    C_CONST = 2e7           

    # Création explicite des tableaux LAT et LON pour l'interface interactive
    LAT = np.array([-90 + i * (180 / NLAT) for i in range(NLAT)])
    LON = np.array([-180 + j * (360 / NLON) for j in range(NLON)])

    def flux_solaire_entrant(lat_rad, lon_deg, heure_universelle, albedo=0.30):
        heure_solaire = (heure_universelle + lon_deg / 15) % 24
        cos_zenith = np.cos((heure_solaire - 12) * np.pi / 12) * np.cos(lat_rad)
        return S0 * (1 - albedo) * max(cos_zenith, 0)

    print("Initialisation du modèle simplifié...")
    T_grid_all_times = np.zeros((N_STEPS + 1, NLAT, NLON))

    for i in range(NLAT):
        lat_rad = np.radians(LAT[i])
        for j in range(NLON):
            lon_deg = LON[j]
            T_grid_all_times[0, i, j] = 288.15 - 30 * np.sin(lat_rad)**2
            
            for k in range(N_STEPS):
                T_act = T_grid_all_times[k, i, j]
                heure_universelle = (k * DT / 3600) % 24
                
                phi_in = flux_solaire_entrant(lat_rad, lon_deg, heure_universelle)
                phi_out = SIGMA * (T_act ** 4) + 20.0 # 20.0 = chaleur latente bidon
                
                dT = (phi_in - phi_out) * DT / C_CONST
                T_grid_all_times[k + 1, i, j] = T_act + dT

    print("Simulation simplifiée terminée !")

else:
    # --- Dépendances optionnelles pour une meilleure visualisation ---
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        USE_CARTOPY = True
        print("Cartopy détecté. Le rendu de la carte sera amélioré.")
    except ImportError:
        USE_CARTOPY = False
        print("AVERTISSEMENT: Cartopy non trouvé. Utilisation du rendu Matplotlib standard.")

    # --- Chemins des fichiers de résultats ---
    NPY_DIR = pathlib.Path("modele_Tsol_principal/modele_principal/codes python/ressources/npy")
    LOWRES_STABILIZED_FILE = NPY_DIR / "grid_lowres_stabilized_FORCAGE.npy"
    LOWRES_ONEYEAR_FILE = NPY_DIR / "grid_lowres_1yr_FORCAGE.npy"

    # ────────────────────────────────────────────────
    # CHARGEMENT DES DONNÉES GLOBALES
    # ────────────────────────────────────────────────
    try:
        print("\n--- Chargement des données géospatiales ---")
        ALBEDO_DIR = pathlib.Path("modele_Tsol_principal/modele_principal/codes python/ressources/albedo")
        monthly_albedo_sol, LAT, LON = f.load_albedo_series(ALBEDO_DIR)
        NLAT, NLON = len(LAT), len(LON)

        RZSM_CSV_PATH = pathlib.Path(
                    "modele_Tsol_principal/modele_principal/codes python/ressources/Cp_humidity/average_rzsm_tout.csv"
        )
        RZSM_GRID, lat_bins_rzsm, lon_bins_rzsm = f.load_and_grid_rzsm_data(
            RZSM_CSV_PATH
        )

        CERES_CLIM_DATA = f.load_monthly_cloud_albedo_from_ceres(
            lat_deg=None, lon_deg=None, return_full_map=True
        )
        print("--- Toutes les données ont été chargées avec succès ---\n")

    except (FileNotFoundError, RuntimeError) as e:
        print(f"ERREUR CRITIQUE: Un fichier de ressources est introuvable : {e}")
        sys.exit(1)

    # ────────────────────────────────────────────────
    # FONCTIONS DE SIMULATION (CORRIGÉES ET COUPLÉES)
    # ────────────────────────────────────────────────
    def f_rhs(T, phinet, C, q_latent, p_cond, forcage_atm):
        """
        Calcule la partie droite de l'équation différentielle (dT/dt).
        """
        return (
            phinet
            - q_latent
            + forcage_atm  # Forçage radiatif atmosphérique interpolé pour ce point et ce pas de temps
            - lib.P_em_surf_thermal(T)
            + p_cond  # Flux de chaleur issu de la conduction profonde du sol
        ) / C

    def integrate_point_temperature(
        days,
        lat_rad,
        lon_deg,
        alb_sol_daily,
        alb_nuages_daily,
        C_const,
        q_base,
        forcage_pixel,
        T0=288.0,
    ):
        """Intègre la température pour UN SEUL point géographique."""
        N = int(days * 24 * 3600 / lib.dt)
        T = np.empty(N + 1)
        T[0] = T0

        # --- INITIALISATION DE LA COLONNE DE SOL POUR CE PIXEL ---
        # On initialise le sol à la température d'équilibre de départ T0
        T_sol = f.initialiser_profil_sol(T_moy_annuelle=T0, N=13)

        sign_daynight = np.empty(N)
        for k in range(N):
            t_sec = k * lib.dt
            jour_sim = int(t_sec // 86400) + 1
            _, heure_solaire = f.get_time_variables(t_sec, lon_deg)
            sign_daynight[k] = (
                1.0
                if f.cos_incidence(lat_rad, jour_sim, heure_solaire) > 0
                else -1.0
            )
        q_latent_smoothed = gaussian_filter1d(
            q_base * sign_daynight, sigma=3.0, mode="wrap"
        )

        for k in range(N):
            t_sec = k * lib.dt
            day_of_year, heure_solaire = f.get_time_variables(t_sec, lon_deg)
            jour_sim = int(t_sec // 86400) + 1

            albedo_sol = alb_sol_daily[day_of_year]
            albedo_nuages = alb_nuages_daily[day_of_year]
            q_latent_step = q_latent_smoothed[k]
            # On calcule à quel jour on se trouve dans la simulation
            jour_index = int((k * lib.dt) // 86400)
            # Sécurité anti-plantage : si on dépasse la taille du tableau, on prend le dernier jour
            jour_index = min(jour_index, len(forcage_pixel) - 1) 
            # On extrait la valeur constante pour ce jour précis
            forcage_actuel = forcage_pixel[jour_index]

            phi_n = lib.P_inc_solar(
                lat_rad, jour_sim, heure_solaire, albedo_sol, albedo_nuages
            )

            # --- CALCUL DE LA CONDUCTION DU SOL POUR CE PAS DE TEMPS ---
            # On calcule le flux conducteur p_cond échangé avec le sous-sol
            T_sol, p_cond = f.calculer_conduction_sol(T[k], T_sol, lib.dt)

            X = T[k]
            for _ in range(8):
                # CORRECTION : p_cond est maintenant correctement passé en 5e argument
                F = X - T[k] - lib.dt * f_rhs(X, phi_n, C_const, q_latent_step, p_cond, forcage_actuel)
                dF = 1.0 - lib.dt * (-4.0 * lib.sigma * X**3 / C_const)
                
                if abs(dF) < 1e-9:
                    break
                X -= F / dF
                if abs(F) < 1e-6:
                    break
            T[k + 1] = X
        return T

    def run_full_simulation(days, stabilize=False):
        """Exécute la simulation pour toute la grille et sauvegarde le résultat."""
        result_file = LOWRES_STABILIZED_FILE if stabilize else LOWRES_ONEYEAR_FILE
        NPY_DIR.mkdir(parents=True, exist_ok=True)

        sim_type = "stabilisée (2 ans)" if stabilize else "rapide (1 an)"
        print(f"\nLancement de la simulation globale {sim_type}...")
        print(f"Les résultats seront sauvegardés dans '{result_file}'")

        print("Interpolation du forçage atmosphérique sur la grille...")
        FORCAGE_ANNUEL = f.preparer_calendrier_forcage(NLAT, NLON, days)
        

        N_steps = int(days * 24 * 3600 / lib.dt) + 1
        T_grid = np.zeros((N_steps, NLAT, NLON))

        for i in tqdm(range(NLAT), desc="Progression (latitude)"):
            for j in range(NLON):
                lat, lon = LAT[i], LON[j]

                albedo_mensuel_loc = monthly_albedo_sol[:, i, j]
                alb_sol_daily = f.lisser_donnees_annuelles(
                    albedo_mensuel_loc, sigma=15.0
                )

                alb_nuages_m = CERES_CLIM_DATA.sel(
                    lat=lat, lon=lon, method="nearest"
                ).to_numpy()
                alb_nuages_daily = f.lisser_donnees_annuelles(
                    alb_nuages_m, sigma=15.0
                )

                lat_idx_rzsm = min(
                    np.abs(lat_bins_rzsm[:-1] - lat).argmin(), RZSM_GRID.shape[0] - 1
                )
                lon_idx_rzsm = min(
                    np.abs(lon_bins_rzsm[:-1] - lon).argmin(), RZSM_GRID.shape[1] - 1
                )
                rzsm_val = RZSM_GRID[lat_idx_rzsm, lon_idx_rzsm]
                cp_kj = (
                    f.compute_cp_from_rzsm(np.array([rzsm_val]))[0]
                    if not np.isnan(rzsm_val)
                    else f.CP_SEC
                )
                C_const = (cp_kj * 1000.0) * f.RHO_BULK * lib.EPAISSEUR_ACTIVE

                continent = f.continent_finder(lat, lon)
                q_base = lib.Q_LATENT_CONTINENT.get(
                    continent, lib.Q_LATENT_CONTINENT["Océan"]
                )
                if lat > 75:
                    q_base = 0.0

                T0 = 288.15 - 30 * np.sin(np.radians(lat)) ** 2

                # --- LE VECTEUR QUE TU AS OUBLIÉ D'EXTRAIRE ---
                forcage_pixel = FORCAGE_ANNUEL[:, i, j]

                T_series = integrate_point_temperature(
                    days,
                    np.radians(lat),
                    lon,
                    alb_sol_daily,
                    alb_nuages_daily,
                    C_const,
                    q_base,
                    forcage_pixel, # <-- IL MANQUAIT CET ARGUMENT
                    T0,
                )
                T_grid[:, i, j] = T_series

        if stabilize:
            print("Simulation terminée. Extraction de la deuxième année...")
            steps_per_year = int(365 * 24 * 3600 / lib.dt)
            T_grid = T_grid[steps_per_year:, :, :]

        print(f"Sauvegarde des résultats dans '{result_file}'...")
        np.save(result_file, T_grid)
        return T_grid
    
    target_file = None
    run_sim = False

    if LOWRES_STABILIZED_FILE.exists():
        choice = input(f"Fichier stabilisé trouvé ('{LOWRES_STABILIZED_FILE.name}'). Charger (c) ou relancer (r) ? [c/r]: ").lower()
        if choice == 'c': target_file = LOWRES_STABILIZED_FILE
        else: run_sim = True
    elif LOWRES_ONEYEAR_FILE.exists():
        choice = input(f"Fichier sur 1 an trouvé ('{LOWRES_ONEYEAR_FILE.name}'). Charger (c) ou relancer (r) ? [c/r]: ").lower()
        if choice == 'c': target_file = LOWRES_ONEYEAR_FILE
        else: run_sim = True
    else:
        run_sim = True

    if run_sim and target_file is None:
        choice = input("Lancer simulation : 1. Rapide (1 an) / 2. Stabilisée (2 ans) ? [1/2]: ").lower()
        if choice == '2':
            T_grid_all_times = run_full_simulation(730, True)
        else:
            T_grid_all_times = run_full_simulation(365, False)
    else:
        print(f"Chargement de la matrice depuis '{target_file}'...")
        T_grid_all_times = np.load(target_file)
        
    # Unification de la constante de temps pour le Dashboard
    DT = lib.dt

# ────────────────────────────────────────────────
# 4. LE DASHBOARD INTERACTIF MATPLOTLIB (Le cœur du système)
# ────────────────────────────────────────────────
print("Génération du Dashboard interactif...")

SIM_DAYS_DISPLAY = T_grid_all_times.shape[0] // int(24 * 3600 / DT)
time_axis_days = np.arange(T_grid_all_times.shape[0]) * DT / 86400

plt.close("all")
# On crée une grande figure horizontale pour avoir 2 graphiques côte à côte
fig = plt.figure(figsize=(15, 7))

# --- GRAPHIQUE 1 : LA CARTE (À GAUCHE) ---
if USE_CARTOPY:
    proj = ccrs.PlateCarree()
    ax_map = fig.add_subplot(1, 2, 1, projection=proj)
    transform = ccrs.PlateCarree()
else:
    ax_map = fig.add_subplot(1, 2, 1)
    transform = ax_map.transData

initial_T_grid = T_grid_all_times[0, :, :]

im = ax_map.imshow(
    initial_T_grid - 273.15,
    origin="lower",
    extent=[-180, 180, -90, 90],
    transform=transform,
    cmap="inferno",
    vmin=-30,
    vmax=40,
)

if USE_CARTOPY:
    ax_map.coastlines(color='black', linewidth=1)
    ax_map.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
else:
    ax_map.set_xlabel("Longitude")
    ax_map.set_ylabel("Latitude")
    ax_map.grid(True, linestyle='--', alpha=0.5)

cb = fig.colorbar(im, ax=ax_map, orientation="horizontal", fraction=0.046, pad=0.08)
cb.set_label("Température de surface (°C)", fontsize=10)
title_map = ax_map.set_title("Carte Thermique - Jour 0, Heure 0", fontsize=12)


# --- GRAPHIQUE 2 : LA COURBE DE TEMPÉRATURE (À DROITE) ---
ax_temp = fig.add_subplot(1, 2, 2)
ax_temp.set_title("Cliquez sur la carte pour générer la courbe", fontsize=12)
ax_temp.set_xlabel("Temps de simulation (Jours)")
ax_temp.set_ylabel("Température (°C)")
ax_temp.grid(True, linestyle='--', alpha=0.6)
ax_temp.set_xlim(0, SIM_DAYS_DISPLAY)
ax_temp.set_ylim(-50, 50)
line_temp, = ax_temp.plot([], [], color='firebrick', linewidth=2) # Ligne vide initialement


# --- WIDGETS : LES SLIDERS (EN BAS DE L'ÉCRAN) ---
plt.subplots_adjust(bottom=0.25, wspace=0.3)

ax_slider_day = plt.axes([0.15, 0.1, 0.3, 0.03])
slider_day = Slider(ax_slider_day, "Jour", 0, SIM_DAYS_DISPLAY - 1, valinit=0, valstep=1)

ax_slider_hour = plt.axes([0.15, 0.05, 0.3, 0.03])
slider_hour = Slider(ax_slider_hour, "Heure", 0, 23, valinit=0, valstep=1)

# --- ÉVÉNEMENTS INTERACTIFS ---

# Événement 1 : Modification des Sliders -> Met à jour la carte
def _refresh_map(val):
    day = int(slider_day.val)
    hour = int(slider_hour.val)
    time_idx = min(day * int(24 * 3600 / DT) + hour * int(3600 / DT), T_grid_all_times.shape[0] - 1)
    
    im.set_data(T_grid_all_times[time_idx, :, :] - 273.15)
    title_map.set_text(f"Carte Thermique - Jour {day}, Heure {hour}")
    fig.canvas.draw_idle()

# Événement 2 : Clic sur la carte -> Met à jour la courbe
def on_map_click(event):
    # Sécurité anti-crash silencieux
    try:
        if event.inaxes != ax_map:
            return
            
        lon_clic, lat_clic = event.xdata, event.ydata
        if lon_clic is None or lat_clic is None:
            return
            
        print(f"--> CLIC DÉTECTÉ sur la carte : Lat={lat_clic:.2f}, Lon={lon_clic:.2f}")
            
        # 1. On trouve la latitude la plus proche
        idx_lat = np.abs(LAT - lat_clic).argmin()
        
        # 2. Sécurité pour la longitude (gère la différence entre -180/180 et 0/360)
        lon_corrige = lon_clic if LON.min() < 0 else (lon_clic + 360) % 360
        idx_lon = np.abs(LON - lon_corrige).argmin()
        
        # 3. Extraction des données
        serie_temp_k = T_grid_all_times[:, idx_lat, idx_lon]
        serie_temp_c = serie_temp_k - 273.15
        
        # 4. Mise à jour du graphique
        line_temp.set_data(time_axis_days, serie_temp_c)
        
        y_min, y_max = serie_temp_c.min(), serie_temp_c.max()
        if y_min == y_max:  # Si la température est 100% constante
            marge = 5.0
        else:
            marge = max((y_max - y_min) * 0.1, 2.0)
            
        ax_temp.set_ylim(y_min - marge, y_max + marge)
        ax_temp.set_title(f"Évolution Thermique à {LAT[idx_lat]:.1f}°N, {LON[idx_lon]:.1f}°E", fontsize=12, color='firebrick')
        
        fig.canvas.draw_idle()
        print("    Courbe mise à jour avec succès !")
        
    except Exception as e:
        print(f"!!! ERREUR LORS DU CLIC : {e} !!!")

# On branche les événements
slider_day.on_changed(_refresh_map)
slider_hour.on_changed(_refresh_map)
fig.canvas.mpl_connect('button_press_event', on_map_click)

print("\nTableau de bord ouvert. Cliquez n'importe où sur la carte !")
plt.show()