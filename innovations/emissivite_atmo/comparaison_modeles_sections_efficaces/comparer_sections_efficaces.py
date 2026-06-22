"""Compare les sections efficaces des modèles empirique et HITRAN.

Le script crée un graphique par gaz (CO2, CH4, H2O et O3). La vue
principale couvre 4-100 µm et un encart montre la zone 4-20 µm. Les deux
axes verticaux restent linéaires.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np


DOSSIER_COMPARAISON = Path(__file__).resolve().parent
DOSSIER_PROJET = DOSSIER_COMPARAISON.parent
DOSSIER_EMPIRIQUE = DOSSIER_PROJET / "modèle1_empirique_emissivité"
DOSSIER_HITRAN = DOSSIER_PROJET / "modèle2_hitran_emissivité"
DOSSIER_SORTIE = DOSSIER_COMPARAISON

TEMPERATURE_K = 296.0
PRESSION_ATM = 1.0
PLAGE_COMPLETE_UM = (4.0, 100.0)
PLAGE_ZOOM_UM = (4.0, 20.0)


def charger_module(nom, chemin):
    """Charge un fichier Python dont le nom n'est pas importable directement."""
    specification = spec_from_file_location(nom, chemin)
    if specification is None or specification.loader is None:
        raise ImportError(f"Impossible de charger le module {chemin}")

    module = module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


# Le module empirique importe un autre fichier situé dans son propre dossier.
sys.path.insert(0, str(DOSSIER_EMPIRIQUE))
modele_empirique = charger_module(
    "sections_empiriques",
    DOSSIER_EMPIRIQUE / "calcul_section_efficace_CO2_CH4_H2O.py",
)
modele_hitran = charger_module(
    "sections_hitran",
    DOSSIER_HITRAN / "2_sections_efficaces_gaz_hitran.py",
)


GAZ = {
    "CO2": {
        "nom_affiche": "CO₂",
        "numero_hitran": 2,
        "fonction_empirique": modele_empirique.calculer_section_CO2,
    },
    "CH4": {
        "nom_affiche": "CH₄",
        "numero_hitran": 6,
        "fonction_empirique": modele_empirique.calculer_section_CH4,
    },
    "H2O": {
        "nom_affiche": "H₂O",
        "numero_hitran": 1,
        "fonction_empirique": modele_empirique.calculer_section_H2O,
    },
    "O3": {
        "nom_affiche": "O₃",
        "numero_hitran": 3,
        "fonction_empirique": modele_empirique.calculer_section_O3,
    },
}


def calculer_courbes(nom_table, numero_hitran, fonction_empirique):
    """Calcule les deux sections sur la grille spectrale native de HITRAN."""
    nombres_onde, sections_hitran = modele_hitran.charger_section_gaz(
        nom_table,
        numero_hitran,
        temperature=TEMPERATURE_K,
        pression_atm=PRESSION_ATM,
    )

    longueurs_onde_m = 1 / (100 * nombres_onde)
    longueurs_onde_um = longueurs_onde_m * 1e6
    sections_empiriques = fonction_empirique(longueurs_onde_m)

    # HAPI renvoie les nombres d'onde croissants, donc les longueurs d'onde
    # décroissantes. On inverse les tableaux pour tracer de 4 vers 100 µm.
    return (
        longueurs_onde_um[::-1],
        sections_empiriques[::-1],
        sections_hitran[::-1],
    )


def tracer_courbes(axe, longueurs_um, empirique, hitran):
    """Trace les deux modèles sur un axe Matplotlib."""
    axe.plot(
        longueurs_um,
        hitran,
        color="tab:blue",
        linewidth=0.8,
        alpha=0.85,
        label="Modèle HITRAN",
    )
    axe.plot(
        longueurs_um,
        empirique,
        color="tab:orange",
        linewidth=2.0,
        label="Modèle empirique",
    )
    axe.set_ylim(bottom=0)
    axe.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    axe.grid(alpha=0.3)


def creer_graphique(nom_table, parametres):
    """Crée et enregistre la comparaison d'un gaz."""
    longueurs_um, empirique, hitran = calculer_courbes(
        nom_table,
        parametres["numero_hitran"],
        parametres["fonction_empirique"],
    )

    figure, axe = plt.subplots(figsize=(12, 7))
    tracer_courbes(axe, longueurs_um, empirique, hitran)
    axe.set_xlim(*PLAGE_COMPLETE_UM)
    axe.set_xlabel("Longueur d’onde (µm)")
    axe.set_ylabel("Section efficace (m²/molécule)")
    axe.set_title(
        f"Section efficace de {parametres['nom_affiche']} — "
        "modèle empirique et HITRAN"
    )
    axe.legend(loc="upper right")

    # Encart : même échelle linéaire, mais limites recalculées sur 4-20 µm.
    axe_zoom = axe.inset_axes([0.40, 0.43, 0.56, 0.46])
    tracer_courbes(axe_zoom, longueurs_um, empirique, hitran)
    axe_zoom.set_xlim(*PLAGE_ZOOM_UM)
    masque_zoom = (longueurs_um >= PLAGE_ZOOM_UM[0]) & (
        longueurs_um <= PLAGE_ZOOM_UM[1]
    )
    maximum_zoom = max(
        np.max(empirique[masque_zoom]),
        np.max(hitran[masque_zoom]),
    )
    axe_zoom.set_ylim(0, maximum_zoom * 1.05)
    axe_zoom.set_title("Zoom 4–20 µm", fontsize=10)
    axe_zoom.set_xlabel("µm", fontsize=9)
    axe_zoom.tick_params(labelsize=8)
    axe.indicate_inset_zoom(axe_zoom, edgecolor="0.35")

    figure.text(
        0.5,
        0.015,
        f"HITRAN : T = {TEMPERATURE_K:.0f} K, p = {PRESSION_ATM:.1f} atm — "
        "échelles verticales linéaires",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.035, 1, 1))

    DOSSIER_SORTIE.mkdir(exist_ok=True)
    chemin_sortie = DOSSIER_SORTIE / f"comparaison_{nom_table}_4_100um.png"
    figure.savefig(chemin_sortie, dpi=200, bbox_inches="tight")
    return chemin_sortie


def main():
    fichiers_crees = []
    for nom_table, parametres in GAZ.items():
        chemin = creer_graphique(nom_table, parametres)
        fichiers_crees.append(chemin)
        print(f"Graphique enregistré : {chemin}")

    # Les quatre fenêtres restent interactives avec un backend graphique.
    plt.show()
    return fichiers_crees


if __name__ == "__main__":
    main()
