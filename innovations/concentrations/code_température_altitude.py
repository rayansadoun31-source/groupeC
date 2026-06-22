import math
# données prises dans le modèle de l'athmosphere standard international 

def temperature_atmosphere(z):
    if 0 <= z <= 11: 
        return 15 - 6.5 * z # Troposphère : La température chute de 6.5°C par km en partant de 15°C au niveau de la mer.
    elif 11 < z <= 20:
        return -56.5  # Tropopause / Basse Stratosphère : La température stagne à -56.5°C (gradient nul).
    elif 20 < z <= 32:
        return -56.5 + 1.0 * (z - 20) # Stratosphère (couche moyenne) : La température remonte doucement de 1.0°C par km.
    elif 32 < z <= 50:
        return -44.5 + 2.8 * (z - 32) # Stratosphère (couche haute) : Le réchauffement s'accélère à 2.8°C par km (dû à la couche d'ozone).
    elif 50 < z <= 71:
        return 5.9 - 2.8 * (z - 50) # Basse Mésosphère : La température recommence à chuter au rythme de -2.8°C par km.
    elif 71 < z <= 85:
        return -52.9 - 2.0 * (z - 71) # Haute Mésosphère : La baisse de température ralentit à -2.0°C par km jusqu'à la mésopause.
    else:
        return -80.9 + 12.0 * (z - 85) # Thermosphère (au-delà de 85 km) : La température augmente de façon drastique (+12.0°C par km).
