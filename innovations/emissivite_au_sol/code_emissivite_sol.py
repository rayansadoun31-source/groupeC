import ee

# Remplace 'ton-vrai-id-en-minuscules' par l'ID que tu viens de copier
ee.Initialize(project='eternal-flux-499913-m1')

print("Connexion réussie ! Lancement du calcul...")

# (La suite de ton code avec MODIS, date_debut, etc.)

# ... la suite du code avec date_debut = ee.Date('2020-01-01') etc ...

# 1. Configuration des paramètres
date_debut = ee.Date('2020-01-01')
date_fin = ee.Date('2024-12-31')

# 2. Chargement et filtrage de la bande d'émissivité
collection = ee.ImageCollection('MODIS/061/MOD11A1') \
    .filterDate(date_debut, date_fin) \
    .select('Emis_31')

# 3. Application du facteur d'échelle
def ajuster_echelle(image):
    return image.multiply(0.002).add(0.49) \
                .copyProperties(image, ['system:time_start'])

collection_calibree = collection.map(ajuster_echelle)

# 4. Calcul de la moyenne par jour de l'année (1 à 365)
liste_jours = ee.List.sequence(1, 365)

def calculer_moyenne_jour(jour):
    # On précise à Google que "jour" est un nombre sur le serveur
    jour_ee = ee.Number(jour)
   
    # On demande au serveur de concaténer le mot "jour_" avec la valeur numérique
    # L'astuce : '%03d' permet d'avoir 'jour_001', 'jour_002', c'est plus propre pour trier les bandes à la fin !
    nom_bande = ee.String('jour_').cat(jour_ee.format('%03d'))
   
    return collection_calibree \
        .filter(ee.Filter.calendarRange(jour_ee, jour_ee, 'day_of_year')) \
        .mean() \
        .rename(nom_bande) # On passe l'objet serveur ee.String au lieu du f-string Python

climatologie = ee.ImageCollection.fromImages(liste_jours.map(calculer_moyenne_jour))
image_finale = climatologie.toBands()

# 5. Définition de la emprise mondiale (180x360 mailles de 1 degré)
grille_mondiale = ee.Geometry.Rectangle([-180, -90, 180, 90], 'EPSG:4326', False)

# 6. Création de la tâche d'exportation vers Google Drive
task = ee.batch.Export.image.toDrive(
    image=image_finale,
    description='Climatologie_Emissivite_5Ans_1Degre',
    folder='EarthEngine_Exports',
    fileNamePrefix='emissivite_mondiale_365jours',
    region=grille_mondiale,
    scale=111320,  # ~1 degré à l'équateur
    crs='EPSG:4326',
    maxPixels=1e13
)

# Lancement du calcul sur les serveurs Google
task.start()
print("Le calcul a commencé sur Google Earth Engine.")
print("Le fichier final (contenant 365 bandes pour chaque jour) sera déposé dans votre Google Drive.")