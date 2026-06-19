import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# CONVERSION DES UNITÉS
# ==========================================================

def convertir_cm2_en_m2(section_cm2):
    """
    Convertit une section efficace de cm²/molécule en m²/molécule.

    """

    return section_cm2 * 1e-4



# ==========================================================
# MODÈLE SIMPLIFIÉ D'UN PIC D'ABSORPTION
# ==========================================================

def calculer_pic_absorption(longueur_onde, lambda_0, section_max, parametre_a):
    """
    Calcule une section efficace d'absorption simplifiée autour d'un pic approximé par une gaussienne.

    sigma(lambda) = sigma_max * 10^(-parametre_a * |lambda - lambda_0| / lambda_0)

    """

    section = section_max * 10**(
        -parametre_a * np.abs((longueur_onde - lambda_0) / lambda_0)
    )

    return section


# ==========================================================
# CALCUL DU PARAMÈTRE a
# ==========================================================

def calculer_parametre_a(lambda_0, lambda_gauche, lambda_droite):
    """
    Calcule le paramètre a qui correspond à la largeur du pic assimilé à une gaussienne.

    lambda_0 : longueur d'onde du sommet du pic
    lambda_gauche : longueur d'onde à gauche où sigma = sigma_max / 10
    lambda_droite : longueur d'onde à droite où sigma = sigma_max / 10
    
    """

    ecart_gauche = abs((lambda_gauche - lambda_0) / lambda_0)
    ecart_droite = abs((lambda_droite - lambda_0) / lambda_0)

    a_gauche = 1 / ecart_gauche
    a_droite = 1 / ecart_droite

    a_moyen = (a_gauche + a_droite) / 2

    return a_moyen

# ==========================================================
# PARAMÈTRES a DES PICS
# ==========================================================

# Pour l'instant, on garde les valeurs approchées déjà utilisées.
# Quand on lit les valeurs sur un vrai graphe, on peut remplacer ces valeurs par calculer_parametre_a(...)

a_CO2_15 = 24
a_CO2_42 = 24

a_CH4_33 = 25
a_CH4_77 = 20

a_H2O_27 = 16
a_H2O_63 = 14
a_H2O_174 = 5


# Exemple :
# a_CO2_15 = calculer_parametre_a(
#     lambda_0=15.0e-6,
#     lambda_gauche=14.5e-6,
#     lambda_droite=15.6e-6
# )


# ==========================================================
# SECTION EFFICACE DU CO2
# ==========================================================

def calculer_section_CO2(longueur_onde):
    """
    Calcule la section efficace d'absorption du CO2 en fonction de la longueur d'onde.

    Pics retenus :
        - 15 µm : sigma_max = 4e-18 cm²/molécule
        - 4.2 µm : sigma_max = 13e-18 cm²/molécule
    """

    # Pic à 15 µm
    section_15 = calculer_pic_absorption(
        longueur_onde=longueur_onde,
        lambda_0=15.0e-6,
        section_max=convertir_cm2_en_m2(4e-18),
        parametre_a=a_CO2_15
    )

    # Pic à 4.2 µm
    section_42 = calculer_pic_absorption(
        longueur_onde=longueur_onde,
        lambda_0=4.2e-6,
        section_max=convertir_cm2_en_m2(13e-18),
        parametre_a=a_CO2_42
    )

    return section_15 + section_42


# ==========================================================
# SECTION EFFICACE DU CH4
# ==========================================================

def calculer_section_CH4(longueur_onde):
    """
    Calcule la section efficace d'absorption du CH4 en fonction de la longueur d'onde.

    Pics retenus :
        - 3.3 µm : sigma_max = 1.8e-18 cm²/molécule
        - 7.7 µm : sigma_max = 7.7e-19 cm²/molécule
    """

    # Pic à 3.3 µm
    section_33 = calculer_pic_absorption(
        longueur_onde=longueur_onde,
        lambda_0=3.3e-6,
        section_max=convertir_cm2_en_m2(1.8e-18),
        parametre_a=a_CH4_33
    )

    # Pic à 7.7 µm
    section_77 = calculer_pic_absorption(
        longueur_onde=longueur_onde,
        lambda_0=7.7e-6,
        section_max=convertir_cm2_en_m2(7.7e-19),
        parametre_a=a_CH4_77
    )

    return section_33 + section_77


# ==========================================================
# SECTION EFFICACE DE H2O
# ==========================================================

def calculer_section_H2O(longueur_onde):
    """
    Calcule la section efficace d'absorption de H2O en fonction de la longueur d'onde.

    Pics retenus :
        - 2.7 µm : sigma_max = 723e-21 cm²/molécule
        - 6.3 µm : sigma_max = 916e-21 cm²/molécule
        - 17.4 µm : sigma_max = 31e-21 cm²/molécule
    """

    # Pic à 2.7 µm
    section_27 = calculer_pic_absorption(
        longueur_onde=longueur_onde,
        lambda_0=2.7e-6,
        section_max=convertir_cm2_en_m2(723e-21),
        parametre_a=a_H2O_27
    )

    # Pic à 6.3 µm
    section_63 = calculer_pic_absorption(
        longueur_onde=longueur_onde,
        lambda_0=6.3e-6,
        section_max=convertir_cm2_en_m2(916e-21),
        parametre_a=a_H2O_63
    )

    # Pic à 17.4 µm
    section_174 = calculer_pic_absorption(
        longueur_onde=longueur_onde,
        lambda_0=17.4e-6,
        section_max=convertir_cm2_en_m2(31e-21),
        parametre_a=a_H2O_174
    )

    return section_27 + section_63 + section_174


# ==========================================================
# SECTION EFFICACE MOYENNE DE L'ATMOSPHÈRE
# ==========================================================

def calculer_section_atmosphere(
        longueur_onde,
        fraction_CO2=420e-6,
        fraction_CH4=1.9e-6,
        fraction_H2O=0.01):
    """
    Calcule une section efficace moyenne de l'atmosphère.

    On pondère la section efficace de chaque gaz par sa fraction molaire :

        sigma_atmosphere =
            fraction_CO2 * sigma_CO2
          + fraction_CH4 * sigma_CH4
          + fraction_H2O * sigma_H2O

    Exemples de fractions molaires :
        420 ppm = 420e-6
        1.9 ppm = 1.9e-6
        1 % = 0.01
    """

    section_atmosphere = (
        fraction_CO2 * calculer_section_CO2(longueur_onde)
        +
        fraction_CH4 * calculer_section_CH4(longueur_onde)
        +
        fraction_H2O * calculer_section_H2O(longueur_onde)
    )

    return section_atmosphere


# ==========================================================
# VALEURS EN UN POINT
# ==========================================================

longueur_onde_test = 15e-6

print("À 15 µm :")
print("CO2 :", calculer_section_CO2(longueur_onde_test), "m²/molécule")
print("CH4 :", calculer_section_CH4(longueur_onde_test), "m²/molécule")
print("H2O :", calculer_section_H2O(longueur_onde_test), "m²/molécule")
print("Atmosphère :", calculer_section_atmosphere(longueur_onde_test), "m²/molécule")


# ==========================================================
# GRAPHIQUE
# ==========================================================

longueurs_onde = np.linspace(1e-6, 30e-6, 2000)

plt.semilogy(
    longueurs_onde * 1e6,
    calculer_section_CO2(longueurs_onde),
    label='CO2'
)

plt.semilogy(
    longueurs_onde * 1e6,
    calculer_section_CH4(longueurs_onde),
    label='CH4'
)

plt.semilogy(
    longueurs_onde * 1e6,
    calculer_section_H2O(longueurs_onde),
    label='H2O'
)

plt.xlabel("Longueur d'onde (µm)")
plt.ylabel("Section efficace (m²/molécule)")
plt.legend()
plt.grid()

plt.show()