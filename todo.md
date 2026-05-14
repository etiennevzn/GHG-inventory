[x] Séparer les fichiers (mettre certaines fonctions dans un fichier utils) laisser juste création du modele + réponses aux questions dans l'ETL
[X] ETL : sauvegarder la distance entre les villes
[ ] ETL : revoir fonction imputation du type de matériel (la partie df['TYPE'] = df['TYPE'].fillna('Matériel Informatique'))
[ ] Voir si les réponses aux questions changent si on met date de début au 28 avril et date de fin au 15 novembre
[ ] graphique avion prédominant : soit changer les axes, soit faire une figure avec l'avion et une figure avec tout sauf l'avion
[ ] Vérifier cohérence questions ETL / dashboard
[ ] Slides
[ ] Repasser sur toutes les questions et vérifier que la logique est bonne 
[ ] Organiser fichiers dans les dossiers
[X] Modifier les fonctions de traitement pour mettre la boucle sur les dates à l'extérieur
[ ] Supprimer les tables de dimension inutiles + update UML
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
Dire tout ce qu'on fait dans l'ETL
-Uniformisation langue
Difficultés : 
-Limites API
-Estimation distance voyage dans la même ville
-Temps de chargement dashboard (pistes de solution : cache)
-Imputation données matériel : imputation du type à partir du modèle si présent, sinon type majoritaire dans le fichier + modèle par défaut

Rendu : 
-Feuille de questions remplies
-Questions à figure : mettre les figures en png dans le zip du rendu et mettre cf. figure XXX dans la feuille de réponse
-Slides : faire un schéma de l'arborescence des fichiers du projet et des fonctions
-Mettre captures d'écran du streamlit + lui présenter mardi prochain
-On peut mettre des annexes dans les slides