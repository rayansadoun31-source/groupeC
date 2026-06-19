# modele_sphere_basse_res.py
# ==============================================================================
# MODÈLE 0-D DE TEMPÉRATURE DE SURFACE - VISUALISATION SPHÈRE 3D
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.colors import Normalize
from matplotlib import cm
from tqdm import tqdm
import pathlib
import os
import sys

# --- Import des modules locaux ---
import fonctions as f
import lib

# Transformation directe de l'entrée utilisateur
choix_utilisateur = input("Quel modèle lancer ?\n  1. simplifié \n  2. modèle complet \nVotre choix [1/2]: ").strip()
est_modele_simplifie = (choix_utilisateur == '1')

# --- Dépendances optionnelles pour la visualisation ---
try:
    import cartopy.feature as cfeature
    from cartopy.io import shapereader
    USE_CARTOPY = True
    print("Cartopy détecté. Les lignes de côte seront affichées en 3D.")
except ImportError:
    USE_CARTOPY = False
    print("AVERTISSEMENT: Cartopy non trouvé. Les côtes ne seront pas affichées.")


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

    PLOT_LAT = np.array([-90 + i * (180 / NLAT) for i in range(NLAT)])
    PLOT_LON = np.array([-180 + j * (360 / NLON) for j in range(NLON)])

    def flux_solaire_entrant(lat_rad, lon_deg, heure_universelle, albedo=0.30):
        heure_solaire = (heure_universelle + lon_deg / 15) % 24
        cos_zenith = np.cos((heure_solaire - 12) * np.pi / 12) * np.cos(lat_rad)
        return S0 * (1 - albedo) * max(cos_zenith, 0)

    print("Initialisation du modèle simplifié 3D...")
    T_grid_all_times = np.zeros((N_STEPS + 1, NLAT, NLON))

    for i in range(NLAT):
        lat_rad = np.radians(PLOT_LAT[i])
        for j in range(NLON):
            lon_deg = PLOT_LON[j]
            T_grid_all_times[0, i, j] = 288.15 - 30 * np.sin(lat_rad)**2
            
            for k in range(N_STEPS):
                T_act = T_grid_all_times[k, i, j]
                heure_universelle = (k * DT / 3600) % 24
                
                phi_in = flux_solaire_entrant(lat_rad, lon_deg, heure_universelle)
                phi_out = SIGMA * (T_act ** 4) + 20.0 
                
                dT = (phi_in - phi_out) * DT / C_CONST
                T_grid_all_times[k + 1, i, j] = T_act + dT

    print("Simulation simplifiée terminée !")

else:
    # ────────────────────────────────────────────────
    # BRANCHE 2 : MODÈLE COMPLET BASSE RÉSOLUTION
    # ────────────────────────────────────────────────
    NPY_DIR = pathlib.Path("modele4/codes python/ressources/npy")
    STABILIZED_FILE = NPY_DIR / "grid_lowres_stabilized.npy"
    ONEYEAR_FILE = NPY_DIR / "grid_lowres_1yr.npy"

    try:
        print("\n--- Chargement des données géospatiales ---")
        ALBEDO_DIR = pathlib.Path("modele4/codes python/ressources/albedo")
        monthly_albedo_sol, LAT, LON = f.load_albedo_series(ALBEDO_DIR)
        NLAT, NLON = len(LAT), len(LON)

        RZSM_CSV_PATH = pathlib.Path("modele4/codes python/ressources/Cp_humidity/average_rzsm_tout.csv")
        RZSM_GRID, lat_bins_rzsm, lon_bins_rzsm = f.load_and_grid_rzsm_data(RZSM_CSV_PATH)

        CERES_CLIM_DATA = f.load_monthly_cloud_albedo_from_ceres(lat_deg=None, lon_deg=None, return_full_map=True)
        print("--- Toutes les données ont été chargées avec succès ---\n")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"ERREUR CRITIQUE: Un fichier de ressources est introuvable : {e}")
        sys.exit(1)

    def f_rhs(T, phinet, C, q_latent):
        return (phinet - q_latent + lib.P_em_atm_thermal(lib.Tatm) - lib.P_em_surf_thermal(T)) / C

    def integrate_point_temperature(days, lat_rad, lon_deg, alb_sol_daily, alb_nuages_daily, C_const, q_base, T0=288.0):
        from scipy.ndimage import gaussian_filter1d
        N = int(days * 24 * 3600 / lib.dt)
        T = np.empty(N + 1)
        T[0] = T0

        sign_daynight = np.empty(N)
        for k in range(N):
            t_sec = k * lib.dt
            jour_sim = int(t_sec // 86400) + 1
            _, heure_solaire = f.get_time_variables(t_sec, lon_deg)
            sign_daynight[k] = 1.0 if f.cos_incidence(lat_rad, jour_sim, heure_solaire) > 0 else -1.0
        q_latent_smoothed = gaussian_filter1d(q_base * sign_daynight, sigma=3.0, mode="wrap")

        for k in range(N):
            t_sec = k * lib.dt
            day_of_year, heure_solaire = f.get_time_variables(t_sec, lon_deg)
            jour_sim = int(t_sec // 86400) + 1
            albedo_sol = alb_sol_daily[day_of_year]
            albedo_nuages = alb_nuages_daily[day_of_year]
            phi_n = lib.P_inc_solar(lat_rad, jour_sim, heure_solaire, albedo_sol, albedo_nuages)

            X = T[k]
            for _ in range(8):
                F = X - T[k] - lib.dt * f_rhs(X, phi_n, C_const, q_latent_smoothed[k])
                dF = 1.0 - lib.dt * (-4.0 * lib.sigma * X**3 / C_const)
                if abs(dF) < 1e-9: break
                X -= F / dF
                if abs(F) < 1e-6: break
            T[k + 1] = X
        return T

    def run_full_simulation(days, stabilize=False):
        result_file = STABILIZED_FILE if stabilize else ONEYEAR_FILE
        NPY_DIR.mkdir(parents=True, exist_ok=True)
        sim_type = "stabilisée (2 ans)" if stabilize else "rapide (1 an)"
        print(f"\nLancement de la simulation globale {sim_type}...")
        
        N_steps = int(days * 24 * 3600 / lib.dt) + 1
        T_grid = np.zeros((N_steps, NLAT, NLON))

        for i in tqdm(range(NLAT), desc="Progression (latitude)"):
            for j in range(NLON):
                lat, lon = LAT[i], LON[j]
                albedo_mensuel_loc = monthly_albedo_sol[:, i, j]
                alb_sol_daily = f.lisser_donnees_annuelles(albedo_mensuel_loc, sigma=15.0)
                alb_nuages_m = CERES_CLIM_DATA.sel(lat=lat, lon=lon, method="nearest").to_numpy()
                alb_nuages_daily = f.lisser_donnees_annuelles(alb_nuages_m, sigma=15.0)
                
                lat_idx_rzsm = min(np.abs(lat_bins_rzsm[:-1] - lat).argmin(), RZSM_GRID.shape[0] - 1)
                lon_idx_rzsm = min(np.abs(lon_bins_rzsm[:-1] - lon).argmin(), RZSM_GRID.shape[1] - 1)
                rzsm_val = RZSM_GRID[lat_idx_rzsm, lon_idx_rzsm]
                cp_kj = f.compute_cp_from_rzsm(np.array([rzsm_val]))[0] if not np.isnan(rzsm_val) else f.CP_SEC
                
                C_const = (cp_kj * 1000.0) * f.RHO_BULK * lib.EPAISSEUR_ACTIVE
                continent = f.continent_finder(lat, lon)
                q_base = lib.Q_LATENT_CONTINENT.get(continent, lib.Q_LATENT_CONTINENT["Océan"])
                if lat > 75: q_base = 0.0
                T0 = 288.15 - 30 * np.sin(np.radians(lat)) ** 2
                
                T_series = integrate_point_temperature(days, np.radians(lat), lon, alb_sol_daily, alb_nuages_daily, C_const, q_base, T0)
                T_grid[:, i, j] = T_series

        if stabilize:
            steps_per_year = int(365 * 24 * 3600 / lib.dt)
            T_grid = T_grid[steps_per_year:, :, :]

        np.save(result_file, T_grid)
        return T_grid

    target_file = None
    run_sim = False

    if STABILIZED_FILE.exists():
        choice = input(f"Fichier stabilisé trouvé ('{STABILIZED_FILE.name}'). Charger (c) ou relancer (r) ? [c/r]: ").lower()
        if choice == 'c': target_file = STABILIZED_FILE
        else: run_sim = True
    elif ONEYEAR_FILE.exists():
        choice = input(f"Fichier sur 1 an trouvé ('{ONEYEAR_FILE.name}'). Charger (c) ou relancer (r) ? [c/r]: ").lower()
        if choice == 'c': target_file = ONEYEAR_FILE
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
        
    PLOT_LAT = LAT
    PLOT_LON = LON
    DT = lib.dt

# ────────────────────────────────────────────────
# VISUALISATION 3D (Unifiée pour les 2 branches)
# ────────────────────────────────────────────────
SIM_DAYS_DISPLAY = T_grid_all_times.shape[0] // int(24 * 3600 / DT)

plt.close("all")
fig = plt.figure(figsize=(10, 9))
ax = fig.add_subplot(111, projection="3d")

# Forcer un aspect parfaitement sphérique
ax.set_xlim([-1.1, 1.1])
ax.set_ylim([-1.1, 1.1])
ax.set_zlim([-1.1, 1.1])
ax.set_box_aspect([1, 1, 1])

# Préparation des coordonnées
lon_sphere = np.append(PLOT_LON, PLOT_LON[0] + 360)
T_grid_sphere = np.concatenate((T_grid_all_times, T_grid_all_times[:, :, 0:1]), axis=2)
lon_rad = np.radians(lon_sphere)
lat_rad = np.radians(90 - PLOT_LAT)
lon_mesh, lat_mesh = np.meshgrid(lon_rad, lat_rad)
R = 1.0
X = R * np.sin(lat_mesh) * np.cos(lon_mesh)
Y = R * np.sin(lat_mesh) * np.sin(lon_mesh)
Z = R * np.cos(lat_mesh)

vmin, vmax = 220, 320
if est_modele_simplifie: vmin, vmax = 250, 310 # Echelle un peu réduite pour le simplifié

norm = Normalize(vmin=vmin, vmax=vmax)
cmap = cm.inferno

T_slice = T_grid_sphere[0, :, :]
face_colors = cmap(norm(T_slice))
surf = ax.plot_surface(X, Y, Z, facecolors=face_colors, rstride=1, cstride=1, antialiased=False, shade=False, edgecolor='none', zorder=1)
ax.set_axis_off()

if USE_CARTOPY:
    R_coast = 1.08
    coastline_feature = cfeature.COASTLINE
    for geometry in coastline_feature.geometries():
        for line in (geometry if hasattr(geometry, 'geoms') else [geometry]):
            lons, lats = line.xy
            lon_c_rad = np.radians(np.array(lons))
            lat_c_rad = np.radians(90 - np.array(lats))
            Xc = R_coast * np.sin(lat_c_rad) * np.cos(lon_c_rad)
            Yc = R_coast * np.sin(lat_c_rad) * np.sin(lon_c_rad)
            Zc = R_coast * np.cos(lat_c_rad)
            ax.plot(Xc, Yc, Zc, color='black', linewidth=1.2, zorder=10, alpha=0.9)

m = cm.ScalarMappable(cmap=cmap, norm=norm)
m.set_array([])
cb = fig.colorbar(m, ax=ax, shrink=0.5, aspect=10, pad=0.01)
cb.set_label("Température de surface (K)")
plt.subplots_adjust(bottom=0.2)
title = fig.suptitle("Jour 0, Heure 0", fontsize=14)
ax_slider_day = plt.axes([0.2, 0.1, 0.6, 0.03])
slider_day = Slider(ax_slider_day, "Jour", 0, SIM_DAYS_DISPLAY - 1, valinit=0, valstep=1)
ax_slider_hour = plt.axes([0.2, 0.05, 0.6, 0.03])
slider_hour = Slider(ax_slider_hour, "Heure", 0, 23, valinit=0, valstep=1)

def _refresh(val):
    day = int(slider_day.val)
    hour = int(slider_hour.val)
    steps_per_day = int(24 * 3600 / DT)
    steps_per_hour = int(3600 / DT)
    time_idx = min(day * steps_per_day + hour * steps_per_hour, T_grid_sphere.shape[0] - 1)
    T_slice = T_grid_sphere[time_idx, :, :]
    new_colors_3d = cmap(norm(T_slice))
    colors_for_faces = new_colors_3d[:-1, :-1, :]
    surf.set_facecolors(colors_for_faces.reshape(-1, 4))
    title.set_text(f"Jour {day}, Heure {hour}")
    fig.canvas.draw_idle()

slider_day.on_changed(_refresh)
slider_hour.on_changed(_refresh)
_refresh(0)

print("\nFenêtre de visualisation 3D ouverte. Tournez la sphère à la souris.")
plt.show()