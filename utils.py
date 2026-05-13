import pandas as pd
import numpy as np
from pathlib import Path
import pyspark.pandas as ps
from pyspark.sql.functions import *
from datetime import date, timedelta
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import pandas as pd
import unicodedata

np.random.seed(42) # Fixation de seed pour avoir des résultats reproductibles lors 
# du calcul des distances intra-ville

# Sert à calculer les distances entre les villes
geolocator = Nominatim(user_agent="BGES_app")

# ===================================
# Fonctions de traitement des données
# ===================================

# Fonctions d'homogénéisation de la langue des fonctions et missions
# On homogénéise la langue des missions / fonctions en anglais car 4 sites sur 6 utilisent déjà l'anglais

def clean_langue_fonction(df, site):
    match site:
        case "BERLIN":
            map_fonctions = {
                "Ökonom": "Economist",
                "Führungskraft": "Business Executive",
                "Personalleiter": "HRD",
                "Computeringenieur": "Computer Engineer",
                "Dateningenieur": "Data Engineer",
            }
            df["FONCTION_PERSONNEL"] = df["FONCTION_PERSONNEL"].replace(map_fonctions)
        case "PARIS":
            map_fonctions = {
                "Ingénieur Informaticien": "Computer Engineer",
                "Ingénieur Data": "Data Engineer",
                "Economiste": "Economist",
                "DRH": "HRD",
                "Cadre": "Business Executive",
            }
            df["FONCTION_PERSONNEL"] = df["FONCTION_PERSONNEL"].replace(map_fonctions)


def clean_langue_mission(df, site):
    match site:
        case "BERLIN":
            map_type_mission = {
                "Geschäftstreffen": "Business Meeting",
                "Konferenz": "Conference",
                "Schulung": "Vocational Training",
                "Meeting": "Team Meeting",
                "Entwicklung": "Development",
            }
            df["TYPE_MISSION"] = df["TYPE_MISSION"].replace(map_type_mission)
        case "PARIS":
            map_type_mission = {
                "Conférence": "Conference",
                "Formation": "Vocational Training",
                "Réunion": "Team Meeting",
                "Rencontre entreprises": "Business Meeting",
                "Développement": "Development",
            }
            df["TYPE_MISSION"] = df["TYPE_MISSION"].replace(map_type_mission)

# Fonction d'homogénéisation des fuseaux horaires

def clean_date(df, site, date_col):
    """
    Convertit la colonne de dates d'un site donné vers UTC+2 (heure de Paris).
    On suppose que le fuseau horaire originel des dates est celui de leur site de provenance. 
    """
    # Mapping site -> fuseau horaire IANA
    site_tz = {
        "PARIS":      "Europe/Paris",
        "BERLIN":     "Europe/Berlin",
        "LONDON":     "Europe/London",
        "NEWYORK":    "America/New_York",
        "LOSANGELES": "America/Los_Angeles",
        "SHANGHAI":   "Asia/Shanghai",
    }

    tz = site_tz[site]

    # S'assurer que la colonne est bien en datetime
    df[date_col] = pd.to_datetime(df[date_col], format="%Y-%m-%d %H:%M:%S")

    # Localiser la date dans le fuseau du site, puis convertir vers Paris (UTC+2 en été)
    df[date_col] = (
        df[date_col]
          .dt.tz_localize(tz, ambiguous=False, nonexistent='shift_forward') # on dit "cette heure est en heure locale du site"
          # les params ambiguous et nonexistent sont utilisés pour les heures du changement d'heure
          .dt.tz_convert("Europe/Paris")  # on la convertit vers Paris
          .dt.tz_localize(None)           # on retire l'info de fuseau horaire
    )

# Fonctions pour calculer l'age d'un employé

def calcul_age(date_naissance, date_reference=None):
    if date_reference is None:
        date_reference = date.today()
    age = date_reference.year - date_naissance.year
    # Retire 1 an si l'anniversaire n'est pas encore passé
    if (date_reference.month, date_reference.day) < (date_naissance.month, date_naissance.day):
        age -= 1
    return age

def convertir_age_personnel(df_personnel, date_reference=None, timezone="UTC"):

    if date_reference is None:
        date_reference = date.today()
    
    df = df_personnel.copy()
    
    # Conversion au fuseau horaire général
    df["DT_NAISS"] = pd.to_datetime(df["DT_NAISS"], utc=True).dt.tz_convert(timezone)
    
    
    df["AGE"] = df["DT_NAISS"].apply(calcul_age)
    
    # Suppression de DT_NAISS
    df = df.drop(columns=["DT_NAISS"])
    
    return df

# Fonction pour extraire et traiter les données du personnel

def extract_personnel():
    sites = ["PARIS", "BERLIN", "LONDON", "NEWYORK", "SHANGHAI", "LOSANGELES"]
    base_path = Path("data/BDD_BGES")

    personnel_dfs = []

    # On charge la liste du personnel de chaque site dans un dataframe
    for site in sites:
        file_path = base_path / f"BDD_BGES_{site}" / f"PERSONNEL_{site}.txt"
        df = pd.read_csv(str(file_path), sep=';')
        clean_langue_fonction(df, site) 
        df['ID_SITE'] = site
        
        personnel_dfs.append(df)

    # On combine les dataframes 
    personnel_df = pd.concat(personnel_dfs)
  
    # On sélectionne uniquement les colonnes nécessaires
    personnel_final_df = personnel_df[['ID_PERSONNEL','FONCTION_PERSONNEL', 'ID_SITE', 'DT_NAISS']]
    personnel_final_df = convertir_age_personnel(personnel_final_df)
    return personnel_final_df


# Fonction pour imputer les données manquantes des fichiers de matériel

def clean_materiel(df):
    df = df.copy()
    
    # Charger le dictionnaire modèle -> type (une seule fois à la première utilisation)
    if 'modele_to_type' not in globals():
        global modele_to_type
        impact_df = pd.read_csv("./data/BDD_BGES/materiel_informatique_impact.csv")
        modele_to_type = dict(zip(impact_df['Modèle'], impact_df['Type']))
    
    # Nettoyage des espaces blancs
    df['TYPE'] = df['TYPE'].astype(str).str.strip()
    df['MODELE'] = df['MODELE'].astype(str).str.strip()
    
    # Convertir en NaN si vide
    df['TYPE'] = df['TYPE'].replace('', pd.NA)
    df['MODELE'] = df['MODELE'].replace('', pd.NA)
    
    # Remplir les TYPE manquants en utilisant le MODELE
    def get_type_from_modele(row):
        if pd.notna(row['TYPE']):  # Si TYPE existe déjà
            return row['TYPE']
        if pd.notna(row['MODELE']):  # Si MODELE existe, on peut imputer TYPE
            return modele_to_type.get(row['MODELE'], None)
        return None
    
    df['TYPE'] = df.apply(get_type_from_modele, axis=1)
    
    # Remplir les MODELE manquants par "modèle par défaut"
    df['MODELE'] = df['MODELE'].fillna('modèle par défaut')
    
    # Remplir les TYPE restants manquants par une valeur par défaut 
    df['TYPE'] = df['TYPE'].fillna('Matériel Informatique')
    
    return df

# Fonction pour calculer les impacts du matériel

# On charge le fichier qui contient l'impact carbone du matériel informatique. 
IMPACT_MAT_INFO_DF = pd.read_csv("./data/BDD_BGES/materiel_informatique_impact.csv")

#Fonction pour retirer les accents et convertir en majuscules les noms de colonne (pour jointures ultérieures)
def remove_accents_and_uppercase(name):
    #Normaliser et retirer les accents
    normalized = unicodedata.normalize('NFD', name)
    without_accents = ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')
    return without_accents.upper()

# Convertir tous les noms de colonnes en majuscules sans accents pour pouvoir faire les jointures
IMPACT_MAT_INFO_DF.columns = [remove_accents_and_uppercase(c) for c in IMPACT_MAT_INFO_DF.columns]
IMPACT_MAT_INFO_DF['IMPACT'] = IMPACT_MAT_INFO_DF['IMPACT'].fillna(0)

# Fonction pour calculer et ajouter la colonne impact
def add_impact_materiel(mat_df, impact_df = IMPACT_MAT_INFO_DF):
    merged = mat_df.merge(
        impact_df[['TYPE', 'MODELE', 'IMPACT']],
        on=['TYPE', 'MODELE'],
        how='left'
    )
    mat_df['IMPACT'] = merged['IMPACT'].fillna(0).astype(float) / 1000


# Fonction de calcul des distances entre 2 villes avec geopy
# Dictionnaire des coefficients en fonction du mode de transport
COEFFS_DISTANCE = {
    "Train" : 1.2,
    "Taxi" : 1.2,
    "Transports en commun" : 1.5
}

# Dictionnaire de coordonnées pour éviter les appels répétés et la limitation API GeoPy
CITY_COORDS = {
    # Sites principaux
    ("Paris", "France"): (48.8566, 2.3522),
    ("Berlin", "Germany"): (52.5200, 13.4050),
    ("Berlin", "Allemagne"): (52.5200, 13.4050),
    ("London", "England"): (51.5074, -0.1278),
    ("New York", "USA"): (40.7128, -74.0060),
    ("New-York", "USA"): (40.7128, -74.0060),
    ("Los Angeles", "USA"): (34.0522, -118.2437),
    ("Shanghai", "China"): (31.2304, 121.4737),
    ("Marseille", "France"): (43.2965, 5.3698),
    ("Compiègne", "France"): (49.4144, 2.8259),
    ("Stockholm", "Sweden"): (59.3293, 18.0686),
    ("Stockholm", "Suède"): (59.3293, 18.0686),
    ("Helsinki", "Finland"): (60.1695, 24.9354),
    ("Helsinki", "Finlande"): (60.1695, 24.9354),
    ("Osaka", "Japan"): (34.6937, 135.5023),
    ("Tokyo", "Japan"): (35.6762, 139.6503),
    ("Melbourne", "Australia"): (-37.8136, 144.9631),
    ("Sydney", "Australia"): (-33.8688, 151.2093),
    ("Sidney", "Australia"): (-33.8688, 151.2093),
    ("Wellington", "New Zealand"): (-41.2865, 174.7762),
    ("Montreal", "Canada"): (45.5017, -73.5673),
    ("Vancouver", "Canada"): (49.2827, -123.1207),
    ("Washington", "USA"): (38.9072, -77.0369),
    ("Buenos Aires", "Argentina"): (-34.6037, -58.3816),
    ("Bogota", "Colombia"): (4.7110, -74.0721),
    ("Rio de Janeiro", "Brazil"): (-22.9068, -43.1729),
    ("Rabat", "Morocco"): (34.0209, -6.8416),
    ("Rabat", "Maroc"): (34.0209, -6.8416),
    ("Dubaï", "Emirats"): (25.2048, 55.2708),
    ("Mexico", "Mexico"): (19.4326, -99.1332),
    ("Tunis", "Tunisia"): (36.8065, 10.1686),
    ("Tunis", "Tunisie"): (36.8065, 10.1686),
    ("Sao Paulo", "Brazil"): (-23.5505, -46.6333),
    ("Stockholm", "Sweden"): (59.3293, 18.0686),
    ("Stockholm", "Suede"): (59.3293, 18.0686),
    ("Alger", "Algeria"): (36.7538, 3.0588),
    ("Auckland", "New Zealand"): (-37.0882, 174.8860),
    ("Bordeaux", "France"): (44.8378, -0.5792),
    ("Pekin", "China"): (39.9042, 116.4074),
    ("Beijing", "China"): (39.9042, 116.4074),
    ("Lille", "France"): (50.6292, 3.0573),
    ("Oslo", "Norvège"): (59.9139, 10.7522),
    ("Oslo", "Norway"): (59.9139, 10.7522),
    ("Lima", "Peru"): (-12.0464, -77.0428)
}

def get_distance_between_cities(ville_depart, pays_depart, ville_destination, pays_destination):
    try:      
        # Si c'est un trajet intra-ville, on estime la distance de manière aléatoire
        # avec une loi normale et des valeurs raisonnables
        if (ville_depart.lower() == ville_destination.lower() and pays_depart.lower() == pays_destination.lower()):
            moyenne = 8      
            ecart_type = 3   

            # Générer une distance estimée avec loi normale
            distance = np.random.normal(moyenne, ecart_type)

            # Éviter les distances négatives
            distance_km = 0 if distance < 0 else distance
            return distance_km
        
        # Si trajets entre 2 villes différentes : chercher dans le dictionnaire d'abord
        coords_depart = CITY_COORDS.get((ville_depart, pays_depart))
        coords_dest = CITY_COORDS.get((ville_destination, pays_destination))
        
        # Si ville de départ non trouvée, appeler Nominatim
        if not coords_depart:
            print("ville depart non présente: ", ville_depart)
            print("pays depart non présent: ", pays_depart)
            location_depart = geolocator.geocode(f"{ville_depart}, {pays_depart}", timeout=10)
            if location_depart:
                coords_depart = (location_depart.latitude, location_depart.longitude)
        
        # Si ville de destination non trouvée, appeler Nominatim
        if not coords_dest:
            print("ville arrivee non présente: ", ville_destination)
            print("pays arrivee non présent: ", pays_destination)
            location_destination = geolocator.geocode(f"{ville_destination}, {pays_destination}", timeout=10)
            if location_destination:
                coords_dest = (location_destination.latitude, location_destination.longitude)
        
        # Si les deux coordonnées ont été trouvées, calculer la distance
        if coords_depart and coords_dest:
            distance_km = geodesic(coords_depart, coords_dest).kilometers
            return distance_km
        else:
            return None
            
    except Exception as e:
        print(f"Erreur lors du calcul: {e}")
        return None
    

#Fonction permettant de calculer les emissions des missions
"""

Clarification du transport "transports en communs" : 

Sur le site labos1.5, on a plusieurs types de transports en commun, dont deux qui ne sont pas pris en compte 
dans la liste donnée dans le sujet (bus et bateau). Cependant, quand on regarde dans la liste des missions, 
on constate que les missions labellisées transport en commun ont toutes la même ville d'arrivée et de départ,
cf exécuter le code suivant : 

missions_df[(missions_df["TRANSPORT"] == "Transports en commun") & (missions_df["VILLE_DEPART"] != missions_df["VILLE_DESTINATION"])]

On considère donc que les trajets en transport peuvent être représentés par des trajets en bus. Sur le site 
de labo1.5 on trouve : 

Spécificité des déplacements en bus :
Nous faisons l’hypothèse que les trajets en bus inter-urbains seront majoritaires en terme de distances 
parcourues lors d’une mission, comparativement aux trajets en bus urbains. Les trajets inter-urbains étant 
moins émetteurs que les trajets urbains, nous prenons le facteur d’émission le moins élevé parmi les 3 facteurs
 disponibles dans la Base Carbone: c’est celui des bus dans des agglomérations de plus de 250 000 habitants.

Ce facteur sera donc utilisé pour les missions utilisant le type de transport "transports en commun".

"""
def get_emission(distance, transport, ar, pays_depart, pays_destination):
        #Chargement des fichiers permettant de récupérer les facteurs d'émission
        base_path = Path("data/facteurs_emission")
        fe_transports_en_commun_df = pd.read_csv(base_path / "fe_transports_en_commun.tsv", sep='\t')
        fe_vehicules_df = pd.read_csv(base_path / "fe_vehicules.tsv", sep='\t')
        fe_transports_en_commun_df.head(100)


        #Multiplicateur si le trajet est un aller-retour
        multAr = 2 if ar == "oui" else 1

        #Modification de la distance en fonction du moyen de transport
        if(transport == "Avion"):
            distance += 95
        else : 
            distance *= COEFFS_DISTANCE.get(transport)
        
        #Calcul du facteur et de l'emission totale en fonction du moyen de transport
        #On divise par 1000 à chaque fois pour renvoyer la quantité directement en tCO2e
        match transport:
            case "Avion":
                if distance < 1000:
                    facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "Court courrier (< 1000 km)"]["total"].iloc[0]
                elif distance < 3500:
                    facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "Moyen courrier (< 1001 - 3500km)"]["total"].iloc[0]
                else:
                    facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "Long courrier (> 3500 km)"]["total"].iloc[0]
                
                return distance*facteur*multAr/1000

            
            case "Train":
                if(pays_depart == "France"):
                    if(pays_destination == "France"):
                        if distance > 200 :
                            facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "TGV > 200 km"]["total"].iloc[0]
                        else:
                            facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "Train < 200 km"]["total"].iloc[0]
                    else:
                        facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "Train mixte France et international"]["total"].iloc[0]
                else:
                    if(pays_destination == "France"):
                        facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "Train mixte France et international"]["total"].iloc[0]
                    else:
                        facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "Train international"]["total"].iloc[0]
                
                return distance*facteur*multAr/1000
            
            case "Taxi":
                facteur = fe_vehicules_df[fe_vehicules_df["subsubcategory"] == "Motorisation inconnue"]["total"].iloc[0]
                #On calcule aussi les émissions pour le trajet aller (on condisère 2 personnes à bord)
                #et retour (on considère le chauffeur seul à bord)
                em = (distance * (1 + 1/2) * facteur) 
                return multAr*em/1000
            
            case "Transports en commun":
                facteur = fe_transports_en_commun_df[fe_transports_en_commun_df["subsubcategory"] == "Bus > 250 000 habitants"]["total"].iloc[0]
                return distance*facteur*multAr/1000
            

# Fonction pour extraire et traiter les données de matériel
def extract_materiel(date):
    sites = ["PARIS", "BERLIN", "LONDON", "NEWYORK", "SHANGHAI", "LOSANGELES"]
    base_path = Path("data/BDD_BGES")
    
    day_str = date.strftime("%Y%m%d")
    materiel_day_dfs = []
    
    # Boucle sur chaque site
    for site in sites:
        file_path = base_path / f"BDD_BGES_{site}/BDD_BGES_{site}_INFORMATIQUE/MATERIEL_INFORMATIQUE_{day_str}.txt"
        
        # Vérifier si le fichier existe avant de le lire
        if file_path.exists():
            df = pd.read_csv(str(file_path), sep=';')
            clean_date(df, site, "DATE_ACHAT")
            df = clean_materiel(df)  # Nettoyer et imputer données manquantes
            df['ID_DATE'] = df['DATE_ACHAT'].dt.date
            add_impact_materiel(df)
            materiel_day_dfs.append(df)
            
    # Si des fichiers ont été trouvés pour ce jour
    if materiel_day_dfs:
        return pd.concat(materiel_day_dfs, ignore_index=True)
    else:
        print(f"Aucun fichier de matériel trouvé pour {day_str}.")
        return None


# Fonction pour extraire et traiter les données des missions
# Même logique que la fonction d'extraction du matériel
def extract_missions(date):
    sites = ["PARIS", "BERLIN", "LONDON", "NEWYORK", "SHANGHAI", "LOSANGELES"]
    base_path = Path("data/BDD_BGES")
    
    day_str = date.strftime("%Y%m%d")
    missions_day_dfs = []
    
    for site in sites:
        file_path = base_path / f"BDD_BGES_{site}/BDD_BGES_{site}_MISSION/MISSION_{day_str}.txt"
        
        if file_path.exists():
            df = pd.read_csv(str(file_path), sep=';')
            clean_langue_mission(df, site)
            clean_date(df, site, "DATE_MISSION")
            df['ID_SITE'] = site
            df['ID_DATE'] = df['DATE_MISSION'].dt.date # Pour jointure
            # Calcul de la distance entre les villes depart et destination
            df['DISTANCE_KM'] = df.apply(
                lambda row: get_distance_between_cities(
                    row['VILLE_DEPART'],
                    row['PAYS_DEPART'],
                    row['VILLE_DESTINATION'],
                    row['PAYS_DESTINATION'],
                ),
                axis=1
            )
            # Calcul de l'emission des missions
            df['EMISSION'] = df.apply(
                lambda row: get_emission(
                    row['DISTANCE_KM'],
                    row['TRANSPORT'],
                    row['ALLER_RETOUR'],
                    row['PAYS_DEPART'],
                    row['PAYS_DESTINATION']
                ),
                axis=1
            )
            missions_day_dfs.append(df)
            
    if missions_day_dfs:
        return pd.concat(missions_day_dfs, ignore_index=True)
    else:
        print(f"Aucun fichier de missions trouvé pour {day_str}.")
        return None
    
def get_date_range_from_bges(root_path="data/BDD_BGES"):
    root = Path(root_path)
    
    # Chercher tous les fichiers de missions et matériel
    mission_files = list(root.rglob("MISSION_*.txt"))
    materiel_files = list(root.rglob("MATERIEL_INFORMATIQUE_*.txt"))
    
    all_files = mission_files + materiel_files
    
    if not all_files:
        print(f"Aucun fichier trouvé dans {root_path}")
        return None, None
    
    # Extraire les dates des noms de fichiers
    dates = []
    
    for fichier in all_files:
        stem = fichier.stem  # ex: 'MISSION_20260429' ou 'MATERIEL_INFORMATIQUE_20260429'
        # Extraire la partie YYYYMMDD (8 derniers caractères du stem)
        candidate = stem.split('_')[-1]
        
        if len(candidate) == 8 and candidate.isdigit():
            try:
                date_obj = pd.to_datetime(candidate, format="%Y%m%d")
                dates.append(date_obj)
            except:
                print(f"Impossible de parser: {fichier.name}")
    
    if not dates:
        print("Aucune date valide trouvée dans les noms de fichiers.")
        return None, None
    
    dates = pd.to_datetime(dates)
    earliest = dates.min().date()
    latest = dates.max().date()
    
    return earliest, latest