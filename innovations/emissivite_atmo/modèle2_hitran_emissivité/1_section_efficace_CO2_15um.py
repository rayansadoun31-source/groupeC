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

# Valeurs à comparer. Ces listes peuvent être modifiées librement.
TEMPERATURES_K = [220.0, 260.0, 296.0, 320.0]
PRESSIONS_ATM = [0.2, 0.5, 1.0, 2.0]


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
    """Calcule la section efficace du CO₂ pour une température et une pression."""
    nombres_onde, sections_cm2 = absorptionCoefficient_Voigt(
        SourceTables="CO2",
        WavenumberRange=[nombre_onde_min, nombre_onde_max],
        WavenumberStep=pas_nombre_onde,
        Environment={"T": temperature, "p": pression_atm},
        HITRAN_units=True,
    )

    # Conversion de cm²/molécule en m²/molécule.
    return nombres_onde, sections_cm2 * 1e-4


def initialiser_donnees_hitran(nombre_onde_min=550, nombre_onde_max=800):
    """Sélectionne la base locale et récupère les raies HITRAN du CO₂."""
    db_begin(str(DOSSIER_DONNEES))
    fetch("CO2", 2, 1, nombre_onde_min, nombre_onde_max)


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


def tracer_sections_co2(
    temperatures_k=TEMPERATURES_K,
    pressions_atm=PRESSIONS_ATM,
):
    """Compare la section efficace pour plusieurs températures et pressions."""
    if not temperatures_k or not pressions_atm:
        raise ValueError("Il faut fournir au moins une température et une pression.")

    initialiser_donnees_hitran()
    longueurs_onde_m = np.linspace(12e-6, 18e-6, 3000)
    figure, axes = plt.subplots(
        len(temperatures_k),
        1,
        figsize=(10, 3.5 * len(temperatures_k)),
        sharex=True,
        sharey=True,
        squeeze=False,
    )

    for axe, temperature_k in zip(axes[:, 0], temperatures_k):
        for pression_atm in pressions_atm:
            nombres_onde, sections_co2 = charger_section_co2(
                temperature=temperature_k,
                pression_atm=pression_atm,
            )
            sections_interpolees = calculer_section_co2(
                longueurs_onde_m,
                nombres_onde,
                sections_co2,
            )
            axe.plot(
                longueurs_onde_m * 1e6,
                sections_interpolees,
                label=f"p = {pression_atm:g} atm",
            )

        axe.set_title(f"T = {temperature_k:g} K")
        axe.set_ylabel("Section efficace (m²/molécule)")
        axe.grid(alpha=0.3)
        axe.legend()

    axes[-1, 0].set_xlabel("Longueur d'onde (µm)")
    figure.suptitle(
        "Section efficace du CO₂ autour de 15 µm — influence de T et p"
    )
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    tracer_sections_co2()
