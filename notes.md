# Date de rendu : 19 mai

# Catégories d'émission 

3 catégories d’emissions de GES vis-à-vis du BGES d’une organisation, dont 2 principales :

- Émission directe de GES :  ́Emission de GES à partir de sources appartenant à ou  ́etant sous le contrôle de l’organisation. On retrouve par exemple missions, achats ou matériel informatique.

- Émission indirecte de GES :  ́Emission de GES consommée par l’organisation mais qui provient de sources n’appartenant pas ou n'étant pas sous le contrôle de l’organisation. On retrouve par exemple les déplacements domicile / travail 

Objectif : Estimer le BGES de l'organisation en fonction de ses missions qui sont importantes pour le bien de son activité, du materiel informatique qui est là aussi nécessaire pour son
activité.

Sites de l’organisation : Paris, Londres, Berlin, New-York, Los Angeles, Shanghai.

Secteurs d'activité : Ingénieur Data / Ingénieur Informaticien / Cadre / Economiste / DRH
Attention : nécessité d'homogénéiser la langue des secteurs d'activité dans les bases de données en fonction du site. 

Transports possibles pour les missions : Avion / Train / Taxi / Transports en commun

# Calcul de l'empreinte carbone de chaque transport pour les missions

Calcul générique : calcul des émissions d’un trajet puis agrégation des émissions de tous les trajets sur l’année considérée. Émissions d’un trajet = distance parcourue (calculer avec GeoPy) * facteur d’émission du mode de déplacement (par km parcouru ou par passager-km)

Pour la distance : 
- Calculer la distance à vol d'oiseau entre 2 villes 
- Appliquer un coefficient en fonction du moyen de transport : 1,3 pour les déplacements en voiture, 1,2 pour le train et pour le RER, 1,7 pour le métro, 1,5 pour le bus et le tramway.
- Pour les déplacements en taxi, la distance routière du retour est systématiquement prise en compte et correspond à la distance aller
- Pour les déplacements en avion, 95km sont ajoutés à la distance à vol d’oiseau

Spécificité des déplacements en bus :
Nous faisons l’hypothèse que les trajets en bus inter-urbains seront majoritaires en terme de distances parcourues lors d’une mission, comparativement aux trajets en bus urbains. Les trajets inter-urbains étant moins émetteurs que les trajets urbains, nous prenons le facteur d’émission le moins élevé parmi les 3 facteurs disponibles dans la Base Carbone: c’est celui des bus dans des agglomérations de plus de 250 000 habitants.

Spécificité des déplacements en train :
Nous distinguons les trajets purement sur le territoire national, des trajets avec une ville d’origine ou de destination à l’étranger pour tenir compte de facteurs d’émission différenciés (cf fichier justification des facteurs d’émission)

Spécificité des déplacements en avion :
Un test est effectué sur la distance parcourue pour sélectionner le facteur d’émission adéquat (trajet inférieur à 1000 km, de 1001 à 3500 km, supérieur à 3500 km)

Spécificité des déplacements en taxi :
Le facteur d’émission retenu est celui de la voiture "motorisation moyenne" de la Base Carbone. Les émissions sont divisées par le nombre de personnes dans le taxi pour le trajet aller. Pour le retour au point d’origine, nous faisons l’hypothèse que le taxi revient seulement avec une personne à bord (le chauffeur).
Emissions des déplacements en taxi = (distance orthodromique*1,2) * (1 + 1 / nb de personnes à bord) * facteur d’émission voiture "motorisation moyenne"

# Calcul de l'empreinte carbone du matériel informatique

Pour chaque site de l’organisation, un fichier contenant les achats quotidiens de matériel informatique sur le site a été enregistré chaque jour. Remarque : Certaines données de ces fichiers quotidiens peuvent être manquantes (donc potentiellement les imputer avec moyenne ou ML)

# Idée pour le schéma du Data Warehouse : 

Pour chaque site : 

- Dimension personnel (homogénéiser la langue du secteur d'activité)
- Dimension mission (homogénéiser la langue du type de la mission)
- Dimension matériel informatique (nécessité d'estimation des données manquantes dans les fichiers des différents sites)
- Table de fait qui regroupe les clés primaires des 3 dimensions 

Coment réunir les modèles étoile de chaque site ? 




