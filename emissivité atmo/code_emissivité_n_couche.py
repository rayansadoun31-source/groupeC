import numpy as np

# =============================================================================
# ÉMISSIVITÉ D'UNE SEULE COUCHE ATMOSPHÉRIQUE
# Formulation : tau = sigma * n * dz
# =============================================================================

def calculer_densite_moleculaire_air(pression, temperature):
    """
    Formule :
        n_air = P / (kB * T)

    Résultat :
        densité moléculaire de l'air en molécules/m^3
    """

    kB = 1.380649e-23  # constante de Boltzmann, en J/K

    densite_air = pression / (kB * temperature)

    return densite_air


def convertir_ppm_en_fraction_molaire(valeur_ppm):
    """
    Convertit une valeur exprimée en ppm en fraction molaire.

    Exemple :
        415 ppm -> 415e-6
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
    gaz_absorbants,
    epaisseur_optique_nuages=0.0
):
    """
    Calcule l'émissivité totale d'une seule couche atmosphérique.

    Le dictionnaire gaz_absorbants contient les gaz pris en compte.

    Exemple :
        gaz_absorbants = {
            "CO2": {
                "fraction_molaire": ...,
                "section_efficace_absorption": ...
            },
            "H2O": {
                "fraction_molaire": ...,
                "section_efficace_absorption": ...
            },
            "CH4": {
                "fraction_molaire": ...,
                "section_efficace_absorption": ...
            }
        }

    Formule :
        tau_total = tau_CO2 + tau_H2O + tau_CH4 + tau_nuages

    puis :
        emissivite = 1 - exp(-tau_total)
    """

    epaisseurs_optiques_gaz = {}

    tau_total = 0.0

    for nom_gaz, donnees_gaz in gaz_absorbants.items():

        fraction_molaire_gaz = donnees_gaz["fraction_molaire"]
        section_efficace_absorption_gaz = donnees_gaz["section_efficace_absorption"]

        tau_gaz = calculer_epaisseur_optique_gaz(
            pression=pression,
            temperature=temperature,
            fraction_molaire_gaz=fraction_molaire_gaz,
            epaisseur_couche=epaisseur_couche,
            section_efficace_absorption_gaz=section_efficace_absorption_gaz
        )

        epaisseurs_optiques_gaz[nom_gaz] = tau_gaz
        tau_total += tau_gaz

    tau_total += epaisseur_optique_nuages

    emissivite = calculer_emissivite(tau_total)

    return emissivite, tau_total, epaisseurs_optiques_gaz


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

    CO2_ppm = 415.0
    CH4_ppm = 1.9

    fraction_molaire_CO2 = convertir_ppm_en_fraction_molaire(CO2_ppm)
    fraction_molaire_CH4 = convertir_ppm_en_fraction_molaire(CH4_ppm)

    # Pour la vapeur d'eau, on donne directement une fraction molaire.
    # Exemple : 0.01 = 1 % de vapeur d'eau.
    fraction_molaire_H2O = 0.01

    # -------------------------------------------------------------------------
    # Sections efficaces d'absorption
    # À choisir ou calibrer selon le modèle
    # Unité : m^2/molécule
    # -------------------------------------------------------------------------

    section_efficace_absorption_CO2 = 1e-25
    section_efficace_absorption_H2O = 1e-25
    section_efficace_absorption_CH4 = 1e-25

    # -------------------------------------------------------------------------
    # Dictionnaire des gaz absorbants
    # -------------------------------------------------------------------------

    gaz_absorbants = {
        "CO2": {
            "fraction_molaire": fraction_molaire_CO2,
            "section_efficace_absorption": section_efficace_absorption_CO2
        },
        "H2O": {
            "fraction_molaire": fraction_molaire_H2O,
            "section_efficace_absorption": section_efficace_absorption_H2O
        },
        "CH4": {
            "fraction_molaire": fraction_molaire_CH4,
            "section_efficace_absorption": section_efficace_absorption_CH4
        }
    }

    # -------------------------------------------------------------------------
    # Calcul de l'émissivité
    # -------------------------------------------------------------------------

    emissivite, tau_total, epaisseurs_optiques_gaz = calculer_emissivite_une_couche(
        pression=pression,
        temperature=temperature,
        epaisseur_couche=epaisseur_couche,
        gaz_absorbants=gaz_absorbants,
        epaisseur_optique_nuages=0.0
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
    for nom_gaz, tau_gaz in epaisseurs_optiques_gaz.items():
        print(f"tau_{nom_gaz} = {tau_gaz:.6e}")

    print(f"tau_total = {tau_total:.6e}")
    print()

    print(f"Émissivité de la couche = {emissivite:.6f}")