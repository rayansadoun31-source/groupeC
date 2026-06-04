import tkinter as tk  #Interface graphique utilisant Tkinter
from tkinter import ttk  # Importation de (Frame, Button, etc.)
import numpy as np  # Calculs numériques, tableaux, etc.
import matplotlib.pyplot as plt  # Tracé de graphiques
import cartopy.crs as ccrs  # Importation d'une carte
import matplotlib.patches as mpatches  # Pour dessiner des des rectangles
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Pour intégrer des graphiques matplotlib dans Tkinter
from Code_avec_appel_biblio import Temp  # Fonction fait pour calculer la température
from fonction_découpage_capacité_couleurs import colours, capacite  # Couleurs associées aux types de sols + fonction de découpage

def color_zones(ax, res=10):  # Fonction pour colorier la carte selon la capacité thermique
    """Colorie la carte selon capacite/colours."""
    for lon in np.arange(-180, 180, res):  # Parcourt les longitudes par pas de res
        for lat in np.arange(-90, 90, res):  # Parcourt les latitudes par pas de res
            cap = capacite(lat + res/2, lon + res/2)  # Récupère la capacité thermique au centre de la cellule
            color = colours.get(cap, '#FF00FF')  # Obtient la couleur correspondante, défaut : rose
            rect = mpatches.Rectangle(  # Crée un rectangle coloré
                (lon, lat), res, res, facecolor=color, alpha=0.6,  # Position, taille, couleur, transparence
                transform=ccrs.PlateCarree(), linewidth=0, edgecolor='none'  # Pas de bordure
            )
            ax.add_patch(rect)  # Ajoute le rectangle à la carte

def on_map_click(event):  # Fonction appelée quand on clique sur la carte
    if event.inaxes != ax_map:  # Si on ne clique pas sur la carte, on ignore
        return
    lon, lat = event.xdata, event.ydata  # Récupère la position du clic
    if lon is None or lat is None:  # Si clic hors carte, on ignore
        return
    lon, lat = round(lon,2), round(lat,2)  # Arrondit les coordonnées

    temp_vals = Temp(lat, lon, nb_jours_simulation=365)  # Calcule les températures sur un an
    t = np.linspace(0, 365, len(temp_vals))  # Crée l'axe des temps (jours)

    ax_temp.clear()  # Efface le graphe précédent
    ax_temp.plot(t, temp_vals, 'b-', linewidth=2)  # Trace la température en bleu
    ax_temp.set_title(f"Température à lat={lat}°, lon={lon}°")  # Titre
    ax_temp.set_xlabel("Temps (jours)")  # Légende axe X
    ax_temp.set_ylabel("Température (°C)")  # Légende axe Y
    ax_temp.grid(True, alpha=0.3)  # Active une grille légère
    ax_temp.set_xlim(0, 365)  # Fixe les bornes X

    if len(set(temp_vals)) > 1:  # Si la température varie
        y_min, y_max = min(temp_vals), max(temp_vals)  # Valeurs min/max
        margin = (y_max - y_min) * 0.1  # Marge de 10%
        ax_temp.set_ylim(y_min - margin, y_max + margin)  # Fixe les bornes Y avec marge
    else:  # Si température constante
        val = temp_vals[0]
        ax_temp.set_ylim(val - 5, val + 5)  # Fenêtre de ±5°C

    canvas_temp.draw()  # Redessine le graphe

# === Interface Tkinter ===

root = tk.Tk()  # Crée la fenêtre principale
root.title("Carte + Température")  # Titre de la fenêtre
root.geometry("1300x700")  # Taille de la fenêtre

frame_left = ttk.Frame(root)  # Cadre de gauche (carte)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

frame_right = ttk.Frame(root)  # Cadre de droite (graphique)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# === Carte ===
fig_map = plt.Figure(figsize=(7,5), dpi=100)  # Création de la figure de la carte
ax_map = fig_map.add_subplot(1,1,1, projection=ccrs.PlateCarree())  # Ajoute une carte plate carrée
ax_map.coastlines()  # Affiche les côtes
ax_map.set_global()  # Affiche le monde entier
ax_map.gridlines(draw_labels=True, alpha=0.3)  # Grille de coordonnées avec étiquettes
color_zones(ax_map)  # Coloriage de la carte par zones

canvas_map = FigureCanvasTkAgg(fig_map, master=frame_left)  # Intègre la carte dans Tkinter
canvas_map.draw()  # Dessine la carte
canvas_map.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Affiche dans le cadre

# === Graphique de température ===
fig_temp = plt.Figure(figsize=(7,5), dpi=100)  # Création de la figure de température
ax_temp = fig_temp.add_subplot(1,1,1)  # Ajoute un sous-graphe
ax_temp.set_title("Cliquez sur la carte pour voir la température")  # Titre par défaut
ax_temp.set_xlabel("Temps (heures)")  # Légende par défaut X
ax_temp.set_ylabel("Température (°C)")  # Légende Y
ax_temp.grid(True, alpha=0.3)  # Grille légère

canvas_temp = FigureCanvasTkAgg(fig_temp, master=frame_right)  # Intègre le graphe température
canvas_temp.draw()  # Dessine le graphe
canvas_temp.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Affiche dans le cadre

# === Zoom avec la molette ===
def on_scroll(event):  # Gère le zoom sur le graphe
    if event.inaxes != ax_temp:
        return
    base_scale = 1.2  # Facteur de zoom
    scale_factor = 1 / base_scale if event.button == 'up' else base_scale  # Zoom avant/arrière

    xlim = ax_temp.get_xlim()
    ylim = ax_temp.get_ylim()
    xdata = event.xdata
    ydata = event.ydata

    new_xlim = [
        xdata - (xdata - xlim[0]) * scale_factor,
        xdata + (xlim[1] - xdata) * scale_factor
    ]
    new_ylim = [
        ydata - (ydata - ylim[0]) * scale_factor,
        ydata + (ylim[1] - ydata) * scale_factor
    ]

    ax_temp.set_xlim(new_xlim)
    ax_temp.set_ylim(new_ylim)
    canvas_temp.draw()  # Redessine avec le zoom

# === Pan (déplacement) avec clic + glisser ===
pan_start = {'x': None, 'y': None, 'xlim': None, 'ylim': None}  # Coordonnées de départ du déplacement

def on_button_press(event):  # Clic souris enfoncé
    if event.inaxes != ax_temp:
        return
    pan_start['x'], pan_start['y'] = event.xdata, event.ydata  # Enregistre les coordonnées initiales
    pan_start['xlim'] = ax_temp.get_xlim()  # Limites X de départ
    pan_start['ylim'] = ax_temp.get_ylim()  # Limites Y de départ

def on_motion(event):  # Mouvement souris avec clic enfoncé
    if event.inaxes != ax_temp or pan_start['x'] is None or pan_start['y'] is None:
        return
    dx = event.xdata - pan_start['x']  # Déplacement en X
    dy = event.ydata - pan_start['y']  # Déplacement en Y
    ax_temp.set_xlim(pan_start['xlim'][0] - dx, pan_start['xlim'][1] - dx)  # Nouvelle fenêtre X
    ax_temp.set_ylim(pan_start['ylim'][0] - dy, pan_start['ylim'][1] - dy)  # Nouvelle fenêtre Y
    canvas_temp.draw()  # Redessine avec le déplacement

def on_button_release(event):  # Relâchement du clic
    pan_start['x'], pan_start['y'] = None, None  # Réinitialise les valeurs

# === Connexion des événements ===
fig_map.canvas.mpl_connect('button_press_event', on_map_click)  # Clic sur la carte → afficher température
fig_temp.canvas.mpl_connect('scroll_event', on_scroll)  # Molette sur graphe → zoom
fig_temp.canvas.mpl_connect('button_press_event', on_button_press)  # Clic pressé → début déplacement
fig_temp.canvas.mpl_connect('motion_notify_event', on_motion)  # Mouvement souris → déplacer
fig_temp.canvas.mpl_connect('button_release_event', on_button_release)  # Clic relâché → fin déplacement

root.mainloop()  # Lance la boucle principale Tkinter (affichage)