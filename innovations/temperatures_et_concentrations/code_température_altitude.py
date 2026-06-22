import math


def temperature_atmosphere(z):
    if 0 <= z <= 11:
        return 15 - 6.5 * z
    elif 11 < z <= 20:
        return -56.5
    elif 20 < z <= 32:
        return -56.5 + 1.0 * (z - 20)
    elif 32 < z <= 50:
        return -44.5 + 2.8 * (z - 32)
    elif 50 < z <= 71:
        return 5.9 - 2.8 * (z - 50)
    elif 71 < z <= 85:
        return -52.9 - 2.0 * (z - 71)
    else:
        return -80.9 + 12.0 * (z - 85)