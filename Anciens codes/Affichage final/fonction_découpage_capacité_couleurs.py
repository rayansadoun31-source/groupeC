# Capacité thermique massique en J/kg.K
capa_glace = 2060
capa_eau = 4185
capa_neige = 2092
capa_desert = 835
capa_foret = 2400
capa_terre = 750

colours = {
    capa_glace: "#4F84A0",   # bleu clair pour la glace
    capa_eau: "#2D1EFF",     # bleu pour l'eau
    capa_neige: "#737A83",   # gris neige
    capa_desert: "#FFD700",  # jaune doré pour le désert
    capa_foret: "#228B22",   # vert forêt
    capa_terre: "#8B4513",   # marron pour la terre
}

# Capacité thermique massique en fonction de la localisation
def capacite(lat, lng):
    if lat >= 65 or lat <= -65 :
        return capa_glace
    elif lng >= 160 or lng <= -140 :
        return capa_eau
    elif lng <= -120 and lng >= -140 and lat >= -65 and lat <= 50 :
        return capa_eau
    elif lng <= -80 and lng >= -120 and lat >= -65 and lat <= 20 :
        return capa_eau
    elif lng <= 140 and lng >= -60 and lat >= -65 and lat <= -30 :
        return capa_eau
    elif lng <= -60 and lng >= -80 and lat >= 10 and lat <= 40 :
        return capa_eau
    elif lng <= 0 and lng >= -60 and lat >= 30 and lat <= 65 :
        return capa_eau
    elif lng <= -20 and lng >= -60 and lat >= 10 and lat <= 30 :
        return capa_eau
    elif lng <= 10 and lng >= -60 and lat >= 0 and lat <= 10 :
        return capa_eau
    elif lng <= 10 and lng >= -40 and lat >= -30 and lat <= 0 :
        return capa_eau
    elif lng <= 120 and lng >= 40 and lat >= 10 and lat <= 20 :
        return capa_eau
    elif lng <= 100 and lng >= 40 and lat >= -30 and lat <= 10 :
        return capa_eau
    elif lng <= 120 and lng >= 100 and lat >= -30 and lat <= -10 :
        return capa_eau
    elif lng <= 140 and lng >= 120 and lat >= 0 and lat <= 30 :
        return capa_eau
    elif lng <= 160 and lng >= 140 and lat >= 0 and lat <= 60 :
        return capa_eau
    elif lng <= 160 and lng >= 140 and lat<= -40 and lat >= -60 :
        return capa_eau
    elif lng <= -60 and lng >= - 80 and lat<= 10 and lat >= 0 :
       return capa_foret
    elif lng <= -40 and lng >= - 80 and lat <= 0 and lat >= -30 :
        return capa_foret
    elif lng <= -60 and lng >= - 80 and lat <= -30 and lat >= -65 :
        return capa_foret
    elif lng <= 40 and lng >= - 20 and lat <= 20  and lat >= -10 :
        return capa_foret
    elif lng <= 140 and lng >= 100 and lat<= 40 and lat >= 30 :
        return capa_foret
    elif lng <= 120 and lng >= 100 and lat<= 30 and lat >= 0 :
        return capa_foret
    elif lng <= 160 and lng >= 100 and lat<= 0 and lat >= -10 :
        return capa_foret
    elif lng <= 160 and lng >= 140 and lat<= -30 and lat >= -40 :
        return capa_foret
    elif lng <= 40 and lng >= 10 and lat<= -10 and lat >= -30 :
        return capa_desert
    elif lng <= 60 and lng >= 0 and lat<= 40 and lat >= 20 :
        return capa_desert
    elif lng <= 160 and lng >= 120 and lat<= -10 and lat >= -30 :
        return capa_desert
    elif lng <= -0 and lng >= - 20 and lat<= 30 and lat >= 20 :
        return capa_desert
    elif lng <= -80 and lng >= - 120 and lat<= 50 and lat >= 20 :
        return capa_terre
    elif lng <= 140 and lng >= 0 and lat<= 60 and lat >= 30 :
        return capa_terre
    elif lng <= 60 and lng >= 40 and lat<= 40 and lat >= 20 :
        return capa_terre
    elif lng <= 100 and lng >= 40 and lat<= 40 and lat >= 20 :
        return capa_terre
    else:
        return capa_neige