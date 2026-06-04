#Cette librairie propose une convention pour le nom des puissances surfaciques considérées, mais n'a pas vocation à être réutilisée telle quelle.
# conventions:
# lat: float (radian), 0 is at equator, -pi/2 is at south pole, and +pi/2 is at north pole
# long: float (radian), 0 is at greenwich meridiant
# t: float (s), 0 is at 00:00 (greenwich time) january 1, 365*24*60*60 is at the end of the year, (maybe use 365.25? no idea what is best, or maybe use UTC ?)


import numpy as np
import pandas as pd
import numpy as np
from math import sqrt
from datetime import datetime, timedelta

P0 = 1340  # W/m² – zenith irradiance at the top of the atmosphere
PHI = 0.409  # precession angle rad  (23.45 deg)
SIGMA = 5.67e-8  # W/m²K⁴ – Stefan-Boltzmann constant
epsilon = 0.71 #Proportions des rayons infrarouges qui sont effectivement absorbés par l'atmosphère, on considère que le reste est perdu dans le vide intersidéral

# Capacités thermiques (constantes)
capa_glace = 2060
capa_eau = 4185
capa_neige = 2092
capa_desert = 835
capa_foret = 2400
capa_terre = 750

#Fonctions qui servent à déterminer des constantes

# Cache pour stocker les albédos calculés par l'API NASA
albedo_cache = {}


# Fonction annexe utilisée dans la fonction get_nasa_albedo, qui fait appel à l'API de la NASA
def get_albedo_estimation(latitude, longitude, start_date, end_date):
    """Récupère l'estimation d'albédo depuis l'API NASA POWER"""
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"

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
        print(f"Requête API NASA: {url}")
        print(f"Paramètres: {params}")

        response = requests.get(url, params=params, timeout=30)
        print(f"Status code: {response.status_code}")

        if response.status_code != 200:
            print(f"Erreur HTTP: {response.status_code}")
            print(f"Réponse: {response.text[:500]}")
            return None

        data = response.json()
        print("Réponse JSON reçue avec succès")

        # Vérifier la structure de la réponse
        if 'properties' not in data or 'parameter' not in data['properties']:
            print("Structure de réponse inattendue")
            print(f"Clés disponibles: {data.keys()}")
            return None

        # Extraire les données de rayonnement solaire
        parameters = data['properties']['parameter']
        if 'ALLSKY_SFC_SW_DWN' not in parameters or 'ALLSKY_SFC_SW_UP' not in parameters:
            print("Paramètres de rayonnement non trouvés dans la réponse")
            return None

        down_radiation = parameters['ALLSKY_SFC_SW_DWN']
        up_radiation = parameters['ALLSKY_SFC_SW_UP']

        # Calculer l'albédo pour chaque jour
        albedo_estimation = {}
        for date in down_radiation.keys():
            down_val = down_radiation[date]
            up_val = up_radiation[date]

            if down_val and up_val and down_val > 0:
                albedo_val = up_val / down_val
                # Limiter l'albédo entre 0 et 1
                albedo_estimation[date] = max(0, min(1, albedo_val))
            else:
                albedo_estimation[date] = None

        return albedo_estimation

    except requests.RequestException as e:
        print(f"Erreur de requête: {e}")
        return None
    except Exception as e:
        print(f"Erreur lors du traitement: {e}")
        return None


#Fonction à appeler pour avoir l'albedo en un point précis de latitude et de longitude donnée. Fait appel à l'API de la NASA
def get_nasa_albedo(lat, lng, date_debut="2022-01-01", duree_simulation_jours=365):
    """Récupère l'albédo moyen depuis l'API NASA pour une position donnée"""
    # Clé pour le cache
    cache_key = f"{lat},{lng},{date_debut},{duree_simulation_jours}"

    if cache_key in albedo_cache:
        print(f"Albédo trouvé dans le cache: {albedo_cache[cache_key]:.3f}")
        return albedo_cache[cache_key]

    # Limiter les requêtes à 1 an maximum pour éviter les timeouts
    duree_limitee = min(duree_simulation_jours, 365)

    # Convertir les dates au format requis par l'API
    date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin_obj = date_debut_obj + timedelta(days=duree_limitee-1)

    start_date_str = date_debut_obj.strftime("%Y%m%d")
    end_date_str = date_fin_obj.strftime("%Y%m%d")

    print(f"Récupération albédo NASA pour lat={lat}, lng={lng} du {start_date_str} au {end_date_str}")

    # Appel à l'API
    albedo_data = get_albedo_estimation(lat, lng, start_date_str, end_date_str)

    if albedo_data is None:
        print("Échec de récupération des données NASA, utilisation d'une valeur par défaut")
        # Utiliser une valeur par défaut raisonnable
        albedo_defaut = 0.3  # Valeur moyenne pour terre/végétation
        albedo_cache[cache_key] = albedo_defaut
        return albedo_defaut

    # Calculer la moyenne des albédos valides
    valeurs_valides = [v for v in albedo_data.values() if v is not None and 0 <= v <= 1]

    if not valeurs_valides:
        print("Aucune donnée d'albédo valide, utilisation d'une valeur par défaut")
        albedo_defaut = 0.3
        albedo_cache[cache_key] = albedo_defaut
        return albedo_defaut

    albedo_moyen = sum(valeurs_valides) / len(valeurs_valides)
    # Limiter l'albédo entre 0.05 et 0.95 pour éviter les valeurs extrêmes
    albedo_moyen = max(0.05, min(0.95, albedo_moyen))
    print(f"Albédo NASA calculé: {albedo_moyen:.3f} (basé sur {len(valeurs_valides)} mesures)")

    # Mettre en cache
    albedo_cache[cache_key] = albedo_moyen
    return albedo_moyen


#Pour calculer l'albedo en un point de latitude et de longitude données, sans faire d'appel API, juste avec un fichier csv fourni ou rempli avec les données de l'API de la NASA

#Permet de transformer un fichier csv en un tableau dataframe propre, lisible en Python
def charger_donnees_albedo(fichier_csv):
    """
    Charge les données d'albédo depuis le fichier CSV.

    Args:
        fichier_csv (str): Chemin vers le fichier CSV contenant les données d'albédo

    Returns:
        pandas.DataFrame: DataFrame contenant les données d'albédo
    """
    try:
        df = pd.read_csv(fichier_csv)
        # Nettoyer les en-têtes (supprimer les espaces)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Erreur lors du chargement du fichier: {e}")
        return None


#Permet de calculer la distance entre deux points, en considérant la Terre localement plate pour des points assez rapprochés
def distance_euclidienne(lat1, lon1, lat2, lon2):
    """
    Calcule la distance euclidienne entre deux points (approximation simple).
    Pour une précision géographique plus élevée, utilisez la formule de Haversine.

    Args:
        lat1, lon1: Coordonnées du premier point
        lat2, lon2: Coordonnées du second point

    Returns:
        float: Distance euclidienne
    """
    return sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

#Renvoie l'albdedo du point le  plus proche dans notre jeu de données par rapport au point fourni
def obtenir_albedo(latitude, longitude, df_albedo):
    """
    Trouve l'albédo pour des coordonnées données.

    Args:
        latitude (float): Latitude recherchée
        longitude (float): Longitude recherchée
        df_albedo (pandas.DataFrame): DataFrame contenant les données d'albédo
        methode (str): Méthode de recherche ('plus_proche' ou 'interpolation')

    Returns:
        dict: Dictionnaire contenant l'albédo et les métadonnées
              {'albedo': float, 'albedo_std': float, 'distance': float,
               'lat_trouve': float, 'lon_trouve': float, 'points_reussis': int}
        None si aucune donnée n'est trouvée
    """
    if df_albedo is None or df_albedo.empty:
        print("Aucune donnée disponible")
        return None

    # Calculer les distances pour tous les points
    df_albedo = df_albedo.copy()
    df_albedo['distance'] = df_albedo.apply(
        lambda row: distance_euclidienne(latitude, longitude, row['latitude'], row['longitude']),
        axis=1
    )

    # Trouver le point le plus proche
    point_proche = df_albedo.loc[df_albedo['distance'].idxmin()]

    return {
        'albedo': point_proche['albedo'],
        'albedo_std': point_proche['albedo_std'],
        'distance': point_proche['distance'],
        'lat_trouve': point_proche['latitude'],
        'lon_trouve': point_proche['longitude'],
        'points_reussis': point_proche['points_reussis'],
        'points_total': point_proche['points_total']
    }

#Fonction à appeler, qui utilise les trois fonctions précédentes
def rechercher_albedo_simple(latitude, longitude, fichier_csv='albedo_lat_lon_multisampled_3pts.csv'):
    """
    Fonction simplifiée pour rechercher l'albédo.

    Args:
        latitude (float): Latitude recherchée
        longitude (float): Longitude recherchée
        fichier_csv (str): Chemin vers le fichier CSV

    Returns:
        float: Valeur d'albédo du point le plus proche
    """
    df = charger_donnees_albedo(fichier_csv)
    if df is None:
        return None

    resultat = obtenir_albedo(latitude, longitude, df)
    return resultat['albedo'] if resultat else None

#Exemple d'utilisation :
# albedo_simple = rechercher_albedo_simple(0,0)
# print(albedo_simple)


def capacite(lat: float, lng: float, t: float = 0):
    """Capacité thermique massique en fonction de la localisation"""
    if lat >= 65 or lat <= -65:
        return capa_glace
    elif lng >= 160 or lng <= -140:
        return capa_eau
    elif lng <= -120 and lng >= -140 and lat >= -65 and lat <= 50:
        return capa_eau
    elif lng <= -80 and lng >= -120 and lat >= -65 and lat <= 20:
        return capa_eau
    elif lng <= 140 and lng >= -60 and lat >= -65 and lat <= -30:
        return capa_eau
    elif lng <= -60 and lng >= -80 and lat >= 10 and lat <= 40:
        return capa_eau
    elif lng <= 0 and lng >= -60 and lat >= 30 and lat <= 65:
        return capa_eau
    elif lng <= -20 and lng >= -60 and lat >= 10 and lat <= 30:
        return capa_eau
    elif lng <= 10 and lng >= -60 and lat >= 0 and lat <= 10:
        return capa_eau
    elif lng <= 10 and lng >= -40 and lat >= -30 and lat <= 0:
        return capa_eau
    elif lng <= 120 and lng >= 40 and lat >= 10 and lat <= 20:
        return capa_eau
    elif lng <= 100 and lng >= 40 and lat >= -30 and lat <= 10:
        return capa_eau
    elif lng <= 120 and lng >= 100 and lat >= -30 and lat <= -10:
        return capa_eau
    elif lng <= 140 and lng >= 120 and lat >= 0 and lat <= 30:
        return capa_eau
    elif lng <= 160 and lng >= 140 and lat >= 0 and lat <= 60:
        return capa_eau
    elif lng <= -60 and lng >= -80 and lat <= 10 and lat >= 0:
        return capa_foret
    elif lng <= -40 and lng >= -80 and lat <= 0 and lat >= -30:
        return capa_foret
    elif lng <= -60 and lng >= -80 and lat <= -30 and lat >= -65:
        return capa_foret
    elif lng <= 40 and lng >= -20 and lat <= 20 and lat >= -10:
        return capa_foret
    elif lng <= 140 and lng >= 100 and lat <= 40 and lat >= 30:
        return capa_foret
    elif lng <= 120 and lng >= 100 and lat <= 30 and lat >= 0:
        return capa_foret
    elif lng <= 160 and lng >= 100 and lat <= 0 and lat >= -10:
        return capa_foret
    elif lng <= 40 and lng >= 10 and lat <= -10 and lat >= -30:
        return capa_desert
    elif lng <= 60 and lng >= 0 and lat <= 40 and lat >= 20:
        return capa_desert
    elif lng <= 160 and lng >= 120 and lat <= -10 and lat >= -30:
        return capa_desert
    elif lng <= -80 and lng >= -120 and lat <= 50 and lat >= 20:
        return capa_terre
    elif lng <= 140 and lng >= 0 and lat <= 60 and lat >= 30:
        return capa_terre
    elif lng <= 60 and lng >= 40 and lat <= 40 and lat >= 20:
        return capa_terre
    elif lng <= 100 and lng >= 40 and lat <= 40 and lat >= 20:
        return capa_terre
    else:
        return capa_neige



def P_inc_solar(lat:float, lng:float, t:float):
    # Constantes
    S0 = 1361  # Constante solaire en W/m²
    obliquity = np.radians(23.44)  # Inclinaison axe Terre (en radians)

    # Temps
    day = t / 86400  # Nombre de jours écoulés depuis t=0
    hour = (t % 86400) / 3600  # Heure locale approximative

    # Coordonnées en radians
    lat = np.radians(lat)
    lng = np.radians(lng)

    # Angle horaire (rotation de la Terre)
    omega = 2 * np.pi * (t % 86400) / 86400  # angle entre midi local et le moment t

    # Jour de l’année (simplifié)
    n = int(day % 365)

    # Déclinaison solaire (approximation de Cooper)
    delta = np.radians(23.44) * np.sin(2 * np.pi * (284 + n) / 365)

    # Calcul de l'angle zénithal
    cos_theta = (np.sin(lat) * np.sin(delta) +
                 np.cos(lat) * np.cos(delta) * np.cos(omega - lng))

    # Puissance reçue
    if cos_theta > 0:
        return S0 * cos_theta
    else:
        return 0


# Surface
def P_abs_surf_solar(lat: float, long: float, t: float, Pinc: float): ##puissance absorbée par le sol
    AbsSurf = 1 - get_nasa_albedo(lat,lng)
    return AbsSurf * Pinc


def P_em_surf_thermal(lat: float, long: float, t: float, T: float): ##puissance émise par le sol dans les infrarouges
    '''->float'''
    return SIGMA * (T**4)


def P_em_surf_conv(lat: float, long: float, t: float): ##pas existante/ en reflexion
    return 0


def P_em_surf_evap(lat: float, long: float, t: float): ##pas existante
    return 0


# atmosphere
def P_abs_atm_solar(lat: float, long: float, t: float, Pinc: float): ## on considère l'amosphere transparente au visible
    return 0


def P_abs_atm_thermal(lat: float, long: float, t: float, T_T: float): ## puissance abrobé par l'atmosphère dans l'infrarouge
    return (P_em_surf_thermal(lat,lng,t,T_T)*epsilon)


def P_em_atm_thermal_up(lat: float, long: float, t: float, T_atm:float):  ## puissance emise par atmosphère domaine infrarouge dans le vide intersidéral
    '''->float'''
    return epsilon*SIGMA * (T_atm**4)


def P_em_atm_thermal_down(lat: float, long: float, t: float, T_atm:float): ## puissance emise par atmosphère domaine infrarouge vers l'intérieur de la Terre
    '''->float'''
    return epsilon*SIGMA * (T_atm**4)
