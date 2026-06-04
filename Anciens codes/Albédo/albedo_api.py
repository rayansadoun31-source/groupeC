import requests
def get_albedo_estimation(latitude, longitude, start_date, end_date):
    # URL de l'API NASA POWER
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point"

    # Paramètres de la requête
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP",
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }

    # Effectuer la requête
    response = requests.get(url, params=params)
    data = response.json()

    # Extraire les données de rayonnement solaire
    allsky = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
    clearsky = data['properties']['parameter']['ALLSKY_SFC_SW_UP']

    # Calculer une estimation de l'albédo
    albedo_estimation = {}
    for date in allsky.keys():
        if clearsky[date] != 0:
            albedo_estimation[date] =  (clearsky[date] / allsky[date])
        else:
            albedo_estimation[date] = None

    return albedo_estimation

latitude1 = [27.9878] #Liste des latitudes
longitude1 = [86.9250]
start_date1 = "20220101"
end_date1 = "20231231"

albedoreturn = []

def albedo(latitude, longitude, start_date, end_date):
    for i in range(len(latitude)):
        albedo_data = get_albedo_estimation(latitude[i], longitude[i], start_date, end_date)

        valeurs = []
        # Extraire les valeurs
        for date in albedo_data:
            if albedo_data[date] != None:
                valeurs.append(albedo_data[date])


        # Calculer la somme des valeurs
        somme = sum(valeurs)

        # Calculer le nombre d'éléments
        nombre_elements = len(valeurs)

        # Calculer la moyenne
        albedo_moyen = somme / nombre_elements
        albedoreturn.append(albedo_moyen)

albedo(latitude1, longitude1, start_date1, end_date1)

print(f"La moyenne de l'albédo' est : {albedoreturn}")
