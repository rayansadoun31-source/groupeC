import matplotlib.pyplot as plt
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------

# ===================
# RAYONNEMENT DU CORPS NOIR
# ===================

def planck_function(lambda_wavelength, T):
    h = 6.62607015e-34      # constante de Planck, J·s
    c = 2.998e8             # vitesse de la lumière, m/s
    kB = 1.380649e-23       # constante de Boltzmann, J/K
    term1 = (2 * h * c**2) / lambda_wavelength**5
    term2 = np.exp((h * c) / (lambda_wavelength * kB * T)) - 1
    return term1 / term2

# ----------------------------------------------------------------------------------------------------------------------

# ================
# MODÈLE D'ATMOSPHÈRE
# ================

def pressure(z):
    P0 = 101325     # pression au niveau de la mer, Pa
    H = 8500        # hauteur d'échelle de l'atmosphère, m
    return P0 * np.exp(-z / H)

def temperature_uniform(z):
    T0 = 288.2
    return T0 * np.ones_like(z)

def temperature_simple(z):
    T0 = 288.2      # température au niveau de la mer, K
    z_trop = 11000  # altitude de la tropopause, m
    Gamma = -0.0065 # gradient thermique, K/m
    T_trop = T0 + Gamma * z_trop
    return np.piecewise(z, [z < z_trop, z >= z_trop],
                        [lambda z: T0 + Gamma * z,
                         lambda z: T_trop])

def temperature_US1976(z):
    z_km = z/1000  # conversion de l'altitude en kilomètres

    # Troposphère (0 à 11 km)
    T0 = 288.15
    z_trop = 11

    # Tropopause (11 à 20 km)
    T_tropopause = 216.65
    z_tropopause = 20

    # Basse stratosphère (20 à 32 km)
    T_strat1 = T_tropopause
    z_strat1 = 32

    # Haute stratosphère (32 à 47 km)
    T_strat2 = 228.65
    z_strat2 = 47

    # Stratopause (47 à 51 km)
    T_stratopause = 270.65
    z_stratopause = 51

    # Basse mésosphère (51 à 71 km)
    T_meso1 = T_stratopause
    z_meso1 = 71

    # Mésosphère au-delà de 71 km
    T_meso2 = 214.65

    return np.piecewise(z_km,
                        [z_km < z_trop,
                         (z_km >= z_trop) & (z_km < z_tropopause),
                         (z_km >= z_tropopause) & (z_km < z_strat1),
                         (z_km >= z_strat1) & (z_km < z_strat2),
                         (z_km >= z_strat2) & (z_km < z_stratopause),
                         (z_km >= z_stratopause) & (z_km < z_meso1),
                         z_km >= z_meso1],
                        [lambda z: T0 - 6.5 * z,
                         lambda z: T_tropopause,
                         lambda z: T_strat1 + 1 * (z - z_tropopause),
                         lambda z: T_strat2 + 2.8 * (z - z_strat1),
                         lambda z: T_stratopause,
                         lambda z: T_meso1 - 2.8 * (z - z_stratopause),
                         lambda z: T_meso2 - 2 * (z - z_meso1)])


# Profil de température choisi pour la simulation.
def temperature(z):
    return temperature_simple(z)

def air_number_density(z):
    kB = 1.380649e-23  # constante de Boltzmann, J/K
    return pressure(z) / (kB * temperature(z))

# ----------------------------------------------------------------------------------------------------------------------

# ==============
# ABSORPTION DU CO₂
# ==============

def cross_section_CO2(wavelength):
    # Le modèle représente l'absorption du CO₂ par une bande centrée sur 15 µm.
    LAMBDA_0 = 15.0e-6  # centre de la bande, m
    exponent = -22.5 - 24 * np.abs((wavelength - LAMBDA_0) / LAMBDA_0)
    sigma = 10 ** exponent
    return sigma

# ----------------------------------------------------------------------------------------------------------------------

# =============================
# SIMULATION DU TRANSFERT RADIATIF
# =============================

# Toutes les longueurs d'onde sont calculées en même temps.

def simulate_radiative_transfer(
    CO2_fraction,
    z_max=80000,
    delta_z=10,
    lambda_min=0.1e-6,
    lambda_max=100e-6,
    delta_lambda=0.01e-6,
    conserver_historique=True,
):

    # Grilles d'altitude et de longueur d'onde
    z_range = np.arange(0, z_max, delta_z)
    lambda_range = np.arange(lambda_min, lambda_max, delta_lambda)

    # L'historique complet est utile pour étudier chaque altitude, mais coûte
    # environ 1,2 Go avec la grille par défaut. Le mode léger ne conserve que
    # les valeurs au sommet de l'atmosphère.
    if conserver_historique:
        upward_flux = np.zeros((len(z_range), len(lambda_range)))
        optical_thickness = np.zeros((len(z_range), len(lambda_range)))
    else:
        upward_flux = np.zeros((1, len(lambda_range)))
        optical_thickness = np.zeros((1, len(lambda_range)))

    # Flux émis par la surface terrestre à chaque longueur d'onde
    earth_flux = np.pi * planck_function(lambda_range, temperature(0)) * delta_lambda
    print(f"Total earth surface flux in wavelength range: {earth_flux.sum():.2f} W/m^2")

    flux_in = earth_flux
    for i, z in enumerate(z_range):

        # Quantité de CO₂ et absorption dans la couche
        n_CO2 = air_number_density(z) * CO2_fraction
        kappa = cross_section_CO2(lambda_range) * n_CO2

        # Le flux absorbé ne peut pas dépasser le flux reçu par la couche.
        epaisseur_optique_couche = kappa * delta_z
        absorbed_flux = np.minimum(kappa * delta_z * flux_in , flux_in)
        emitted_flux = epaisseur_optique_couche * np.pi * planck_function(lambda_range, temperature(z)) * delta_lambda
        flux_out = flux_in - absorbed_flux + emitted_flux

        if conserver_historique:
            optical_thickness[i, :] = epaisseur_optique_couche
            upward_flux[i, :] = flux_out

        # Le flux sortant devient le flux reçu par la couche suivante.
        flux_in = flux_out

    if not conserver_historique:
        optical_thickness[0, :] = epaisseur_optique_couche
        upward_flux[0, :] = flux_in

    print(f"Total outgoing flux at the top of the atmosphere: {upward_flux[-1,:].sum():.2f} W/m^2")

    return lambda_range, z_range, upward_flux, optical_thickness

# ----------------------------------------------------------------------------------------------------------------------

def main():
    """Compare les spectres sortants pour 280 et 560 ppm de CO₂."""
    CO2_fraction = 280e-6
    lambda_range, _, upward_flux, _ = simulate_radiative_transfer(
        CO2_fraction,
        conserver_historique=False,
    )
    lambda_range, _, upward_flux2, _ = simulate_radiative_transfer(
        2 * CO2_fraction,
        conserver_historique=False,
    )

    # Spectre au sommet de l'atmosphère
    plt.figure(figsize=(14, 9))
    # Corps noirs de référence à la température du sol et à 216 K.
    plt.plot(1e6 * lambda_range, np.pi * planck_function(lambda_range, temperature(0))/1e6,'--k')
    plt.plot(1e6 * lambda_range, np.pi * planck_function(lambda_range, 216)/1e6,'--k')

    delta_lambda = lambda_range[1] - lambda_range[0]
    plt.plot(1e6 * lambda_range, upward_flux[-1, :]/delta_lambda/1e6,'-g')
    plt.plot(1e6 * lambda_range, upward_flux2[-1, :]/delta_lambda/1e6,'-r')
    plt.fill_between(1e6 * lambda_range, upward_flux[-1, :]/delta_lambda/1e6, upward_flux2[-1, :]/delta_lambda/1e6, color='yellow', alpha=0.9)
    plt.xlabel("Longueur d'onde (μm)")
    plt.ylabel("Luminance spectrale (W/m²/μm/sr)")
    plt.xlim(0, 50)
    plt.ylim(0, 30)
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------------------------------------------------
