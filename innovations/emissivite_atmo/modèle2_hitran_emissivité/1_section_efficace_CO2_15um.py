from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from hapi import absorptionCoefficient_Voigt, db_begin, fetch

# Fonctions HAPI utilisées :
# - db_begin : choisit le dossier où lire et enregistrer les données HITRAN.
# - fetch : télécharge les raies d'absorption du CO2 dans ce dossier.
# - absorptionCoefficient_Voigt : calcule la section efficace du CO2 à partir
#   de ces raies. Elle renvoie les nombres d'onde et les sections associées.

# Dossier local dans lequel HAPI enregistre les raies spectrales HITRAN.
DOSSIER_DONNEES = Path(__file__).resolve().parent / "donnees_hitran"


def convertir_lambda_m_en_nombre_onde_cm_1(longueur_onde_m):
    """Convertit une longueur d'onde en m en nombre d'onde en cm-1."""
    return 1 / (longueur_onde_m * 100)


def charger_section_co2(
    nombre_onde_min=550,
    nombre_onde_max=800,
    pas_nombre_onde=0.05,
    temperature=296.0,
    pression_atm=1.0,
):
    """Télécharge les raies du CO2."""
    db_begin(str(DOSSIER_DONNEES))
    fetch("CO2_15um", 2, 1, nombre_onde_min, nombre_onde_max)

    """Calcule la section efficace."""
    nombres_onde, sections_cm2 = absorptionCoefficient_Voigt(
        SourceTables="CO2_15um",
        WavenumberRange=[nombre_onde_min, nombre_onde_max],
        WavenumberStep=pas_nombre_onde,
        Environment={"T": temperature, "p": pression_atm},
        HITRAN_units=True,
    )

    # Conversion de cm²/molécule en m²/molécule.
    return nombres_onde, sections_cm2 * 1e-4


def calculer_section_co2(longueurs_onde_m, nombres_onde, sections_co2):
    """Interpole la section efficace aux longueurs d'onde demandées."""
    nombres_onde_demandes = convertir_lambda_m_en_nombre_onde_cm_1(
        longueurs_onde_m
    )
    return np.interp(
        nombres_onde_demandes,
        nombres_onde,
        sections_co2,
        left=0,
        right=0,
    )


def tracer_section_co2():
    """Calcule et affiche la section efficace du CO₂ entre 12 et 18 µm."""
    nombres_onde, sections_co2 = charger_section_co2()
    longueurs_onde_m = np.linspace(12e-6, 18e-6, 3000)
    sections_interpolees = calculer_section_co2(
        longueurs_onde_m, nombres_onde, sections_co2
    )

    plt.plot(longueurs_onde_m * 1e6, sections_interpolees)
    plt.xlabel("Longueur d'onde (µm)")
    plt.ylabel("Section efficace CO₂ (m²/molécule)")
    plt.title("Section efficace du CO₂ autour de 15 µm — HITRAN/HAPI")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    tracer_section_co2()
