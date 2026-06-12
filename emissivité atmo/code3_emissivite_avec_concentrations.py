import numpy as np

from code_H20_CH4_CO2 import get_gases_ppm

# =============================================================================
# CONSTANTES ADMISES
# =============================================================================

section_efficace_absorption_CO2 = 1e-25
section_efficace_absorption_H2O = 1e-25
section_efficace_absorption_CH4 = 1e-25


def calculer_densite_moleculaire_air(pression, temperature):
    """
    Formule :
        n_air = P / (kB * T)

    en nb de molécules d'air par m^3
    """

    kB = 1.380649e-23  # constante de Boltzmann, en J/K

    densite_air = pression / (kB * temperature)

    return densite_air


def convertir_ppm_en_fraction_molaire(valeur_ppm):
    """
    Convertit une valeur exprimée en ppm en fraction molaire.
    """

    fraction_molaire = valeur_ppm * 1e-6

    return fraction_molaire


def calculer_densite_moleculaire_gaz(
    pression,
    temperature,
    fraction_molaire_gaz
):
    """
    Calcule la densité moléculaire d'un gaz quelconque.

    Formule :
        n_gaz = x_gaz * n_air

    avec :
        x_gaz : fraction molaire du gaz
        n_air : densité moléculaire totale de l'air
    """

    densite_air = calculer_densite_moleculaire_air(
        pression=pression,
        temperature=temperature
    )

    densite_gaz = fraction_molaire_gaz * densite_air

    return densite_gaz


def calculer_epaisseur_optique_gaz(
    pression,
    temperature,
    fraction_molaire_gaz,
    epaisseur_couche,
    section_efficace_absorption_gaz
):
    """
    Calcule l'épaisseur optique d'un gaz quelconque.

    Formule :
        tau_gaz = sigma_gaz * n_gaz * dz

    avec :
        sigma_gaz : section efficace d'absorption du gaz en m^2/molécule
        n_gaz : densité moléculaire du gaz en molécules/m^3
        dz : épaisseur de la couche en m
    """

    densite_gaz = calculer_densite_moleculaire_gaz(
        pression=pression,
        temperature=temperature,
        fraction_molaire_gaz=fraction_molaire_gaz
    )

    epaisseur_optique_gaz = (
        section_efficace_absorption_gaz
        * densite_gaz
        * epaisseur_couche
    )

    return epaisseur_optique_gaz


def calculer_emissivite(epaisseur_optique):
    """
    Convertit une épaisseur optique tau en émissivité epsilon.

    Formule :
        epsilon = 1 - exp(-tau)
    """

    emissivite = 1.0 - np.exp(-epaisseur_optique)

    return emissivite


def calculer_emissivite_une_couche(
    pression,
    temperature,
    epaisseur_couche,
    altitude_couche_km
):
    """
    Calcule l'émissivité totale d'une seule couche atmosphérique en prenant en compte tous les gaz présents.

    Formule :
        emissivite = 1 - exp(-tau_total)
        tau_total = tau_CO2 + tau_H2O + tau_CH4
    """

    concentrations = get_gases_ppm(altitude_couche_km)

    CO2_ppm = concentrations["CO2 de mélange (Proportion)"]
    H2O_ppm = concentrations["H2O de mélange (Proportion)"]
    CH4_ppm = concentrations["CH4 de mélange (Proportion)"]

    fraction_molaire_CO2 = convertir_ppm_en_fraction_molaire(CO2_ppm)
    fraction_molaire_H2O = convertir_ppm_en_fraction_molaire(H2O_ppm)
    fraction_molaire_CH4 = convertir_ppm_en_fraction_molaire(CH4_ppm)

    tau_CO2 = calculer_epaisseur_optique_gaz(
        pression=pression,
        temperature=temperature,
        fraction_molaire_gaz=fraction_molaire_CO2,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_gaz=section_efficace_absorption_CO2
    )

    tau_H2O = calculer_epaisseur_optique_gaz(
        pression=pression,
        temperature=temperature,
        fraction_molaire_gaz=fraction_molaire_H2O,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_gaz=section_efficace_absorption_H2O
    )

    tau_CH4 = calculer_epaisseur_optique_gaz(
        pression=pression,
        temperature=temperature,
        fraction_molaire_gaz=fraction_molaire_CH4,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_gaz=section_efficace_absorption_CH4
    )

    tau_total = (
        tau_CO2
        + tau_H2O
        + tau_CH4
    )

    emissivite = calculer_emissivite(tau_total)

    return emissivite, tau_total, tau_CO2, tau_H2O, tau_CH4, concentrations


# =============================================================================
# TEST INDÉPENDANT
# =============================================================================

if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # Paramètres de la couche
    # -------------------------------------------------------------------------

    pression = 101325.0          # Pa
    temperature = 288.0          # K
    epaisseur_couche = 100.0    # m
    altitude_couche_km = 0.0     # km

    # -------------------------------------------------------------------------
    # Calcul de l'émissivité
    # -------------------------------------------------------------------------

    emissivite, tau_total, tau_CO2, tau_H2O, tau_CH4, concentrations = calculer_emissivite_une_couche(
        pression=pression,
        temperature=temperature,
        epaisseur_couche=epaisseur_couche,
        altitude_couche_km=altitude_couche_km
    )
     
    # -------------------------------------------------------------------------
    # Affichage des résultats
    # -------------------------------------------------------------------------

    print("=== TEST ÉMISSIVITÉ : UNE SEULE COUCHE ===")
    print(f"Altitude de la couche : {altitude_couche_km:.2f} km")
    print(f"Pression : {pression:.1f} Pa")
    print(f"Température : {temperature:.1f} K")
    print(f"Épaisseur de couche : {epaisseur_couche:.1f} m")
    print()

    print("Concentrations récupérées :")
    print(f"CO2 : {concentrations['CO2 de mélange (Proportion)']:.6f} ppm")
    print(f"H2O : {concentrations['H2O de mélange (Proportion)']:.6f} ppm")
    print(f"CH4 : {concentrations['CH4 de mélange (Proportion)']:.6f} ppm")
    print()

    print("Épaisseurs optiques :")
    print(f"tau_CO2    = {tau_CO2:.6e}")
    print(f"tau_H2O    = {tau_H2O:.6e}")
    print(f"tau_CH4    = {tau_CH4:.6e}")
    print(f"tau_total  = {tau_total:.6e}")
    print()

    print(f"Émissivité de la couche = {emissivite:.6f}") 
    
