import numpy as np
from datetime import datetime, timedelta
import requests
import csv
import time
import random

# Cache local
albedo_cache = {}

def get_albedo_estimation(latitude, longitude, start_date, end_date):
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP",
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        down_radiation = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        up_radiation = data['properties']['parameter']['ALLSKY_SFC_SW_UP']

        albedo_estimation = {}
        for date in down_radiation.keys():
            if down_radiation[date] != 0 and down_radiation[date] is not None:
                albedo_estimation[date] = up_radiation[date] / down_radiation[date]
            else:
                albedo_estimation[date] = None

        return albedo_estimation
    except Exception as e:
        print(f"Erreur lors de la récupération des données NASA: {e}")
        return None

def get_nasa_albedo(lat, lng, date_debut="2022-01-01", duree_simulation_jours=365):
    cache_key = f"{lat},{lng},{date_debut},{duree_simulation_jours}"
    if cache_key in albedo_cache:
        return albedo_cache[cache_key]

    date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin_obj = date_debut_obj + timedelta(days=duree_simulation_jours-1)

    start_date_str = date_debut_obj.strftime("%Y%m%d")
    end_date_str = date_fin_obj.strftime("%Y%m%d")

    albedo_data = get_albedo_estimation(lat, lng, start_date_str, end_date_str)

    if albedo_data is None:
        raise Exception("Échec de récupération des données depuis l'API NASA POWER")

    valeurs_valides = [v for v in albedo_data.values() if v is not None and 0 <= v <= 1]

    if not valeurs_valides:
        raise Exception("Aucune donnée d'albédo valide trouvée")

    albedo_moyen = sum(valeurs_valides) / len(valeurs_valides)
    albedo_moyen = max(0, min(1, albedo_moyen))

    albedo_cache[cache_key] = albedo_moyen
    return albedo_moyen

def generate_sampling_points(lat_center, lon_center, step_size, num_samples=4):
    """
    Génère des points d'échantillonnage autour du centre de la cellule
    """
    points = []

    # Point central
    points.append((lat_center, lon_center))

    # Points aux coins de la cellule
    half_step = step_size / 2
    corner_offsets = [
        (-half_step * 0.7, -half_step * 0.7),  # Sud-Ouest
        (-half_step * 0.7, half_step * 0.7),   # Sud-Est
        (half_step * 0.7, -half_step * 0.7),   # Nord-Ouest
        (half_step * 0.7, half_step * 0.7)     # Nord-Est
    ]

    # Sélectionner les points selon num_samples
    if num_samples <= 1:
        return [points[0]]  # Seulement le centre
    elif num_samples <= 5:
        # Prendre le centre + (num_samples-1) coins
        selected_corners = corner_offsets[:num_samples-1]
        for offset in selected_corners:
            points.append((lat_center + offset[0], lon_center + offset[1]))

    return points

def get_robust_albedo(lat_center, lon_center, step_size, date_debut, duree_simulation_jours, num_samples=4, max_retries=2):
    """
    Calcule l'albédo moyen en échantillonnant plusieurs points dans une zone
    """
    sampling_points = generate_sampling_points(lat_center, lon_center, step_size, num_samples)

    albedo_values = []
    failed_attempts = 0

    for lat, lon in sampling_points:
        # Ajouter un petit délai pour éviter de surcharger l'API
        time.sleep(0.1)

        retry_count = 0
        while retry_count <= max_retries:
            try:
                albedo = get_nasa_albedo(lat, lon, date_debut, duree_simulation_jours)
                albedo_values.append(albedo)
                break
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    print(f"[!] Échec pour point lat={lat:.4f}, lon={lon:.4f} après {max_retries} tentatives: {e}")
                    failed_attempts += 1
                else:
                    time.sleep(0.5)  # Attendre avant retry

    if not albedo_values:
        raise Exception(f"Aucune valeur d'albédo récupérée pour {num_samples} points échantillonnés")

    # Calculer la moyenne et les statistiques
    albedo_moyen = sum(albedo_values) / len(albedo_values)
    albedo_std = np.std(albedo_values) if len(albedo_values) > 1 else 0

    print(f"[INFO] Zone lat={lat_center:.2f}, lon={lon_center:.2f}: {len(albedo_values)}/{num_samples} points réussis, "
          f"albédo moyen={albedo_moyen:.4f} (σ={albedo_std:.4f})")

    return {
        'albedo_moyen': albedo_moyen,
        'albedo_std': albedo_std,
        'points_reussis': len(albedo_values),
        'points_total': num_samples
    }

# Paramètres de configuration
STEP_RAD = 0.5
NUM_SAMPLES = 3  # Nombre de points à échantillonner par zone (1-5)
MAX_RETRIES = 2  # Nombre de tentatives en cas d'échec

# 🚀 OPTIMISATIONS POSSIBLES POUR RÉDUIRE LE TEMPS :
# STEP_RAD = 0.2  # Divise par 4 le nombre de cellules (~30min au lieu de 2h20)
# NUM_SAMPLES = 2  # Divise par 2 le temps (~1h10 au lieu de 2h20)
#
# Exemple configuration rapide :
# STEP_RAD = 0.2
# NUM_SAMPLES = 2
# → Temps estimé : ~15-20 minutes

# Paramètres de grille
latitudes = np.arange(-np.pi/2, np.pi/2, STEP_RAD)
longitudes = np.arange(-np.pi, np.pi, STEP_RAD)

# Période
date_debut = "2022-01-01"
duree_simulation_jours = 365

# Stockage des résultats
grid_cells = []
total_cells = len(latitudes) * len(longitudes)
processed_cells = 0

print(f"🚀 Début du traitement de {total_cells} cellules avec {NUM_SAMPLES} échantillons par cellule")
print(f"📊 Estimation: ~{total_cells * NUM_SAMPLES} requêtes API au total")

start_time = time.time()

for i, lat in enumerate(latitudes):
    for j, lon in enumerate(longitudes):
        lat_centre_rad = lat + STEP_RAD / 2
        lon_centre_rad = lon + STEP_RAD / 2

        lat_deg = np.degrees(lat_centre_rad)
        lon_deg = np.degrees(lon_centre_rad)

        try:
            result = get_robust_albedo(
                lat_deg, lon_deg, np.degrees(STEP_RAD),
                date_debut, duree_simulation_jours,
                NUM_SAMPLES, MAX_RETRIES
            )

            grid_cells.append({
                "latitude": round(lat_deg, 4),
                "longitude": round(lon_deg, 4),
                "albedo": round(result['albedo_moyen'], 4),
                "albedo_std": round(result['albedo_std'], 4),
                "points_reussis": result['points_reussis'],
                "points_total": result['points_total']
            })

        except Exception as e:
            print(f"[!] Erreur pour zone lat={lat_deg:.2f}, lon={lon_deg:.2f} : {e}")

        processed_cells += 1

        # Affichage du progrès
        if processed_cells % 50 == 0:
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / processed_cells) * total_cells
            remaining_time = estimated_total_time - elapsed_time

            print(f"📈 Progrès: {processed_cells}/{total_cells} ({100*processed_cells/total_cells:.1f}%) "
                  f"- ETA: {remaining_time/60:.1f} min")

# Sauvegarde dans un fichier CSV avec colonnes supplémentaires
csv_filename = f"albedo_lat_lon_multisampled_{NUM_SAMPLES}pts.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ["latitude", "longitude", "albedo", "albedo_std", "points_reussis", "points_total"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for cell in grid_cells:
        writer.writerow(cell)

elapsed_time = time.time() - start_time
print(f"\n✅ Fichier CSV généré avec {len(grid_cells)} points : {csv_filename}")
print(f"⏱️  Temps total d'exécution: {elapsed_time/60:.1f} minutes")
print(f"📊 Statistiques:")
print(f"   - Points traités avec succès: {len(grid_cells)}/{total_cells}")
print(f"   - Temps moyen par cellule: {elapsed_time/max(1,len(grid_cells)):.1f} secondes")