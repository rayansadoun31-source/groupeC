Ce programme python permet d'afficher une carte du monde dans une fenêtre Tkinter et de générer une courbe traçant la température prédit par notre modèle (fonction *Temp*).

<details>
<summary> <b>Affichage à gauche  </b></summary>
On colorie la carte du monde avec le code couleur correspondant aux approximations très simplifiées de la capacité calorifique que nous avons faites des différents types de terrains du globe.
Une estimation de l’albédo a aussi été effectuée pour chaque zone, en fonction de sa latitude et de sa longitude; cela est basé sur un pavage fait de moyennes des valeurs de la NASA.
</details>

<details>
<summary>  <b>Affichage à droite</b> </summary>
Le graphique de la température est généré à partir de la fonction Temp dans le fichier Code_avec_appel_biblio.py. Pour générer un graphique il faut cliquer sur un endroit sur la carte à gauche pour qu'il prenne les valeurs de longitude et latitude renvoyées par cette action et les rentre ensuite dans la fonction *Temp*. Puis, le graphique est affiché à gauche de manière que l'on puisse zoomer et se déplacer sur la courbe. 
</details>

<details>
<summary>  <b>Généralités</b> </summary>
Durée de fonctionnement : Actuellement le programme se déroule sur un an, pour modifier cela il faut modifier les lignes 31, 32 et 40 en remplançant 365 par le nombre de jours de simulation désiré.
</details>

<details>
<summary>  <b>Installations nécéssaires</b> </summary>
pip install: pandas, requests, cartopy
</details>

