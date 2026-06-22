import csv
from pathlib import Path

import numpy as np

from code4_emissivite_avec_section_eff import (
    calculer_emissivite_une_couche,
    get_gases_ppm,
)


COLONNES = [
    "altitude_km",
    "longueur_onde_um",
    "pression_Pa",
    "temperature_C",
    "temperature_K",
    "epaisseur_couche_m",
    "CO2_ppm",
    "H2O_ppm",
    "CH4_ppm",
    "O3_ppm",
    "sigma_CO2_m2_molecule",
    "sigma_H2O_m2_molecule",
    "sigma_CH4_m2_molecule",
    "sigma_O3_m2_molecule",
    "tau_CO2",
    "tau_H2O",
    "tau_CH4",
    "tau_O3",
    "tau_total",
    "emissivite",
]


def generer_table_emissivite(
    fichier_sortie,
    longueur_onde_min_um=0.0,
    longueur_onde_max_um=20.0,
    pas_longueur_onde_um=0.1,
    altitude_min_km=0,
    altitude_max_km=100,
    pas_altitude_km=1,
    epaisseur_couche_m=1000.0,
):
    """Génère un CSV de l'émissivité spectrale des couches atmosphériques."""

    fichier_sortie = Path(fichier_sortie)
    longueurs_onde_um = np.arange(
        longueur_onde_min_um,
        longueur_onde_max_um + pas_longueur_onde_um / 2,
        pas_longueur_onde_um,
    )
    longueurs_onde_m = longueurs_onde_um * 1e-6
    altitudes_km = range(
        altitude_min_km,
        altitude_max_km + 1,
        pas_altitude_km,
    )

    with fichier_sortie.open("w", newline="", encoding="utf-8") as fichier_csv:
        ecrivain = csv.writer(fichier_csv)
        ecrivain.writerow(COLONNES)

        for altitude_km in altitudes_km:
            profil = get_gases_ppm(altitude_km)
            pression = profil["Pression locale (Pa)"]
            temperature_C = profil["Temperature (°C)"]
            temperature_K = temperature_C + 273.15

            resultats = calculer_emissivite_une_couche(
                pression=pression,
                temperature=temperature_K,
                epaisseur_couche=epaisseur_couche_m,
                altitude_couche_km=altitude_km,
                longueur_onde=longueurs_onde_m,
            )

            concentrations = resultats["concentrations"]
            sections = resultats["sections_efficaces"]

            for indice, longueur_onde_um in enumerate(longueurs_onde_um):
                ecrivain.writerow(
                    [
                        altitude_km,
                        f"{longueur_onde_um:.1f}",
                        f"{pression:.1f}",
                        f"{temperature_C:.2f}",
                        f"{temperature_K:.2f}",
                        f"{epaisseur_couche_m:.1f}",
                        f"{concentrations['CO2 de mélange (Proportion)']:.6f}",
                        f"{concentrations['H2O de mélange (Proportion)']:.6f}",
                        f"{concentrations['CH4 de mélange (Proportion)']:.6f}",
                        f"{concentrations['O3 de mélange (Proportion)']:.6f}",
                        f"{sections['CO2'][indice]:.12e}",
                        f"{sections['H2O'][indice]:.12e}",
                        f"{sections['CH4'][indice]:.12e}",
                        f"{sections['O3'][indice]:.12e}",
                        f"{resultats['tau_CO2'][indice]:.12e}",
                        f"{resultats['tau_H2O'][indice]:.12e}",
                        f"{resultats['tau_CH4'][indice]:.12e}",
                        f"{resultats['tau_O3'][indice]:.12e}",
                        f"{resultats['tau_total'][indice]:.12e}",
                        f"{resultats['emissivite'][indice]:.12e}",
                    ]
                )

    return fichier_sortie


if __name__ == "__main__":
    sortie = Path(__file__).resolve().parent / "table_emissivite_0_20um.csv"
    generer_table_emissivite(sortie)
    print(f"Table générée : {sortie}")
