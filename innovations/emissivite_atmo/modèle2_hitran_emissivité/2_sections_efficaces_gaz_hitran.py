from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from hapi import absorptionCoefficient_Voigt, db_begin, fetch, select

# Fonctions HAPI utilisées :
# - db_begin : choisit le dossier où lire et enregistrer les données HITRAN.
# - fetch : télécharge les raies d'absorption d'un gaz dans ce dossier.
# - absorptionCoefficient_Voigt : calcule la section efficace du gaz à partir
#   de ces raies. Elle renvoie les nombres d'onde et les sections associées.

# Dossier local dans lequel HAPI enregistre les raies spectrales HITRAN.
DOSSIER_DONNEES = Path(__file__).resolve().parent / "donnees_hitran"

# L'intervalle 4-100 µm correspond à 2500-100 cm⁻¹.
# Relation : nombre d'onde = 1 / longueur d'onde
# Avec λ en mètres : nombre d'onde (cm⁻¹) = 1 / (100 × λ)

LONGUEUR_ONDE_MIN_M = 4e-6
LONGUEUR_ONDE_MAX_M = 100e-6
NOMBRE_ONDE_MIN_CM_1 = 1/(LONGUEUR_ONDE_MAX_M * 100)
NOMBRE_ONDE_MAX_CM_1 = 1/(LONGUEUR_ONDE_MIN_M * 100)


def convertir_lambda_m_en_nombre_onde_cm_1(longueur_onde_m):
    """Convertit une longueur d'onde en m en nombre d'onde en cm⁻¹."""
    return 1 / (longueur_onde_m * 100)


@lru_cache(maxsize=1)
def initialiser_base_hitran():
    """Ouvre une seule fois la base HITRAN locale."""
    db_begin(str(DOSSIER_DONNEES))


@lru_cache(maxsize=None)
def telecharger_raies_gaz(
    nom_table,
    numero_molecule,
    nombre_onde_min,
    nombre_onde_max,
):
    """Télécharge les raies uniquement si la table locale est absente."""
    initialiser_base_hitran()

    fichier_donnees = DOSSIER_DONNEES / f"{nom_table}.data"
    fichier_entete = DOSSIER_DONNEES / f"{nom_table}.header"

    if not fichier_donnees.exists() or not fichier_entete.exists():
        fetch(
            nom_table,
            numero_molecule,
            1,
            nombre_onde_min,
            nombre_onde_max,
        )


@lru_cache(maxsize=8)
def charger_section_gaz(
    nom_table,
    numero_molecule,
    nombre_onde_min=NOMBRE_ONDE_MIN_CM_1,
    nombre_onde_max=NOMBRE_ONDE_MAX_CM_1,
    pas_nombre_onde=0.05,
    temperature=296.0,
    pression_atm=1.0,
):
    """Calcule la section efficace d'un gaz à une pression et une température."""
    # Un résultat déjà calculé avec les mêmes paramètres est réutilisé.
    telecharger_raies_gaz(
        nom_table,
        numero_molecule,
        nombre_onde_min,
        nombre_onde_max,
    )

    nom_table_calcul = nom_table
    if (
        nombre_onde_min > NOMBRE_ONDE_MIN_CM_1
        or nombre_onde_max < NOMBRE_ONDE_MAX_CM_1
    ):
        # HAPI parcourt sinon toutes les raies de la table, même pour une seule
        # longueur d'onde. On garde les raies voisines (marge pour les ailes de
        # Voigt) dans une table en mémoire avant le calcul.
        marge_raies_cm_1 = 25.0
        nom_table_calcul = f"__{nom_table}_plage"
        select(
            nom_table,
            DestinationTableName=nom_table_calcul,
            Conditions=(
                "between",
                "nu",
                nombre_onde_min - marge_raies_cm_1,
                nombre_onde_max + marge_raies_cm_1,
            ),
            Output=False,
        )

    nombres_onde, sections_cm2 = absorptionCoefficient_Voigt(
        SourceTables=nom_table_calcul,
        WavenumberRange=[nombre_onde_min, nombre_onde_max],
        WavenumberStep=pas_nombre_onde,
        Environment={"T": temperature, "p": pression_atm},
        HITRAN_units=True,
    )

    # Conversion de cm²/molécule en m²/molécule.
    sections_m2 = sections_cm2 * 1e-4
    return nombres_onde, sections_m2


def interpoler_section_gaz(grille_longueurs_onde_m, nombres_onde, sections_gaz):
    """Interpole la section efficace aux longueurs d'onde demandées."""
    nombres_onde_demandes = convertir_lambda_m_en_nombre_onde_cm_1(
        grille_longueurs_onde_m
    )

    return np.interp(
        nombres_onde_demandes,
        nombres_onde,
        sections_gaz,
        left=0,
        right=0,
    )


def calculer_sections_gaz(
    nom_table,
    numero_molecule,
    grille_longueurs_onde_m,
    temperature=296.0,
    pression_atm=1.0,
):
    """Calcule et interpole la section efficace d'un gaz."""
    longueurs_onde_m = np.asarray(grille_longueurs_onde_m)
    if (
        longueurs_onde_m.size == 0
        or not np.all(np.isfinite(longueurs_onde_m))
        or np.any(longueurs_onde_m <= 0)
    ):
        raise ValueError("Les longueurs d'onde doivent être strictement positives.")

    nombres_onde_demandes = np.asarray(
        convertir_lambda_m_en_nombre_onde_cm_1(longueurs_onde_m)
    )

    # Ne calcule que la portion du spectre demandée. Pour un appel ponctuel
    # (par exemple à 10 µm), cela évite de reconstruire inutilement toute la
    # grille 4-100 µm. Une marge conserve assez de points pour l'interpolation.
    marge_cm_1 = 0.1
    nombre_onde_min = max(
        NOMBRE_ONDE_MIN_CM_1,
        float(np.min(nombres_onde_demandes)) - marge_cm_1,
    )
    nombre_onde_max = min(
        NOMBRE_ONDE_MAX_CM_1,
        float(np.max(nombres_onde_demandes)) + marge_cm_1,
    )
    if nombre_onde_min >= nombre_onde_max:
        raise ValueError("Les longueurs d'onde doivent être comprises entre 4 et 100 µm.")

    nombres_onde, sections_gaz = charger_section_gaz(
        nom_table,
        numero_molecule,
        nombre_onde_min=nombre_onde_min,
        nombre_onde_max=nombre_onde_max,
        temperature=temperature,
        pression_atm=pression_atm,
    )

    sections_interpolees = interpoler_section_gaz(
        grille_longueurs_onde_m,
        nombres_onde,
        sections_gaz,
    )

    return sections_interpolees


def tracer_sections_des_quatre_gaz():
    """Trace les sections efficaces entre 4 et 100 µm."""
    grille_longueurs_onde_m = np.linspace(
        LONGUEUR_ONDE_MIN_M,
        LONGUEUR_ONDE_MAX_M,
        20_000,
    )
    sections_co2 = calculer_sections_gaz("CO2", 2, grille_longueurs_onde_m)
    sections_ch4 = calculer_sections_gaz("CH4", 6, grille_longueurs_onde_m)
    sections_o3 = calculer_sections_gaz("O3", 3, grille_longueurs_onde_m)
    sections_h2o = calculer_sections_gaz("H2O", 1, grille_longueurs_onde_m)

    sections_par_gaz = {
        "CO₂": sections_co2,
        "CH₄": sections_ch4,
        "O₃": sections_o3,
        "H₂O": sections_h2o,
    }

    figure, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    axes = axes.flatten()

    for axe, resultat_gaz in zip(axes, sections_par_gaz.items()):
        nom_gaz, sections = resultat_gaz
        axe.plot(grille_longueurs_onde_m * 1e6, sections)
        axe.set_title(nom_gaz)
        axe.set_ylabel("Section efficace (m²/molécule)")
        axe.grid()

    axes[2].set_xlabel("Longueur d'onde (µm)")
    axes[3].set_xlabel("Longueur d'onde (µm)")
    figure.suptitle("Sections efficaces HITRAN entre 4 et 100 µm")
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    tracer_sections_des_quatre_gaz()
