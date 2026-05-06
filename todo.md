[ ] Priorité : voir comment nettoyer les NaN dans les données de matériel (reprendre le TD)

[ ] Repasser sur toutes les questions et vérifier que la logique est bonne 

[X] Architecture Data Warehouse 
[ ] ETL journaliser
[ ] Questions
[ ] Tableau de bord
[ ] Slides
[x] Créer la table de dimension date 
[X] Tables de dimension
[X] Tables de faits
[ ] Voir si notre boucle respecte ce qu'il disait (ajouter les données à la suite dans la table finale)
[ ] Pour les trajets dans la même ville, trouver une solution pour la distance
[ ] Séparer les fichiers (mettre certaines fonctions dans un fichier utils par exemple)
[ ] Mission sur les sites européens : on est d'accord que ça concerne paris, londres et berlin ?
[ ] Clarifier transports en communs et voir quel facteur prendre pour les bus
[ ] coeff taxi : 1.2 ou 1.3 ??
[ ] Verifier l'age pendant la mission (mettre une borne inf et borne max)
[ ] Est-ce que secteur d'activité = fonction personnel ? 
[ ] Ambiguite seminaire / conférence (questions 13/14)
[ ] Question 18 dépends uniquement du trajet et non du matériel donc beaucoup de duplicat de valeurs pour des missions différentes
[ ] Question 18 double check si le calcul des emission du taxi (top1) est bon (2625.9 miles de route) plus importante que celle de  Shanghai (19 631km en avion)

Vol Shanghai → Buenos Aires (19 631 km)
Pour un vol long-courrier, l'émission moyenne est d'environ 90 g de CO₂ par passager par kilomètre (en incluant le forçage radiatif, c'est plus proche de 150-250 g/km, mais restons sur le CO₂ direct pour comparer équitablement).
19 631 km × 90 g/km ≈ 1,77 tonne de CO₂ par passager
Trajet en taxi DC → LA (2625,9 miles ≈ 4 226 km)
Une voiture thermique moyenne émet environ 170-200 g de CO₂ par km. Prenons 180 g/km pour un taxi (souvent une berline).
4 226 km × 180 g/km ≈ 0,76 tonne de CO₂
Verdict : le vol émet plus de CO₂, environ 2,3 fois plus que le taxi, malgré le fait qu'on compare souvent l'avion et la voiture en disant que la voiture pollue plus par personne. Ici, deux facteurs jouent :

La distance du vol est environ 4,6 fois plus longue que celle du taxi
Tu voyages seul dans le taxi (1 passager), alors que pour l'avion j'ai compté l'émission par passager — si on prend l'émission totale de l'avion (avec ~250 passagers), on parle de ~440 tonnes pour le vol entier, sans comparaison possible

Si on remplit le taxi avec 4 personnes, l'écart se creuse encore plus en faveur du taxi (190 kg de CO₂ par personne contre 1,77 tonne pour le vol).
