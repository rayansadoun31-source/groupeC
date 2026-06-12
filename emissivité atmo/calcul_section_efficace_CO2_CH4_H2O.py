import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# CO2
# ==========================================================

def cross_section_CO2(wavelength):

    LAMBDA_0 = 15.0e-6      # 15 µm

    exponent = (
        -22.5
        - 24*np.abs(
            (wavelength-LAMBDA_0)/LAMBDA_0
        )
    )

    return 10**exponent


# ==========================================================
# CH4
# ==========================================================

def cross_section_CH4(wavelength):

    # bande principale vers 7.7 µm
    LAMBDA_1 = 7.7e-6

    exponent1 = (
        -23.0
        - 20*np.abs(
            (wavelength-LAMBDA_1)/LAMBDA_1
        )
    )

    sigma1 = 10**exponent1

    # bande secondaire vers 3.3 µm
    LAMBDA_2 = 3.3e-6

    exponent2 = (
        -23.5
        - 25*np.abs(
            (wavelength-LAMBDA_2)/LAMBDA_2
        )
    )

    sigma2 = 10**exponent2

    return sigma1 + sigma2


# ==========================================================
# H2O
# ==========================================================

def cross_section_H2O(wavelength):

    # bande 6.3 µm
    LAMBDA_1 = 6.3e-6

    exponent1 = (
        -22.0
        - 14*np.abs(
            (wavelength-LAMBDA_1)/LAMBDA_1
        )
    )

    sigma1 = 10**exponent1

    # bande 2.7 µm
    LAMBDA_2 = 2.7e-6

    exponent2 = (
        -22.5
        - 16*np.abs(
            (wavelength-LAMBDA_2)/LAMBDA_2
        )
    )

    sigma2 = 10**exponent2

    # absorption large dans l'IR lointain
    LAMBDA_3 = 20e-6

    exponent3 = (
        -23.0
        - 5*np.abs(
            (wavelength-LAMBDA_3)/LAMBDA_3
        )
    )

    sigma3 = 10**exponent3

    return sigma1 + sigma2 + sigma3


# ==========================================================
# TOTAL ATMOSPHERE
# ==========================================================

def cross_section_total(
        wavelength,
        CO2_fraction=420e-6,
        CH4_fraction=1.9e-6,
        H2O_fraction=0.01):

    sigma = (
        CO2_fraction * cross_section_CO2(wavelength)
        +
        CH4_fraction * cross_section_CH4(wavelength)
        +
        H2O_fraction * cross_section_H2O(wavelength)
    )

    return sigma

# Pour avoir les valeurs en un point :
#lam = 15e-6

#print(cross_section_CO2(lam))
#print(cross_section_CH4(lam))
#print(cross_section_H2O(lam))

#Pour avoir un graphique :


lam = np.linspace(1e-6,30e-6,2000)

plt.semilogy(
    lam*1e6,
    cross_section_CO2(lam),
    label='CO2'
)

plt.semilogy(
    lam*1e6,
    cross_section_CH4(lam),
    label='CH4'
)

plt.semilogy(
    lam*1e6,
    cross_section_H2O(lam),
    label='H2O'
)

plt.xlabel("Longueur d'onde (µm)")
plt.ylabel("Section efficace (m²/molécule)")
plt.legend()
plt.grid()

plt.show()