import numpy as np

# =============================================================================
# ÉMISSIVITÉ D'UNE SEULE COUCHE ATMOSPHÉRIQUE
# Formulation : tau = sigma * n * dz
# =============================================================================

# =============================================================================
# CONSTANTES GLOBALES
# =============================================================================

CO2_ppm = 415.0
CH4_ppm = 1.9
fraction_molaire_H2O = 0.01

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
    epaisseur_couche
):
    """
    Calcule l'émissivité totale d'une seule couche atmosphérique en prenant en compte tous les gaz présents.

    Formule :
        emissivite = 1 - exp(-tau_total)
        tau_total = tau_CO2 + tau_H2O + tau_CH4
    """

    fraction_molaire_CO2 = convertir_ppm_en_fraction_molaire(CO2_ppm)
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

    return emissivite, tau_total, tau_CO2, tau_H2O, tau_CH4


# =============================================================================
# TEST INDÉPENDANT
# =============================================================================

if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # Paramètres de la couche
    # -------------------------------------------------------------------------

    pression = 101325.0          # Pa
    temperature = 288.0          # K
    epaisseur_couche = 1000.0    # m

    # -------------------------------------------------------------------------
    # Fractions molaires des gaz
    # -------------------------------------------------------------------------

    fraction_molaire_CO2 = convertir_ppm_en_fraction_molaire(CO2_ppm)
    fraction_molaire_CH4 = convertir_ppm_en_fraction_molaire(CH4_ppm)

    # -------------------------------------------------------------------------
    # Calcul de l'émissivité
    # -------------------------------------------------------------------------

    emissivite, tau_total, tau_CO2, tau_H2O, tau_CH4 = calculer_emissivite_une_couche(
        pression=pression,
        temperature=temperature,
        epaisseur_couche=epaisseur_couche
    )

    # -------------------------------------------------------------------------
    # Affichage des résultats
    # -------------------------------------------------------------------------

    print("=== TEST ÉMISSIVITÉ : UNE SEULE COUCHE ===")
    print(f"Pression : {pression:.1f} Pa")
    print(f"Température : {temperature:.1f} K")
    print(f"Épaisseur de couche : {epaisseur_couche:.1f} m")
    print()

    print("Fractions molaires :")
    print(f"CO2 : {CO2_ppm:.1f} ppm = {fraction_molaire_CO2:.6e}")
    print(f"H2O : {fraction_molaire_H2O:.6e}")
    print(f"CH4 : {CH4_ppm:.1f} ppm = {fraction_molaire_CH4:.6e}")
    print()

    print("Épaisseurs optiques :")
    print(f"tau_CO2    = {tau_CO2:.6e}")
    print(f"tau_H2O    = {tau_H2O:.6e}")
    print(f"tau_CH4    = {tau_CH4:.6e}")
    print(f"tau_total  = {tau_total:.6e}")
    print()

    print(f"Émissivité de la couche = {emissivite:.6f}")