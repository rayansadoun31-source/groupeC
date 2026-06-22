import numpy as np
import matplotlib.pyplot as plt
import datetime

# =============================================================================
# CHOIX DU JOUR À AFFICHER
# =============================================================================
# ⚠️ MODIFIEZ UNIQUEMENT CE NOMBRE (Doit être le même que votre calcul) :
# 6 février: 37
# 6 mai: 126
# 5 aout: 217
# 6 novembre: 310
JOUR_DE_L_ANNEE = 37

# --- La magie de Python : Conversion automatique en noms ---
date_calc = datetime.datetime(2026, 1, 1) + datetime.timedelta(days=JOUR_DE_L_ANNEE - 1)
mois_fr = ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"]
nom_mois = mois_fr[date_calc.month - 1]

DATE_AFFICHEE = f"{date_calc.day} {nom_mois}"
SUFFIXE_FICHIER = f"{date_calc.day}_{nom_mois.upper()}"

# =============================================================================
# 1. CHARGEMENT DES DONNÉES
# =============================================================================
nom_fichier = f'Forcage_Atmospherique_{SUFFIXE_FICHIER}.npy'
print(f"Chargement du fichier {nom_fichier}...")

try:
    forcage_3D = np.load(nom_fichier)
except FileNotFoundError:
    print(f"ERREUR : Le fichier {nom_fichier} n'existe pas. Avez-vous lancé le calcul pour ce jour ?")
    exit()

print("\n--- STATISTIQUES GLOBALES ---")
print(f"Dimensions de la matrice : {forcage_3D.shape}")

donnees_jour_1 = forcage_3D[0, :, :]

print(f"Forçage moyen ({DATE_AFFICHEE}) : {np.mean(donnees_jour_1):.2f} W/m²")
print(f"Forçage maximum ({DATE_AFFICHEE}) : {np.max(donnees_jour_1):.2f} W/m²")
print(f"Forçage minimum ({DATE_AFFICHEE}) : {np.min(donnees_jour_1):.2f} W/m²")

# =============================================================================
# 2. CRÉATION DE LA CARTE
# =============================================================================
print("\nGénération de la carte en cours...")

plt.figure(figsize=(12, 6))

carte = plt.imshow(donnees_jour_1, cmap='magma', aspect='auto', 
                   extent=[-180, 180, -90, 90], origin='lower')

barre_couleur = plt.colorbar(carte)
barre_couleur.set_label("Rayonnement Infrarouge Descendant (W/m²)", fontsize=12)

# Titres dynamiques
plt.title(f"Forçage Radiatif Atmosphérique Mondial - {DATE_AFFICHEE}", fontsize=16, fontweight='bold')
plt.xlabel("Longitude (degrés)", fontsize=12)
plt.ylabel("Latitude (degrés)", fontsize=12)

plt.grid(color='white', linestyle='--', alpha=0.3)
plt.tight_layout()

# Sauvegarde dynamique de l'image
nom_image = nom_fichier.replace('.npy', '.png')
plt.savefig(nom_image, dpi=300, bbox_inches='tight')
print(f"\nImage sauvegardée avec succès sous : {nom_image}")

plt.show()