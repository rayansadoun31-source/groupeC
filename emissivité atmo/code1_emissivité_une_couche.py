import numpy as np

# =============================================================================
# ÉMISSIVITÉ D'UNE SEULE COUCHE ATMOSPHÉRIQUE
# Formulation : tau = sigma * n * dz
# =============================================================================

def calculer_densite_moleculaire_air(pression, temperature):
    """
    Formule :
        n_air = P / (kB * T)

    en nb de molécules d'air par m^3
    """

    kB = 1.380649e-23  # constante de Boltzmann, en J/K

    densite_air = pression / (kB * temperature)

    return densite_air


def calculer_densite_moleculaire_CO2(pression, temperature, concentration_CO2_ppm):
    """
    Formule :
        n_CO2 = x_CO2 * n_air

    avec la fraction molaire du CO2 :
        x_CO2 = concentration_CO2_ppm * 1e-6
    """

    densite_air = calculer_densite_moleculaire_air(
        pression=pression,
        temperature=temperature
    )

    fraction_CO2 = concentration_CO2_ppm * 1e-6

    densite_CO2 = fraction_CO2 * densite_air

    return densite_CO2


def calculer_epaisseur_optique_CO2(
    pression,
    temperature,
    concentration_CO2_ppm,
    epaisseur_couche,
    section_efficace_absorption_CO2
):
    """
    Formule :
        tau_CO2 = sigma_CO2 * n_CO2 * dz
    
    avec sigma_CO2 la section efficace d'absoption du CO2
    """

    densite_CO2 = calculer_densite_moleculaire_CO2(
        pression=pression,
        temperature=temperature,
        concentration_CO2_ppm=concentration_CO2_ppm
    )

    epaisseur_optique_CO2 = (
        section_efficace_absorption_CO2
        * densite_CO2
        * epaisseur_couche
    )

    return epaisseur_optique_CO2


def calculer_emissivite(epaisseur_optique):
    """
    Formule :
        epsilon = 1 - exp(-tau)
    """

    emissivite = 1.0 - np.exp(-epaisseur_optique)

    return emissivite


def calculer_emissivite_une_couche(
    pression,
    temperature,
    concentration_CO2_ppm,
    epaisseur_couche,
    section_efficace_absorption_CO2
):
    """
    Calcule l'émissivité totale d'une seule couche atmosphérique en prenant en compte plus tard les autres gaz présents.
    d'où : 
    
        tau_total = tau_CO2 (+ plus tard : H20 et CH4)
        emissivite = 1 - exp(-tau_total)
    """

    tau_CO2 = calculer_epaisseur_optique_CO2(
        pression=pression,
        temperature=temperature,
        concentration_CO2_ppm=concentration_CO2_ppm,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_CO2=section_efficace_absorption_CO2
    )

    tau_total = tau_CO2

    emissivite = calculer_emissivite(tau_total)

    return emissivite, tau_total, tau_CO2


# =============================================================================
# TEST INDÉPENDANT
# =============================================================================

if __name__ == "__main__":

    # Paramètres de la couche
    pression = 101325.0          # Pa
    temperature = 288.0          # KÚ
    concentration_CO2_ppm = 415.0
    epaisseur_couche = 100.0    # m

    # Coefficient effectif à choisir/calibrer
    # Unité : m^2 par molécule
    section_efficace_absorption_CO2 = 1e-25

    emissivite, tau_total, tau_CO2 = calculer_emissivite_une_couche(
        pression=pression,
        temperature=temperature,
        concentration_CO2_ppm=concentration_CO2_ppm,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_CO2=section_efficace_absorption_CO2
    )

    print("=== TEST ÉMISSIVITÉ : UNE SEULE COUCHE ===")
    print(f"Pression : {pression:.1f} Pa")
    print(f"Température : {temperature:.1f} K")
    print(f"CO2 : {concentration_CO2_ppm:.1f} ppm")
    print(f"Épaisseur de couche : {epaisseur_couche:.1f} m")
    print()
    print(f"tau_CO2 = {tau_CO2:.6f}")
    print(f"tau_total = {tau_total:.6f}")
    print(f"émissivité = {emissivite:.6f}")
    