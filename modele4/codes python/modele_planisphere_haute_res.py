# modele_planisphere_hires.py
# ==============================================================================
# MODÈLE 0-D DE TEMPÉRATURE DE SURFACE - PLANISPHÈRE HAUTE RÉSOLUTION
#
# DESCRIPTION :
# Ce script exécute le modèle thermique complet sur une grille globale HAUTE
# RÉSOLUTION et visualise les résultats sur un planisphère interactif.
# Il est entièrement externalisé et optimisé pour la performance.
#
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.interpolate import RegularGridInterpolator
from tqdm import tqdm
import pathlib
import os
import sys

# --- Import des modules locaux ---
import fonctions as f
import lib

# Transformation directe de l'entrée utilisateur en vrai booléen (True/False)
choix_utilisateur = input("Quel modèle lancer ?\n  1. simplifié \n  2. modèle complet \nVotre choix [1/2]: ").strip()
est_modele_simplifie = (choix_utilisateur == '1')

if est_modele_simplifie:
    # --- IMPORT CARTOPY (Boîte noire pour un bel affichage) ---
    try:
        import cartopy.crs as ccrs
        USE_CARTOPY = True
    except ImportError:
        USE_CARTOPY = False
        print("Cartopy non détecté. Rendu basique.")

    # ────────────────────────────────────────────────
    # 1. PARAMÈTRES ET CONSTANTES GLOBALES (UNITÉS SI)
    # ────────────────────────────────────────────────
    # Paramètres de la grille et du temps
    NLAT = 36               # Résolution latitude (5°)
    NLON = 72               # Résolution longitude (5°)
    DAYS_TO_SIMULATE = 30   # Durée de la simulation (jours)
    DT = 3600               # Pas de temps d'intégration (secondes, s)
    N_STEPS = int(DAYS_TO_SIMULATE * 24 * 3600 / DT)

    # Constantes physiques fondamentales
    SIGMA = 5.67e-8         # Constante de Stefan-Boltzmann (W.m^-2.K^-4)
    S0 = 1361.0             # Constante solaire / Irradiance (W.m^-2)

    # Propriétés thermodynamiques de la surface (Modèle 0-D)
    C_CONST = 2e7           # Capacité thermique surfacique moyenne (J.m^-2.K^-1)

    # Paramètres climatiques simplifiés (Boîtes noires)
    ALBEDO_MOYEN = 0.30     # Albédo planétaire moyen (Sans dimension, %)
    FLUX_LATENT = 20.0      # Flux de chaleur latente moyen (W.m^-2)

    # ──────────────────────────────────────────────────
    # 2. FONCTIONS PHYSIQUES (SIMPLIFIÉES COMME IL FAUT)
    # ──────────────────────────────────────────────────
    def calculer_albedo(lat_rad, lon_deg):
        """
        Physique nulle : renvoie une constante globale.
        Plus tard : brancher ici les données CERES ou un fichier CSV.
        """
        return 0.30

    def calculer_chaleur_latente(lat_rad, lon_deg):
        """
        Physique nulle : l'évaporation enlève 20 W/m² partout.
        """
        return 20.0

    def flux_solaire_entrant(lat_rad, lon_deg, heure_universelle, albedo):
        """
        Physique basique : calcule si le soleil éclaire le pixel selon l'heure locale.
        """
        heure_solaire = (heure_universelle + lon_deg / 15) % 24
        cos_zenith = np.cos((heure_solaire - 12) * np.pi / 12) * np.cos(lat_rad)
        return S0 * (1 - albedo) * max(cos_zenith, 0)

    def flux_infrarouge_sortant(T_actuelle):
        """
        Loi de Stefan-Boltzmann pure.
        """
        return SIGMA * (T_actuelle ** 4)

    def appliquer_methode_euler(T_actuelle, flux_in, flux_out):
        """
        Équation différentielle résolue par méthode d'Euler explicite.
        Bilan d'énergie : C * dT/dt = Somme des flux
        Unité : (W.m^-2) * s / (J.m^-2.K^-1) = Kelvin
        """
        dT = (flux_in - flux_out) * DT / C_CONST
        return T_actuelle + dT

    # ────────────────────────────────────────────────
    # 3. INITIALISATION ET BOUCLE PRINCIPALE (Lisibilité maximale)
    # ────────────────────────────────────────────────
    print("Initialisation du modèle...")
    T_grid = np.zeros((N_STEPS + 1, NLAT, NLON))

    # Boucle spatiale
    for i in range(NLAT):
        lat_rad = np.radians(-90 + i * (180 / NLAT))
        
        for j in range(NLON):
            lon_deg = -180 + j * (360 / NLON)
            
            # Température initiale bidon (plus chaud à l'équateur)
            T_grid[0, i, j] = 288.15 - 30 * np.sin(lat_rad)**2
            
            # Boucle temporelle pour ce pixel
            for k in range(N_STEPS):
                T_act = T_grid[k, i, j]
                heure_universelle = (k * DT / 3600) % 24
                
                # --- APPEL DES MODULES PHYSIQUES ---
                alb = calculer_albedo(lat_rad, lon_deg)
                q_lat = calculer_chaleur_latente(lat_rad, lon_deg)
                
                phi_in = flux_solaire_entrant(lat_rad, lon_deg, heure_universelle, alb)
                phi_out = flux_infrarouge_sortant(T_act) + q_lat
                
                # --- MISE À JOUR ---
                T_grid[k + 1, i, j] = appliquer_methode_euler(T_act, phi_in, phi_out)

    print("Simulation terminée !")

    # ────────────────────────────────────────────────
    # 4. AFFICHAGE CARTOPY (La Boîte Noire Visuelle)
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

    ax_slider_day = plt.axes([0.2, 0.1, 0.6, 0.03])
    slider_day = Slider(ax_slider_day, "Jour", 0, DAYS_TO_SIMULATE - 1, valinit=0, valstep=1)

    ax_slider_hour = plt.axes([0.2, 0.05, 0.6, 0.03])
    slider_hour = Slider(ax_slider_hour, "Heure", 0, 23, valinit=0, valstep=1)

    def _refresh(val):
        day = int(slider_day.val)
        hour = int(slider_hour.val)
        time_idx = min(day * int(24 * 3600 / DT) + hour * int(3600 / DT), T_grid.shape[0] - 1)
        
        im.set_data(T_grid[time_idx, :, :] - 273.15)
        title.set_text(f"Température de surface - Jour {day}, Heure {hour}")
        fig.canvas.draw_idle()

    slider_day.on_changed(_refresh)
    slider_hour.on_changed(_refresh)
    plt.show()

# fin du premier code
else:
    # --- Dépendances optionnelles ---
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        USE_CARTOPY = True
        print("Cartopy détecté. Le rendu de la carte sera amélioré.")
    except ImportError:
        USE_CARTOPY = False
        print("AVERTISSEMENT: Cartopy non trouvé. Utilisation du rendu Matplotlib standard.")

    # --- Chemins des fichiers de résultats HAUTE RÉSOLUTION ---
    NPY_DIR = pathlib.Path("modele4/codes python/ressources/npy")
    HIRES_STABILIZED_FILE = NPY_DIR / "grid_hires_stabilized.npy"
    HIRES_ONEYEAR_FILE = NPY_DIR / "grid_hires_1yr.npy"

    # ────────────────────────────────────────────────
    # CHARGEMENT ET SURÉCHANTILLONNAGE DES DONNÉES (UPSCALE)
    # ────────────────────────────────────────────────

    def upscale_grid(data_lowres, lat_low, lon_low, lat_hi, lon_hi):
        """Interpole une grille 2D de basse à haute résolution."""
        interp = RegularGridInterpolator(
            (lat_low, lon_low), data_lowres, bounds_error=False, fill_value=None
        )
        points_hi = np.array(np.meshgrid(lat_hi, lon_hi, indexing="ij"))
        return interp(np.moveaxis(points_hi, 0, -1))

    

    # ────────────────────────────────────────────────
    # FONCTIONS DE SIMULATION (MODIFIÉES ET COUPLÉES AVEC LE SOL 1D)
    # ────────────────────────────────────────────────
    def f_rhs(T, phinet, C, q_latent, p_cond):
        """Côté droit de l'équation différentielle (dT/dt) incluant la conduction."""
        return (
            phinet
            - q_latent
            + lib.P_em_atm_thermal(lib.Tatm)
            - lib.P_em_surf_thermal(T)
            + p_cond  # Flux de chaleur issu de la conduction profonde du sol
        ) / C

    def integrate_point_temperature(
        days, lat_rad, lon_deg, alb_sol_daily, alb_nuages_daily, C_const, q_base, T0
    ):
        """Intègre la température pour UN SEUL point, en utilisant les profils pré-calculés."""
        from scipy.ndimage import gaussian_filter1d
        N_steps = int(days * 24 * 3600 / lib.dt)
        T = np.empty(N_steps + 1)
        T[0] = T0
        
        # --- INITIALISATION DE LA COLONNE DE SOL DE CE PIXEL ---
        # Le sol profond est initialisé uniformément à sa température d'équilibre locale T0 (en Kelvin)
        T_sol = f.initialiser_profil_sol(T_moy_annuelle=T0, N=13)

        sign_daynight = np.empty(N_steps)
        for k in range(N_steps):
            t_sec = k * lib.dt
            jour_sim = int(t_sec // 86400) + 1
            _, heure_solaire = f.get_time_variables(t_sec, lon_deg)
            sign_daynight[k] = 1.0 if f.cos_incidence(lat_rad, jour_sim, heure_solaire) > 0 else -1.0
        q_latent_smoothed = gaussian_filter1d(q_base * sign_daynight, sigma=3.0, mode="wrap")

        for k in range(N_steps):
            day_of_year, heure_solaire = f.get_time_variables(k * lib.dt, lon_deg)
            jour_sim = int(k * lib.dt // 86400) + 1
            phi_n = lib.P_inc_solar(
                lat_rad, jour_sim, heure_solaire,
                alb_sol_daily[day_of_year], alb_nuages_daily[day_of_year]
            )
            
            # --- CALCUL DE LA CONDUCTION DU SOL DU PAS DE TEMPS ---
            # On fait évoluer la colonne de sol d'un pas dt à partir de la température de surface actuelle T[k]
            T_sol, p_cond = f.calculer_conduction_sol(T[k], T_sol, lib.dt)

            X = T[k]
            for _ in range(8):
                # p_cond intervient directement dans l'évaluation de f_rhs
                F = X - T[k] - lib.dt * f_rhs(X, phi_n, C_const, q_latent_smoothed[k], p_cond)
                dF = 1.0 - lib.dt * (-4.0 * lib.sigma * X**3 / C_const)
                if abs(dF) < 1e-9: break
                X -= F / dF
                if abs(F) < 1e-6: break
            T[k + 1] = X
        return T

    def run_full_hires_simulation(days, stabilize=False):
        """Exécute la simulation pour toute la grille HAUTE RÉSOLUTION."""
        
        print("\n--- Étape 1: Chargement et Suréchantillonnage des Données ---")
        try:
            ALBEDO_DIR = pathlib.Path("modele4/codes python/ressources/albedo")
            monthly_albedo_lowres, LAT_lowres, LON_lowres = f.load_albedo_series(ALBEDO_DIR)
            RZSM_GRID_lowres, RZSM_LAT_lowres, RZSM_LON_lowres = f.load_and_grid_rzsm_data(
                pathlib.Path("modele4/codes python/ressources/Cp_humidity/average_rzsm_tout.csv")
            )
            ceres_clim_lowres = f.load_monthly_cloud_albedo_from_ceres(
                lat_deg=None, lon_deg=None, return_full_map=True
            )
        except (FileNotFoundError, RuntimeError) as e:
            print(f"ERREUR CRITIQUE: Un fichier de ressources est introuvable : {e}")
            sys.exit(1)

        NLAT_HI, NLON_HI = 70, 140
        LAT_HI = np.linspace(LAT_lowres.min(), LAT_lowres.max(), NLAT_HI)
        LON_HI = np.linspace(LON_lowres.min(), LON_lowres.max(), NLON_HI)
        print(f"Grille haute résolution définie : {NLAT_HI}x{NLON_HI} points.")

        print("Pré-calcul des paramètres sur la grille haute résolution...")
        monthly_albedo_hi = np.array([
            upscale_grid(monthly_albedo_lowres[m], LAT_lowres, LON_lowres, LAT_HI, LON_HI)
            for m in range(12)
        ])
        RZSM_GRID_hi = upscale_grid(
            RZSM_GRID_lowres, RZSM_LAT_lowres[:-1], RZSM_LON_lowres[:-1], LAT_HI, LON_HI
        )
        Q_GRID_HI = np.array([[lib.P_em_surf_evap(lat, lon, verbose=False) for lon in LON_HI] for lat in LAT_HI])
        C_GRID_HI = (f.compute_cp_from_rzsm(RZSM_GRID_hi) * 1000.0) * f.RHO_BULK * lib.EPAISSEUR_ACTIVE

        albedo_sol_daily_grid = f.lisser_donnees_annuelles(monthly_albedo_hi, sigma=15.0)
        monthly_cloud_albedo_hi = ceres_clim_lowres.sel(lat=LAT_HI, lon=LON_HI, method="nearest").to_numpy()
        albedo_nuages_daily_grid = f.lisser_donnees_annuelles(monthly_cloud_albedo_hi, sigma=15.0)
        print("--- Pré-calcul terminé ---")


        #début de la boucle spatiale
        result_file = HIRES_STABILIZED_FILE if stabilize else HIRES_ONEYEAR_FILE
        NPY_DIR.mkdir(parents=True, exist_ok=True)
        sim_type = "stabilisée (2 ans)" if stabilize else "rapide (1 an)"
        print(f"\nLancement de la simulation HAUTE RÉSOLUTION {sim_type}...")
        print(f"Les résultats seront sauvegardés dans '{result_file}'")

        N_steps = int(days * 24 * 3600 / lib.dt) + 1
        T_grid = np.zeros((N_steps, NLAT_HI, NLON_HI))

        for i in tqdm(range(NLAT_HI), desc="Progression (latitude)"):
            for j in range(NLON_HI):
                lat, lon = LAT_HI[i], LON_HI[j]
                T0 = 288.15 - 30 * np.sin(np.radians(lat)) ** 2
                
                # Appel de la fonction d'intégration locale couplée
                T_series = integrate_point_temperature(
                    days, np.radians(lat), lon,
                    albedo_sol_daily_grid[:, i, j],
                    albedo_nuages_daily_grid[:, i, j],
                    C_GRID_HI[i, j],
                    Q_GRID_HI[i, j],
                    T0
                )
                T_grid[:, i, j] = T_series

        if stabilize:
            print("Simulation terminée. Extraction de la deuxième année...")
            steps_per_year = int(365 * 24 * 3600 / lib.dt)
            T_grid = T_grid[steps_per_year:, :, :]

        print(f"Sauvegarde des résultats dans '{result_file}'...")
        np.save(result_file, T_grid)
        return T_grid

    # ────────────────────────────────────────────────
    # EXÉCUTION PRINCIPALE ET VISUALISATION 2D
    # ────────────────────────────────────────────────
    if __name__ == "__main__":
        target_file = None
        run_sim = False
        sim_days = 0
        stabilize = False

        if HIRES_STABILIZED_FILE.exists():
            print(f"Un fichier de simulation HI-RES stabilisée a été trouvé ('{HIRES_STABILIZED_FILE.name}').")
            choice = input("Voulez-vous le charger (c) ou relancer une simulation (r) ? [c/r]: ").lower()
            if choice == 'c': target_file = HIRES_STABILIZED_FILE
            else: run_sim = True
        elif HIRES_ONEYEAR_FILE.exists():
            print(f"Un fichier de simulation HI-RES sur 1 an a été trouvé ('{HIRES_ONEYEAR_FILE.name}').")
            choice = input("Charger ce fichier (c), ou lancer une nouvelle simulation stabilisée (r) ? [c/r]: ").lower()
            if choice == 'c': target_file = HIRES_ONEYEAR_FILE
            else: run_sim = True
        else:
            print("Aucun fichier de simulation HI-RES pré-calculé n'a été trouvé.")
            run_sim = True

        if run_sim and target_file is None:
            choice = input("Quelle simulation lancer ?\n  1. Rapide (1 an)\n  2. Stabilisée (2 ans, recommandé)\nVotre choix [1/2]: ").lower()
            if choice == '2':
                sim_days = 365 * 2
                stabilize = True
            else:
                sim_days = 365
                stabilize = False

        if target_file:
            print(f"Chargement des résultats depuis '{target_file}'...")
            T_grid_all_times = np.load(target_file)
        else:
            T_grid_all_times = run_full_hires_simulation(sim_days, stabilize)

        SIM_DAYS_DISPLAY = T_grid_all_times.shape[0] // int(24 * 3600 / lib.dt)
        plt.close("all")
        fig = plt.figure(figsize=(14, 8))

        if USE_CARTOPY:
            proj = ccrs.PlateCarree()
            ax = plt.axes(projection=proj)
            transform = ccrs.PlateCarree()
        else:
            proj = None
            ax = plt.axes()
            transform = ax.transData

        initial_T_grid = T_grid_all_times[0, :, :]
        im = ax.imshow(
            initial_T_grid - 273.15,
            origin="lower",
            extent=[-180, 180, -90, 90],
            transform=transform,
            cmap="inferno",
            vmin=-50, vmax=50,
            interpolation='bilinear'  # Lissage pour un rendu plus doux
        )

        if USE_CARTOPY:
            ax.coastlines()
            ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
        else:
            ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
            ax.grid(True, linestyle='--', alpha=0.5)

        cb = fig.colorbar(im, ax=ax, orientation="vertical", fraction=0.03, pad=0.04)
        cb.set_label("Température de surface (°C)", fontsize=12)
        plt.subplots_adjust(bottom=0.25, top=0.95)
        title = ax.set_title("Température de surface - Jour 0, Heure 0", fontsize=14)

        ax_slider_day = plt.axes([0.2, 0.1, 0.6, 0.03])
        slider_day = Slider(ax_slider_day, "Jour", 0, SIM_DAYS_DISPLAY - 1, valinit=0, valstep=1)
        ax_slider_hour = plt.axes([0.2, 0.05, 0.6, 0.03])
        slider_hour = Slider(ax_slider_hour, "Heure", 0, 23, valinit=0, valstep=1)

        def _refresh(val):
            day = int(slider_day.val)
            hour = int(slider_hour.val)
            steps_per_day = int(24 * 3600 / lib.dt)
            steps_per_hour = int(3600 / lib.dt)
            time_idx = min(day * steps_per_day + hour * steps_per_hour, T_grid_all_times.shape[0] - 1)
            T_slice = T_grid_all_times[time_idx, :, :]
            im.set_data(T_slice - 273.15)
            title.set_text(f"Température de surface - Jour {day}, Heure {hour}")
            fig.canvas.draw_idle()

        slider_day.on_changed(_refresh)
        slider_hour.on_changed(_refresh)
        _refresh(0)

        print("\nFenêtre de visualisation HAUTE RÉSOLUTION ouverte.")
        plt.show()