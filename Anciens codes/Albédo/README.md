## Readme Albédo
>Lorsqu'un corps reçoit un rayonnement, l'albédo est le rapport entre l'énergie réfléchie et l'énergie incidente, c'est-à-dire reçue par la surface.

**- albedo_api.py :**

    Appel de l'API de la NASA, avec une moyenne des données de l'albédo faite sur une année (modifiable).
    
**- albedo_decoupage.py :**

    Donne l'albédo en fonction de la latitude et de la longitude via un découpage grossier de la Terre, avec des données d'albédo selon la matière.
    
**- API to CSV.py :**

    Permet la création d'un fichier CSV à partir de l'appel API pour ne plus avoir à faire l'appel à chaque fois qu'on lance notre code final.
