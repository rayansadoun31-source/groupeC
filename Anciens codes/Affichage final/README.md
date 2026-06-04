## Readme GUI et code
### Le GUI (interface graphique) permet d'afficher un planisphère de la Terre sur lequel on peut cliquer renvoyant un graphique de la température à cette position en fonction du temps.
**- Affichage_final.py :**

        Interface d'utilisateur qui affiche une carte du monde intéractive, l'utilisateur clique dessus pour obtenir un graphique qui affiche l'évolution de la température au cours d'un an.
        
>[!IMPORTANT]
 >**Modules à installer**:
 >pip install requests, pandas, cartopy
        
**- Code_avec_appel_biblio.py :** 

        Code le plus abouti sans interface graphique : sert de base à l'interface graphique (GUI).

**- Explication_code_avec_appel_biblio.md :** 

        Explication et détails généraux du code Code_avec_appel_biblio.py.

**- justification constantes.md :** 
  
        Validation scientifique du code Code_avec_appel_biblio.py.

**- albedo_lat_lon_multisampled_3pts.csv :** 
  
        Stockage des albédos obtenus avec les appels API de la NASA.

**- fonction_découpage_capacité_couleurs.py :**

        Cette fonction permet de découper le monde en des zones avec des capacités calorifiques différentes (selon la longitude et la latitude), ces capacités calorifiques sont également assignés des couleurs pour permettre le traçage sur la carte du monde dans le GUI.

**- imageterreaveclatlong.jpg :**

        Cette image de la carte du monde avec les lignes de latitude et longitude est utilisée dans l'affichage du GUI pour la carte intéractive. 
        
**- librairie_puissances.py :**

        Bibliothèque regroupant les différentes fonctions de calcul utilisées dans le modèle.

**- Document_explicatif_GUI.md :**

        Mode d'emploi du GUI et explication de ses différentes fonctionnalités.
