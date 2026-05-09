"""
Fichier contenant les fonctions pour charger et interroger le modèle étoile BGES, créé dans
le notebook ETL. 
Charge les tables de dimension et de fait depuis les fichiers Parquet
et contient des fonctions pour répondre aux questions analytiques.

Utilise UNIQUEMENT Pandas pour éviter les problèmes Spark sur Windows.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

# CHARGEMENT DES DONNÉES
DATA_PATH = Path(__file__).parent / "star_model_data"
FACTORS_PATH = Path(__file__).parent.parent / "data" / "facteurs_emission"

# Même logique que dans ETL.ipynb
COEFFS_DISTANCE = {
    "Train": 1.2,
    "Taxi": 1.2,
    "Transports en commun": 1.5,
}

# Coordonnées statiques pour éviter les appels réseau depuis le dashboard
CITY_COORDS = {
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
    ("Mexico", "Mexico"): (19.4326, -99.1332),
    ("Tunis", "Tunisia"): (36.8065, 10.1686),
    ("Tunis", "Tunisie"): (36.8065, 10.1686),
    ("Sao Paulo", "Brazil"): (-23.5505, -46.6333),
    ("Alger", "Algeria"): (36.7538, 3.0588),
    ("Auckland", "New Zealand"): (-37.0882, 174.8860),
    ("Bordeaux", "France"): (44.8378, -0.5792),
    ("Pekin", "China"): (39.9042, 116.4074),
    ("Beijing", "China"): (39.9042, 116.4074),
    ("Lille", "France"): (50.6292, 3.0573),
    ("Oslo", "Norvège"): (59.9139, 10.7522),
    ("Oslo", "Norway"): (59.9139, 10.7522),
    ("Lima", "Peru"): (-12.0464, -77.0428),
}


@st.cache_data
def load_emission_factors():
    fe_transports = pd.read_csv(FACTORS_PATH / "fe_transports_en_commun.tsv", sep="\t")
    fe_vehicules = pd.read_csv(FACTORS_PATH / "fe_vehicules.tsv", sep="\t")
    return fe_transports, fe_vehicules


def _safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _haversine_km(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_km * c


def _get_distance_km(ville_depart, pays_depart, ville_destination, pays_destination):
    if not ville_depart or not ville_destination or not pays_depart or not pays_destination:
        return 0.0

    vd = str(ville_depart)
    pdp = str(pays_depart)
    va = str(ville_destination)
    pds = str(pays_destination)

    if vd.lower() == va.lower() and pdp.lower() == pds.lower():
        return 8.0

    coords_depart = CITY_COORDS.get((vd, pdp))
    coords_dest = CITY_COORDS.get((va, pds))
    if not coords_depart or not coords_dest:
        return 0.0

    return _haversine_km(coords_depart[0], coords_depart[1], coords_dest[0], coords_dest[1])


def _get_factor(fe_df, subsubcategory):
    rows = fe_df[fe_df["subsubcategory"] == subsubcategory]
    if rows.empty:
        return 0.0
    return _safe_float(rows["total"].iloc[0])


def _compute_mission_emission_tco2e(row, fe_transports, fe_vehicules):
    transport = row.get("TRANSPORT", "")
    pays_depart = row.get("PAYS_DEPART", "")
    pays_destination = row.get("PAYS_DESTINATION", "")
    aller_retour = str(row.get("ALLER_RETOUR", "non")).strip().lower()
    mult_ar = 2 if aller_retour == "oui" else 1

    if "DISTANCE_KM" in row and not pd.isna(row["DISTANCE_KM"]):
        distance = _safe_float(row["DISTANCE_KM"])
    else:
        distance = _get_distance_km(
            row.get("VILLE_DEPART", ""),
            row.get("PAYS_DEPART", ""),
            row.get("VILLE_DESTINATION", ""),
            row.get("PAYS_DESTINATION", ""),
        )

    if transport == "Avion":
        distance_adjusted = distance + 95
        if distance_adjusted < 1000:
            facteur = _get_factor(fe_transports, "Court courrier (< 1000 km)")
        elif distance_adjusted < 3500:
            facteur = _get_factor(fe_transports, "Moyen courrier (< 1001 - 3500km)")
        else:
            facteur = _get_factor(fe_transports, "Long courrier (> 3500 km)")
        return distance_adjusted * facteur * mult_ar / 1000

    distance_adjusted = distance * COEFFS_DISTANCE.get(transport, 1.0)

    if transport == "Train":
        if pays_depart == "France":
            if pays_destination == "France":
                if distance_adjusted > 200:
                    facteur = _get_factor(fe_transports, "TGV > 200 km")
                else:
                    facteur = _get_factor(fe_transports, "Train < 200 km")
            else:
                facteur = _get_factor(fe_transports, "Train mixte France et international")
        else:
            if pays_destination == "France":
                facteur = _get_factor(fe_transports, "Train mixte France et international")
            else:
                facteur = _get_factor(fe_transports, "Train international")
        return distance_adjusted * facteur * mult_ar / 1000

    if transport == "Taxi":
        facteur = _get_factor(fe_vehicules, "Motorisation inconnue")
        em = distance_adjusted * (1 + 1 / 2) * facteur
        return mult_ar * em / 1000

    if transport == "Transports en commun":
        facteur = _get_factor(fe_transports, "Bus > 250 000 habitants")
        return distance_adjusted * facteur * mult_ar / 1000

    return 0.0

@st.cache_data
def load_star_model():
    try:
        # Charger les tables de dimension
        dim_personnel = pd.read_parquet(str(DATA_PATH / "dim_personnel"))
        dim_mission = pd.read_parquet(str(DATA_PATH / "dim_mission"))
        dim_materiel = pd.read_parquet(str(DATA_PATH / "dim_materiel"))
        dim_site = pd.read_parquet(str(DATA_PATH / "dim_site"))
        dim_date = pd.read_parquet(str(DATA_PATH / "dim_date"))
        
        # Charger les tables de fait
        fait_mission = pd.read_parquet(str(DATA_PATH / "fait_mission"))
        fait_materiel = pd.read_parquet(str(DATA_PATH / "fait_materiel"))
        
        # Charger les données de référence
        impact_materiel_ref = pd.read_parquet(str(DATA_PATH / "impact_materiel_ref"))
        
        return {
            "dim_personnel": dim_personnel,
            "dim_mission": dim_mission,
            "dim_materiel": dim_materiel,
            "dim_site": dim_site,
            "dim_date": dim_date,
            "fait_mission": fait_mission,
            "fait_materiel": fait_materiel,
            "impact_materiel_ref": impact_materiel_ref,
        }
    except FileNotFoundError as e:
        st.error(f"Fichiers Parquet non trouvés: {e}")
        st.info("Attention à bien exécuter les cellules d'export du notebook ETL.ipynb.")
        return None


# FONCTIONS D'INTERROGATION DU MODÈLE

def query_q1(tables):
    """Q1: Combien de cadres travaillent sur le site de Paris ?"""
    if tables is None:
        return 0
    result = tables["dim_personnel"][
        (tables["dim_personnel"]["ID_SITE"] == "PARIS") & 
        (tables["dim_personnel"]["FONCTION_PERSONNEL"] == "Business Executive")
    ]
    return len(result)

def query_q2(tables):
    """Q2: Combien d'ingénieurs Data travaillent sur les sites aux États-Unis ?"""
    if tables is None:
        return 0
    result = tables["dim_personnel"][
        (tables["dim_personnel"]["ID_SITE"].isin(["LOSANGELES", "NEWYORK"])) & 
        (tables["dim_personnel"]["FONCTION_PERSONNEL"] == "Data Engineer")
    ]
    return len(result)

def query_q3(tables):
    """Q3: Combien d'ingénieurs informaticiens travaillent dans l'organisation ?"""
    if tables is None:
        return 0
    result = tables["dim_personnel"][
        tables["dim_personnel"]["FONCTION_PERSONNEL"] == "Computer Engineer"
    ]
    return len(result)

def query_q4(tables):
    """Q4: Combien de PC fixes ont été achetés entre juin et septembre 2026 ?"""
    if tables is None:
        return 0
    
    # Filtrer le matériel PC fixe
    materiel_pc_fixe = tables["dim_materiel"][
        (tables["dim_materiel"]["TYPE"] == "PC fixe sans ecran") | 
        (tables["dim_materiel"]["TYPE"] == "PC fixe tout-en-un")
    ]
    
    # Joindre avec les faits matériel
    joined = tables["fait_materiel"].merge(
        materiel_pc_fixe[["ID_MATERIEL"]], 
        on="ID_MATERIEL", 
        how="inner"
    )
    
    # Convertir les dates pour la comparaison
    joined["ID_DATE_ACHAT"] = pd.to_datetime(joined["ID_DATE_ACHAT"])
    
    # Filtrer par dates (entre juin et septembre 2026)
    result = joined[
        (joined["ID_DATE_ACHAT"] >= pd.to_datetime("2026-06-01")) & 
        (joined["ID_DATE_ACHAT"] <= pd.to_datetime("2026-09-30"))
    ]
    return len(result)

def query_q5(tables):
    """Q5: Impact carbone des PC fixes sans écran entre mai et octobre 2026."""
    if tables is None:
        return 0.0
    
    # Filtrer PC fixe sans écran
    materiel = tables["dim_materiel"][
        tables["dim_materiel"]["TYPE"] == "PC fixe sans ecran"
    ]
    
    # Joindre avec faits matériel
    joined = tables["fait_materiel"].merge(
        materiel[["ID_MATERIEL", "TYPE", "MODELE"]], 
        on="ID_MATERIEL", 
        how="inner"
    )
    
    # Convertir les dates pour la comparaison
    joined["ID_DATE_ACHAT"] = pd.to_datetime(joined["ID_DATE_ACHAT"])
    
    # Filtrer dates mai-oct 2026
    joined = joined[
        (joined["ID_DATE_ACHAT"] >= pd.to_datetime("2026-05-01")) & 
        (joined["ID_DATE_ACHAT"] <= pd.to_datetime("2026-10-31"))
    ]
    
    # Joindre avec impact matériel reference
    result_df = joined.merge(
        tables["impact_materiel_ref"],
        on=["TYPE", "MODELE"],
        how="left"
    )
    
    # Calculer impact total (kg en tCO2e)
    if result_df.empty or "IMPACT" not in result_df.columns:
        return 0.0
    return float(result_df["IMPACT"].sum() / 1000)

def query_q6(tables):
    """Q6: Impact carbone des PC portables Ing. Data LON+NY mai-oct 2026."""
    if tables is None:
        return 0.0
    
    # Filtrer Data Engineers sur LON+NY
    personnel = tables["dim_personnel"][
        (tables["dim_personnel"]["ID_SITE"].isin(["LONDON", "NEWYORK"])) & 
        (tables["dim_personnel"]["FONCTION_PERSONNEL"] == "Data Engineer")
    ]
    
    # Joindre avec faits matériel
    joined = tables["fait_materiel"].merge(
        personnel[["ID_PERSONNEL"]], 
        on="ID_PERSONNEL", 
        how="inner"
    )
    
    # Convertir les dates pour la comparaison
    joined["ID_DATE_ACHAT"] = pd.to_datetime(joined["ID_DATE_ACHAT"])
    
    # Filtrer dates mai-oct 2026
    joined = joined[
        (joined["ID_DATE_ACHAT"] >= pd.to_datetime("2026-05-01")) & 
        (joined["ID_DATE_ACHAT"] <= pd.to_datetime("2026-10-31"))
    ]
    
    # Joindre avec dim_materiel et filtrer PC portable
    joined = joined.merge(
        tables["dim_materiel"][["ID_MATERIEL", "TYPE", "MODELE"]], 
        on="ID_MATERIEL", 
        how="inner"
    )
    joined = joined[joined["TYPE"] == "PC portable"]
    
    # Joindre avec impact reference
    result_df = joined.merge(
        tables["impact_materiel_ref"],
        on=["TYPE", "MODELE"],
        how="left"
    )
    
    if result_df.empty or "IMPACT" not in result_df.columns:
        return 0.0
    return float(result_df["IMPACT"].sum() / 1000)

def query_q7(tables):
    """Q7: Impact carbone des écrans cadres juil-sep 2026."""
    if tables is None:
        return 0.0
    
    # Filtrer Business Executives
    personnel = tables["dim_personnel"][
        tables["dim_personnel"]["FONCTION_PERSONNEL"] == "Business Executive"
    ]
    
    # Joindre avec faits matériel
    joined = tables["fait_materiel"].merge(
        personnel[["ID_PERSONNEL"]], 
        on="ID_PERSONNEL", 
        how="inner"
    )
    
    # Convertir les dates pour la comparaison
    joined["ID_DATE_ACHAT"] = pd.to_datetime(joined["ID_DATE_ACHAT"])
    
    # Filtrer dates juil-sep 2026
    joined = joined[
        (joined["ID_DATE_ACHAT"] >= pd.to_datetime("2026-07-01")) & 
        (joined["ID_DATE_ACHAT"] <= pd.to_datetime("2026-09-30"))
    ]
    
    # Joindre avec dim_materiel et filtrer écrans
    joined = joined.merge(
        tables["dim_materiel"][["ID_MATERIEL", "TYPE", "MODELE"]], 
        on="ID_MATERIEL", 
        how="inner"
    )
    joined = joined[joined["TYPE"] == "Ecran"]
    
    # Joindre avec impact reference
    result_df = joined.merge(
        tables["impact_materiel_ref"],
        on=["TYPE", "MODELE"],
        how="left"
    )
    
    if result_df.empty or "IMPACT" not in result_df.columns:
        return 0.0
    return float(result_df["IMPACT"].sum() / 1000)

def query_personnel_by_fonction(tables):
    """Récupère le nombre de personnel par fonction."""
    if tables is None:
        return pd.DataFrame()
    result = tables["dim_personnel"].groupby("FONCTION_PERSONNEL").size().reset_index(name="count")
    return result.sort_values("count", ascending=False)

def query_personnel_by_site_fonction(tables):
    """Récupère le nombre de personnel par site et fonction."""
    if tables is None:
        return pd.DataFrame()
    result = tables["dim_personnel"].groupby(["ID_SITE", "FONCTION_PERSONNEL"]).size().reset_index(name="count")
    return result

def query_missions_summary(tables):
    """Récupère un résumé des missions."""
    if tables is None:
        return pd.DataFrame()
    result = tables["dim_mission"].merge(
        tables["fait_mission"], 
        on="ID_MISSION", 
        how="inner"
    )
    return result

def query_materiel_summary(tables):
    """Récupère un résumé du matériel informatique."""
    if tables is None:
        return pd.DataFrame()
    result = tables["dim_materiel"].merge(
        tables["fait_materiel"], 
        on="ID_MATERIEL", 
        how="inner"
    )
    return result


# FONCTIONS GÉNÉRIQUES PARAMÉTRABLES POUR CALCULER L'IMPACT

def calculate_materiel_impact(
    tables, 
    materiel_types=None, 
    date_start=None, 
    date_end=None, 
    sites=None, 
    fonctions_personnel=None
):
    if tables is None:
        return 0.0

    try:
        result = tables["fait_materiel"].merge(
            tables["dim_materiel"][["ID_MATERIEL", "TYPE", "MODELE"]],
            on="ID_MATERIEL",
            how="inner",
        )

        if materiel_types:
            result = result[result["TYPE"].isin(materiel_types)]

        if date_start or date_end:
            result["ID_DATE_ACHAT"] = pd.to_datetime(result["ID_DATE_ACHAT"])
            if date_start:
                result = result[result["ID_DATE_ACHAT"] >= pd.to_datetime(date_start)]
            if date_end:
                result = result[result["ID_DATE_ACHAT"] <= pd.to_datetime(date_end)]

        if sites or fonctions_personnel:
            result = result.merge(
                tables["dim_personnel"][["ID_PERSONNEL", "ID_SITE", "FONCTION_PERSONNEL"]],
                on="ID_PERSONNEL",
                how="left",
            )
            if sites:
                result = result[result["ID_SITE"].isin(sites)]
            if fonctions_personnel:
                result = result[result["FONCTION_PERSONNEL"].isin(fonctions_personnel)]

        result = result.merge(
            tables["impact_materiel_ref"][["TYPE", "MODELE", "IMPACT"]],
            on=["TYPE", "MODELE"],
            how="left",
        )

        if result.empty or "IMPACT" not in result.columns:
            return 0.0
        return float(pd.to_numeric(result["IMPACT"], errors="coerce").fillna(0).sum() / 1000)

    except Exception as e:
        print(f"Erreur lors du calcul d'impact matériel : {e}")
        return 0.0


def calculate_mission_impact(
    tables, 
    mission_types=None, 
    date_start=None, 
    date_end=None, 
    sites_depart=None, 
    sites_destination=None, 
    transports=None
):
    if tables is None:
        return 0.0

    try:
        result = tables["dim_mission"].merge(
            tables["fait_mission"],
            on="ID_MISSION",
            how="inner",
        )

        if mission_types:
            result = result[result["TYPE_MISSION"].isin(mission_types)]

        if date_start or date_end:
            result["ID_DATE_MISSION"] = pd.to_datetime(result["ID_DATE_MISSION"])
            if date_start:
                result = result[result["ID_DATE_MISSION"] >= pd.to_datetime(date_start)]
            if date_end:
                result = result[result["ID_DATE_MISSION"] <= pd.to_datetime(date_end)]

        if sites_depart:
            if "ID_SITE" in result.columns:
                result = result[result["ID_SITE"].isin(sites_depart)]
            elif "VILLE_DEPART" in result.columns:
                result = result[result["VILLE_DEPART"].isin(sites_depart)]
        if sites_destination and "VILLE_DESTINATION" in result.columns:
            result = result[result["VILLE_DESTINATION"].isin(sites_destination)]
        if transports:
            result = result[result["TRANSPORT"].isin(transports)]

        if result.empty:
            return 0.0

        fe_transports, fe_vehicules = load_emission_factors()
        result["EMISSION_CALC"] = result.apply(
            lambda row: _compute_mission_emission_tco2e(row, fe_transports, fe_vehicules),
            axis=1,
        )
        return float(pd.to_numeric(result["EMISSION_CALC"], errors="coerce").fillna(0).sum())

    except Exception as e:
        print(f"Erreur lors du calcul d'impact mission : {e}")
        return 0.0


def calculate_total_impact(tables, date_start=None, date_end=None):
    if tables is None:
        return 0.0, 0.0, 0.0
    
    try:
        impact_materiel = calculate_materiel_impact(tables, date_start=date_start, date_end=date_end)
        impact_missions = calculate_mission_impact(tables, date_start=date_start, date_end=date_end)
        impact_total = impact_materiel + impact_missions
        
        return float(impact_total), float(impact_materiel), float(impact_missions)
    
    except Exception as e:
        print(f"Erreur lors du calcul d'impact total : {e}")
        return 0.0, 0.0, 0.0


def calculate_materiel_impact_by_category(tables, date_start=None, date_end=None):
    if tables is None:
        return pd.DataFrame()

    try:
        result = tables["fait_materiel"].merge(
            tables["dim_materiel"][["ID_MATERIEL", "TYPE", "MODELE"]],
            on="ID_MATERIEL",
            how="inner",
        ).merge(
            tables["impact_materiel_ref"][["TYPE", "MODELE", "IMPACT"]],
            on=["TYPE", "MODELE"],
            how="left",
        )

        if date_start or date_end:
            result["ID_DATE_ACHAT"] = pd.to_datetime(result["ID_DATE_ACHAT"])
            if date_start:
                result = result[result["ID_DATE_ACHAT"] >= pd.to_datetime(date_start)]
            if date_end:
                result = result[result["ID_DATE_ACHAT"] <= pd.to_datetime(date_end)]

        result["IMPACT"] = pd.to_numeric(result["IMPACT"], errors="coerce").fillna(0) / 1000
        impact_by_type = result.groupby("TYPE", as_index=False)["IMPACT"].sum()
        return impact_by_type.sort_values("IMPACT", ascending=False)

    except Exception as e:
        print(f"Erreur lors du calcul d'impact par catégorie : {e}")
        return pd.DataFrame()


def calculate_mission_impact_by_transport(tables, date_start=None, date_end=None):
    if tables is None:
        return pd.DataFrame()

    try:
        result = tables["dim_mission"].merge(
            tables["fait_mission"],
            on="ID_MISSION",
            how="inner",
        )

        if date_start or date_end:
            result["ID_DATE_MISSION"] = pd.to_datetime(result["ID_DATE_MISSION"])
            if date_start:
                result = result[result["ID_DATE_MISSION"] >= pd.to_datetime(date_start)]
            if date_end:
                result = result[result["ID_DATE_MISSION"] <= pd.to_datetime(date_end)]

        fe_transports, fe_vehicules = load_emission_factors()
        result["EMISSION_CALC"] = result.apply(
            lambda row: _compute_mission_emission_tco2e(row, fe_transports, fe_vehicules),
            axis=1,
        )

        impact_by_transport = result.groupby("TRANSPORT", as_index=False)["EMISSION_CALC"].sum()
        impact_by_transport.columns = ["TRANSPORT", "IMPACT"]
        return impact_by_transport.sort_values("IMPACT", ascending=False)

    except Exception as e:
        print(f"Erreur lors du calcul d'impact par transport : {e}")
        return pd.DataFrame()


def calculate_materiel_impact_by_site(tables, date_start=None, date_end=None):
    if tables is None:
        return pd.DataFrame()

    try:
        result = tables["fait_materiel"].merge(
            tables["dim_materiel"][["ID_MATERIEL", "TYPE", "MODELE"]],
            on="ID_MATERIEL",
            how="inner",
        ).merge(
            tables["dim_personnel"][["ID_PERSONNEL", "ID_SITE"]],
            on="ID_PERSONNEL",
            how="left",
        ).merge(
            tables["impact_materiel_ref"][["TYPE", "MODELE", "IMPACT"]],
            on=["TYPE", "MODELE"],
            how="left",
        )

        if date_start or date_end:
            result["ID_DATE_ACHAT"] = pd.to_datetime(result["ID_DATE_ACHAT"])
            if date_start:
                result = result[result["ID_DATE_ACHAT"] >= pd.to_datetime(date_start)]
            if date_end:
                result = result[result["ID_DATE_ACHAT"] <= pd.to_datetime(date_end)]

        result["IMPACT"] = pd.to_numeric(result["IMPACT"], errors="coerce").fillna(0) / 1000
        impact_by_site = result.groupby("ID_SITE", as_index=False)["IMPACT"].sum()
        impact_by_site.columns = ["SITE", "IMPACT"]
        return impact_by_site.sort_values("IMPACT", ascending=False)

    except Exception as e:
        print(f"Erreur lors du calcul d'impact par site : {e}")
        return pd.DataFrame()


# FONCTION PRINCIPALE DE CHARGEMENT
def init_star_model():
    if not DATA_PATH.exists():
        st.error(f"Le dossier {DATA_PATH} n'existe pas. Assurez-vous d'exécuter la cellule d'export du notebook ETL.ipynb.")
        return None
    
    try:
        tables = load_star_model()
        return tables
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle étoile : {e}")
        return None
