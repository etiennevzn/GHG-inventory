[X] Supprimer les tables de dimension inutiles + update UML
[X] Repasser sur toutes les questions et vérifier que la logique est bonne et mettre réponse finale sur la fiche 
[X] Vérifier cohérence questions ETL / dashboard
[X] Voir si les réponses aux questions changent si on met date de début au 28 avril et date de fin au 15 novembre

[X] graphique avion prédominant : soit faire une figure avec l'avion et une figure avec tout sauf l'avion
[ ] Slides : https://docs.google.com/presentation/d/17kTfnRmv_DdEbygoQ7ePQyJc8KapBfdv2KinFjL4YJ8/edit?slide=id.g3e23d1b08d5_0_373#slide=id.g3e23d1b08d5_0_373
[X] Organiser fichiers dans les dossiers

[x] Séparer les fichiers (mettre certaines fonctions dans un fichier utils) laisser juste création du modele + réponses aux questions dans l'ETL
[X] ETL : sauvegarder la distance entre les villes
[X] ETL : revoir fonction imputation du type de matériel : en fait le problème de remplacer par le truc le plus courant c'est que ça change par exemple la réponse à nb de pc fixes achetés, est-ce qu'on laisse ça => oui

[X] Modifier les fonctions de traitement pour mettre la boucle sur les dates à l'extérieur
[X] Est-ce que la fonctions d'extraction du personnel on sort la boucle de la fonction ?
[X] Priorité : voir comment nettoyer les NaN dans les données de matériel 
[X] Architecture Data Warehouse 
[X] ETL journaliser
[X] Questions
[x] Créer la table de dimension date 
[X] Tables de dimension
[X] Tables de faits
[X] Pour les trajets dans la même ville, trouver une solution pour la distance

Slides : 
-Modèle étoile : UML, dimensions partagées...
-ETL :
    -Personnel :
        -Uniformisation de la langue pour les secteurs d'activités (anglais)
        -Calcul de l'age du personnel
        -Fonction d'extraction lit le fichier, converti la langue du secteur d'activité et calcul l'age, et garde seulement les colonnes nécessaires au modèle étoile
    -Matériel : 
        -Imputation des données manquantes : Si type manquant et pas modèle : à partir d'un modèle, on peut récupérer le type de matériel avec un dictionnaire constitué à partir du fichier impact matériel. Si modèle manquant et pas type : modèle par défaut. Si modèle et type manquant : on prend le type majoritaire dans le fichier qu'on est en train de traiter et modèle par défaut 
        -Impact du matériel : on join le fichier matériel avec le fichier d'impact sur type et modèle et on récupère directement l'impact
        -Fonction d'extraction lit les fichiers matériel de la date de tous les sites, uniformise le fuseau horaire, nettoie et impute les données matériel et ajoute une colonne impact
    -Missions : 
        -Uniformisation de la langue pour le type de mission
        -fonction de calcul de distance entre les villes en utilisant geopy
        -calcul des emissions : récupération des fichiers contenant les facteurs d'émission sur le site de labo1.5. Application d'un coefficient à la distance en fonction du mode de transport, puis récupération du facteur en fonction du trajet et du type de transport, puis calcul de l'émission totale en prenant en compte les allers retours et le cas particulier du taxi. Emissions / 1000 car elles sont en kgCO2e de base. 
        -Fonction d'extraction lit les fichiers missions de la date qu'elle prend en paramètre pour tous les sites, uniformise la langue du type de mission, le fuseau horaire et calcule les emissions de chaque mission dans une nouvelle colonne 
-Utilisation : 
    -Création des tables de faits et dimensions avec les fonctions définies précédemment
    -Convertion vers le format spark sql dataframe pour requêtes
    -Requêtes pour réponses aux questions
    -Export des tables de dimension et fait au format parquet pour une utilisation dans le dashboard
-Difficultés : 
    -Limites API Geopy : pour contrer ça on a créé un grand dictionnaire qui sauvegarde les coordonnées des villes les plus courantes en mission, et on essaye d'abord ce dictionnaire avant de faire un nouvel appel à l'API
    -Estimation distance voyage dans la même ville : on estime la distance avec une loi normale
    -Temps de chargement dashboard : résolu en ne refaisant pas les calculs à chaque fois mais une seule fois lors de la phase ETL
    -Imputation données matériel : imputation du type à partir du modèle si présent, sinon type majoritaire dans le fichier + modèle par défaut

Rendu : 
-Feuille de questions remplies
-Questions à figure : mettre les figures en png dans le zip du rendu et mettre cf. figure XXX dans la feuille de réponse
-Slides : faire un schéma de l'arborescence des fichiers du projet et des fonctions
-Mettre captures d'écran du streamlit + lui présenter mardi prochain
-On peut mettre des annexes dans les slides