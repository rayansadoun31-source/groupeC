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


def get_gases_ppm(z_km):
    # --- 1. Constantes physiques ---
    g = 9.80665  # m/s²
    M = 0.0289644  # kg/mol
    R = 8.31445  # J/mol/K
    P_sol = 101325.0  # Pression de référence au sol (Pa)
    T_sol_K = 288.15  # Température de référence au sol (K)

    # --- Constantes spécifiques aux gaz ---
    co2_base = 425.0  # Proportion de CO2 au sol (ppm)
    ch4_base = 1.9  # Proportion de CH4 au sol (ppm)
    H_ch4 = 25.0  # Hauteur d'échelle pour la décroissance du CH4 (km)

    # --- 2. Données de structure des couches ---
    layers = [0, 11, 20, 32, 50, 71, 85]
    P_bases = [P_sol]
    alphas_km = [-6.5, 0.0, 1.0, 2.8, -2.8, -2.0, 12.0]

    # Génération des pressions aux limites de couches
    for i in range(len(layers) - 1):
        z_start = layers[i]
        z_end = layers[i + 1]
        T0_K = temperature_atmosphere(z_start) + 273.15
        T1_K = temperature_atmosphere(z_end) + 273.15
        alpha = alphas_km[i] / 1000.0
        dz = (z_end - z_start) * 1000.0

        if alpha != 0:
            P_next = P_bases[-1] * math.pow(
                (T1_K / T0_K), (-g * M) / (R * alpha)
            )
        else:
            P_next = P_bases[-1] * math.exp((-g * M * dz) / (R * T0_K))
        P_bases.append(P_next)

    # --- 3. Trouver la couche actuelle ---
    idx = 0
    for i in range(len(layers) - 1):
        if layers[i] <= z_km <= layers[i + 1]:
            idx = i
            break
    if z_km > 85:
        idx = 6

    # --- 4. Calcul de la pression et température locales ---
    z0 = layers[idx]
    P0 = P_bases[idx]
    alpha = alphas_km[idx] / 1000.0
    dz = (z_km - z0) * 1000.0

    T_C = temperature_atmosphere(z_km)
    T_K = T_C + 273.15
    T0_K = temperature_atmosphere(z0) + 273.15

    if alpha != 0:
        P = P0 * math.pow((T_K / T0_K), (-g * M) / (R * alpha))
    else:
        P = P0 * math.exp((-g * M * dz) / (R * T0_K))

    # --- 5. Calcul des concentrations ---

    # --- CO2 ---
    co2_melange = co2_base
    co2_volumique_absolu = co2_base * (P / P_sol) * (T_sol_K / T_K)

    # --- CH4 (Méthane) ---
    if z_km <= 11.0:
        ch4_melange = ch4_base
    else:
        ch4_melange = ch4_base * math.exp(-(z_km - 11.0) / H_ch4)
    ch4_volumique_absolu = ch4_melange * (P / P_sol) * (T_sol_K / T_K)

    # --- O3 (Ozone - ajouté du code 2) ---
    if 15.0 <= z_km <= 35.0:
        o3_melange = 8.0 * math.exp(-(((z_km - 25.0) / 5.0) ** 2))
    else:
        o3_melange = 0.1
    o3_volumique_absolu = o3_melange * (P / P_sol) * (T_sol_K / T_K)

    # --- H2O (Vapeur d'eau) ---
    e_s = 611.2 * math.exp((17.627 * T_C) / (T_C + 243.04))

    if z_km <= 11.0:
        rh = 0.77 * (1.0 - z_km / 12.0)
        h2o_melange = (rh * e_s / P) * 1000000.0
    else:
        h2o_melange = 4.0

    if h2o_melange < 4.0:
        h2o_melange = 4.0

    h2o_volumique_absolu = h2o_melange * (P / P_sol) * (T_sol_K / T_K)

    return {
        "Altitude (km)": z_km,
        "Temperature (°C)": round(T_C, 2),
        "Pression locale (Pa)": round(P, 1),
        # Résultats CO2
        "CO2 de mélange (Proportion)": co2_melange,
        "CO2 Volumique Absolu (Quantité)": round(co2_volumique_absolu, 2),
        # Résultats CH4
        "CH4 de mélange (Proportion)": round(ch4_melange, 4),
        "CH4 Volumique Absolu (Quantité)": round(ch4_volumique_absolu, 4),
        # Résultats O3
        "O3 de mélange (Proportion)": round(o3_melange, 4),
        "O3 Volumique Absolu (Quantité)": round(o3_volumique_absolu, 4),
        # Résultats H2O
        "H2O de mélange (Proportion)": round(h2o_melange, 2),
        "H2O Volumique Absolu (Quantité)": round(h2o_volumique_absolu, 2),
    }
