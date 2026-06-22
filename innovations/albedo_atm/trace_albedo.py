import xarray as xr
import matplotlib.pyplot as plt

chemin_fichier = 'alb.nc'
dataset = xr.open_dataset(chemin_fichier)

# 1. On isole le bloc de données exact que l'on veut tracer
data_a_tracer = dataset['albedo_0'].isel(pressure_level=1, dayofyear=268)

# 2. On remplace le texte de Copernicus par "Albédo" tout court
data_a_tracer.attrs['long_name'] = "Albédo" 
data_a_tracer.attrs['units'] = "Sans dimension (0-1)"

# 3. On génère le graphique
data_a_tracer.plot(cmap='viridis')

# 4. Ajouter un titre global propre
plt.title("Carte mondiale de l'albédo (Couche 4, Jour 230)")

# 5. Afficher la carte
plt.show()