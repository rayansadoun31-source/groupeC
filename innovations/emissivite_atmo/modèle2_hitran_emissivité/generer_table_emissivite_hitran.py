import csv
from pathlib import Path

import numpy as np

from code_final_emissivite_avec_sections_hitran import (
    calculer_emissivite_une_couche,
    get_gases_ppm,
)


COLONNES = [
    "altitude_km",
    "longueur_onde_um",
    "nombre_onde_cm_1",
    "pression_Pa",
    "epaisseur_couche_m",
    "temperature_K",
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
    "emissivite",
]


def generer_table_emissivite_hitran(
    fichier_sortie,
    longueur_onde_min_um=4.0,
    longueur_onde_max_um=100.0,
    pas_longueur_onde_um=0.1,
    altitude_min_km=0,
    altitude_max_km=100,
    pas_altitude_km=1,
    epaisseur_couche_m=1000.0,
):
    """Génère le CSV de l'émissivité HITRAN des couches atmosphériques."""
    fichier_sortie = Path(fichier_sortie)

    # Le demi-pas permet d'inclure la longueur d'onde maximale dans la grille.
    longueurs_onde_um = np.arange(
        longueur_onde_min_um,
        longueur_onde_max_um + pas_longueur_onde_um / 2,
        pas_longueur_onde_um,
    )
    longueurs_onde_m = longueurs_onde_um * 1e-6
    nombres_onde_cm_1 = 1 / (longueurs_onde_m * 100)

    altitudes_km = range(
        altitude_min_km,
        altitude_max_km + 1,
        pas_altitude_km,
    )
    nombre_altitudes = len(altitudes_km)

    with fichier_sortie.open("w", newline="", encoding="utf-8") as fichier_csv:
        ecrivain = csv.writer(fichier_csv)
        ecrivain.writerow(COLONNES)

        for numero_altitude, altitude_km in enumerate(altitudes_km, start=1):
            profil = get_gases_ppm(altitude_km)
            pression = profil["Pression locale (Pa)"]
            temperature_C = profil["Temperature (°C)"]
            temperature_K = temperature_C + 273.15

            # Calcul de toutes les longueurs d'onde pour cette altitude.
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
                        f"{nombres_onde_cm_1[indice]:.8f}",
                        f"{pression:.6e}",
                        f"{epaisseur_couche_m:.1f}",
                        f"{temperature_K:.2f}",
                        f"{concentrations['CO2 de mélange (Proportion)']:.12e}",
                        f"{concentrations['H2O de mélange (Proportion)']:.12e}",
                        f"{concentrations['CH4 de mélange (Proportion)']:.12e}",
                        f"{concentrations['O3 de mélange (Proportion)']:.12e}",
                        f"{sections['CO2'][indice]:.12e}",
                        f"{sections['H2O'][indice]:.12e}",
                        f"{sections['CH4'][indice]:.12e}",
                        f"{sections['O3'][indice]:.12e}",
                        f"{resultats['tau_CO2'][indice]:.12e}",
                        f"{resultats['tau_H2O'][indice]:.12e}",
                        f"{resultats['tau_CH4'][indice]:.12e}",
                        f"{resultats['tau_O3'][indice]:.12e}",
                        f"{resultats['emissivite'][indice]:.12e}",
                    ]
                )

            # Enregistrement des lignes avant de passer à l'altitude suivante.
            fichier_csv.flush()
            print(
                f"Altitude {altitude_km} km terminée "
                f"({numero_altitude}/{nombre_altitudes})",
                flush=True,
            )

    return fichier_sortie


if __name__ == "__main__":
    sortie = (
        Path(__file__).resolve().parent
        / "table_emissivite_hitran_4_100um_0_100km.csv"
    )
    generer_table_emissivite_hitran(sortie)
    print(f"Table générée : {sortie}")
