import numpy as np

from calcul_section_efficace_CO2_CH4_H2O import (
    calculer_section_CH4,
    calculer_section_CO2,
    calculer_section_H2O,
    calculer_section_O3,
)

from pathlib import Path
chemin = Path(__file__).resolve().parent.parent / "températures_et_concentrations" / "code_H20_CH4_CO2_O3.py"

espace_code_concentrations = {}

exec(
    chemin.read_text(encoding="utf-8"),
    espace_code_concentrations
)

get_gases_ppm = espace_code_concentrations["get_gases_ppm"]

# =============================================================================
# DENSITÉ MOLÉCULAIRE DE L'AIR
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


# =============================================================================
# CONVERSION DES CONCENTRATIONS
# =============================================================================



def convertir_concentrations_en_fractions_molaires(concentrations):
    """
    Convertit les concentrations des gaz, exprimées en ppm,
    en fractions molaires.
    """

    CO2_ppm = concentrations["CO2 de mélange (Proportion)"]
    H2O_ppm = concentrations["H2O de mélange (Proportion)"]
    CH4_ppm = concentrations["CH4 de mélange (Proportion)"]
    O3_ppm = concentrations["O3 de mélange (Proportion)"]

    fractions_molaires = {
        "CO2": CO2_ppm * 1e-6,
        "H2O": H2O_ppm * 1e-6,
        "CH4": CH4_ppm * 1e-6,
        "O3": O3_ppm * 1e-6
    }

    return fractions_molaires


# =============================================================================
# DENSITÉ MOLÉCULAIRE D'UN GAZ
# =============================================================================

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


# =============================================================================
# ÉPAISSEUR OPTIQUE
# =============================================================================

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


# =============================================================================
# ÉMISSIVITÉ
# =============================================================================

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
    altitude_couche_km,
    longueur_onde
):
    """
    Calcule l'émissivité totale d'une seule couche atmosphérique
    en prenant en compte tous les gaz présents.

    Formule :
        emissivite = 1 - exp(-tau_total)

        tau_total = tau_CO2 + tau_H2O + tau_CH4 + tau_O3
    """

    concentrations = get_gases_ppm(altitude_couche_km)

    sections_efficaces = {
        "CO2": calculer_section_CO2(longueur_onde),
        "H2O": calculer_section_H2O(longueur_onde),
        "CH4": calculer_section_CH4(longueur_onde),
        "O3": calculer_section_O3(longueur_onde),
    }

    fractions_molaires = convertir_concentrations_en_fractions_molaires(
        concentrations
    )

    fraction_molaire_CO2 = fractions_molaires["CO2"]
    fraction_molaire_H2O = fractions_molaires["H2O"]
    fraction_molaire_CH4 = fractions_molaires["CH4"]
    fraction_molaire_O3 = fractions_molaires["O3"]

    tau_CO2 = calculer_epaisseur_optique_gaz(
        pression=pression,
        temperature=temperature,
        fraction_molaire_gaz=fraction_molaire_CO2,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_gaz=sections_efficaces["CO2"]
    )

    tau_H2O = calculer_epaisseur_optique_gaz(
        pression=pression,
        temperature=temperature,
        fraction_molaire_gaz=fraction_molaire_H2O,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_gaz=sections_efficaces["H2O"]
    )

    tau_CH4 = calculer_epaisseur_optique_gaz(
        pression=pression,
        temperature=temperature,
        fraction_molaire_gaz=fraction_molaire_CH4,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_gaz=sections_efficaces["CH4"]
    )

    tau_O3 = calculer_epaisseur_optique_gaz(
        pression=pression,
        temperature=temperature,
        fraction_molaire_gaz=fraction_molaire_O3,
        epaisseur_couche=epaisseur_couche,
        section_efficace_absorption_gaz=sections_efficaces["O3"]
    )

    tau_total = (
        tau_CO2
        + tau_H2O
        + tau_CH4
        + tau_O3
    )

    emissivite = calculer_emissivite(tau_total)

    resultats = {
        "emissivite": emissivite,
        "tau_total": tau_total,
        "tau_CO2": tau_CO2,
        "tau_H2O": tau_H2O,
        "tau_CH4": tau_CH4,
        "tau_O3": tau_O3,
        "sections_efficaces": sections_efficaces,
        "concentrations": concentrations,
        "fractions_molaires": fractions_molaires
    }

    return resultats


# =============================================================================
# TEST INDÉPENDANT
# =============================================================================

if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # Paramètres de la couche
    # -------------------------------------------------------------------------

    pression = 101325.0          # Pa
    temperature = 288.0          # K
    epaisseur_couche = 1     # m
    altitude_couche_km = 0    # km
    longueur_onde = 10e-6     # m (10 µm)

    # -------------------------------------------------------------------------
    # Calcul de l'émissivité
    # -------------------------------------------------------------------------

    resultats = calculer_emissivite_une_couche(
        pression=pression,
        temperature=temperature,
        epaisseur_couche=epaisseur_couche,
        altitude_couche_km=altitude_couche_km,
        longueur_onde=longueur_onde
    )

    concentrations = resultats["concentrations"]
    fractions_molaires = resultats["fractions_molaires"]

    # -------------------------------------------------------------------------
    # Affichage des résultats
    # -------------------------------------------------------------------------

    print("=== TEST ÉMISSIVITÉ : UNE SEULE COUCHE ===")
    print(f"Altitude de la couche : {altitude_couche_km:.2f} km")
    print(f"Pression : {pression:.1f} Pa")
    print(f"Température : {temperature:.1f} K")
    print(f"Épaisseur de couche : {epaisseur_couche:.1f} m")
    print(f"Longueur d'onde : {longueur_onde * 1e6:.2f} µm")
    print()

    print("Sections efficaces :")
    print(f"sigma_CO2 : {resultats['sections_efficaces']['CO2']:.6e} m²/molécule")
    print(f"sigma_H2O : {resultats['sections_efficaces']['H2O']:.6e} m²/molécule")
    print(f"sigma_CH4 : {resultats['sections_efficaces']['CH4']:.6e} m²/molécule")
    print(f"sigma_O3  : {resultats['sections_efficaces']['O3']:.6e} m²/molécule")
    print()

    print("Concentrations récupérées :")
    print(f"CO2 : {concentrations['CO2 de mélange (Proportion)']:.6f} ppm")
    print(f"H2O : {concentrations['H2O de mélange (Proportion)']:.6f} ppm")
    print(f"CH4 : {concentrations['CH4 de mélange (Proportion)']:.6f} ppm")
    print(f"O3 : {concentrations['O3 de mélange (Proportion)']:.6f} ppm")
    print()

    print("Fractions molaires :")
    print(f"CO2 : {fractions_molaires['CO2']:.6e}")
    print(f"H2O : {fractions_molaires['H2O']:.6e}")
    print(f"CH4 : {fractions_molaires['CH4']:.6e}")
    print(f"O3 : {fractions_molaires['O3']:.6e}")
    print()

    print("Épaisseurs optiques :")
    print(f"tau_CO2    = {resultats['tau_CO2']:.6e}")
    print(f"tau_H2O    = {resultats['tau_H2O']:.6e}")
    print(f"tau_CH4    = {resultats['tau_CH4']:.6e}")
    print(f"tau_O3     = {resultats['tau_O3']:.6e}")
    print(f"tau_total  = {resultats['tau_total']:.6e}")
    print()

    print(f"Émissivité de la couche = {resultats['emissivite']:.6f}")
