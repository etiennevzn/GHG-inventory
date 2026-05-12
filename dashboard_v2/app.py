import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
import time

# Configuration Streamlit
st.set_page_config(page_title="Dashboard Inventaire GES", layout="wide", initial_sidebar_state="expanded")
st.title("Dashboard - Bilan Gaz à Effet de Serre")

# Réduire l'espace vide en bas de page et cacher le footer Streamlit
st.markdown(
        """
        <style>
            /* Réduit le padding bottom du conteneur principal */
            .block-container { padding-bottom: 1rem !important; }
            /* Hide Streamlit footer to reclaim space */
            .stApp footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
)

# ============================================================================
# CHARGEMENT DES DONNÉES PARQUET
# ============================================================================

@st.cache_data
def load_data():
    """Charge les tables du modèle étoile depuis les fichiers Parquet"""
    data_path = Path("star_model_data")
    
    dim_personnel = pd.read_parquet(data_path / "dim_personnel")
    dim_mission = pd.read_parquet(data_path / "dim_mission")
    dim_materiel = pd.read_parquet(data_path / "dim_materiel")
    dim_site = pd.read_parquet(data_path / "dim_site")
    dim_date = pd.read_parquet(data_path / "dim_date")
    fait_mission = pd.read_parquet(data_path / "fait_mission")
    fait_materiel = pd.read_parquet(data_path / "fait_materiel")
    
    # Convertir les colonnes de dates en datetime
    dim_date['ID_DATE'] = pd.to_datetime(dim_date['ID_DATE'])
    fait_mission['ID_DATE_MISSION'] = pd.to_datetime(fait_mission['ID_DATE_MISSION'])
    fait_materiel['ID_DATE_ACHAT'] = pd.to_datetime(fait_materiel['ID_DATE_ACHAT'])
    
    return {
        'dim_personnel': dim_personnel,
        'dim_mission': dim_mission,
        'dim_materiel': dim_materiel,
        'dim_site': dim_site,
        'dim_date': dim_date,
        'fait_mission': fait_mission,
        'fait_materiel': fait_materiel,
    }

# Charger les données
data = load_data()
dp = data['dim_personnel']
dm = data['dim_mission']
dma = data['dim_materiel']
ds = data['dim_site']
dd = data['dim_date']
fm = data['fait_mission']
fma = data['fait_materiel']

# ============================================================================
# BARRE LATÉRALE - FILTRES GLOBAUX
# ============================================================================

st.sidebar.header("Filtres")

# Filtres de dates
min_date = dd['ID_DATE'].min()
max_date = dd['ID_DATE'].max()
min_value = min_date if isinstance(min_date, date) else min_date.date()
max_value = max_date if isinstance(max_date, date) else max_date.date()

date_range = st.sidebar.date_input(
    "Plage de dates",
    value=(date(2026, 4, 28), date(2026, 11, 15)),
    min_value=min_value,
    max_value=max_value
)

# Filtres par site
sites = sorted(ds['ID_SITE'].unique())
selected_sites = st.sidebar.multiselect(
    "Sites",
    sites,
    default=sites
)

# Filtres par fonction
fonctions = sorted(dp['FONCTION_PERSONNEL'].unique())
selected_fonctions = st.sidebar.multiselect(
    "Fonctions",
    fonctions,
    default=fonctions
)

# Filtres par type de transport
transports = sorted(dm['TRANSPORT'].dropna().unique())
selected_transports = st.sidebar.multiselect(
    "Type de transport",
    transports,
    default=transports
)

# ============================================================================
# PRÉPARATION DES DONNÉES FILTRÉES
# ============================================================================

# Filtrer les dates
date_min = pd.Timestamp(date_range[0])
date_max = pd.Timestamp(date_range[1])
dd_filtered = dd[(dd['ID_DATE'] >= date_min) & (dd['ID_DATE'] <= date_max)]

# Filtrer les sites et fonctions dans les dimensions
dp_filtered = dp[dp['ID_SITE'].isin(selected_sites) & dp['FONCTION_PERSONNEL'].isin(selected_fonctions)]

# Joindre les faits avec les dimensions filtrées
fm_joined = fm.merge(dm, on='ID_MISSION', how='left')
fm_joined = fm_joined.merge(dd_filtered[['ID_DATE']], left_on='ID_DATE_MISSION', right_on='ID_DATE', how='inner')
fm_joined = fm_joined[fm_joined['ID_SITE'].isin(selected_sites)]
# Appliquer filtre transports si défini
if selected_transports:
    fm_joined = fm_joined[fm_joined['TRANSPORT'].isin(selected_transports)]

# Copier une vue des missions filtrées pour réutilisation
fm_missions = fm_joined.copy()

fma_joined = fma.merge(dma, on='ID_MATERIEL', how='left')
fma_joined = fma_joined.merge(dd_filtered[['ID_DATE']], left_on='ID_DATE_ACHAT', right_on='ID_DATE', how='inner')
fma_joined = fma_joined.merge(dp_filtered[['ID_PERSONNEL', 'FONCTION_PERSONNEL']], on='ID_PERSONNEL', how='left')
fma_joined = fma_joined[fma_joined['ID_SITE'].isin(selected_sites)]

# ============================================================================
# ONGLETS PRINCIPAUX
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Aperçu",
    "Personnel et Sites",
    "Matériel Informatique",
    "Missions",
    "Questions"
])

# ============================================================================
# ONGLET 1 - APERÇU
# ============================================================================

with tab1:
    st.header("Aperçu Global")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_impact_missions = fm_joined['EMISSION'].sum()
        st.metric("Impact Missions (tCO₂e)", f"{total_impact_missions:.2f}")
    
    with col2:
        total_impact_materiel = fma_joined['IMPACT'].sum()
        st.metric("Impact Matériel (tCO₂e)", f"{total_impact_materiel:.2f}")
    
    with col3:
        total_impact = total_impact_missions + total_impact_materiel
        st.metric("Impact Total (tCO₂e)", f"{total_impact:.2f}")
    
    with col4:
        nb_employes = dp_filtered['ID_PERSONNEL'].nunique()
        st.metric("Employés", nb_employes)
    
    # Impact mensuel global
    st.subheader("Impact Mensuel Global")
    
    # Missions mensuelles
    fm_monthly = fm_joined.copy()
    fm_monthly['MOIS'] = pd.to_datetime(fm_monthly['ID_DATE_MISSION']).dt.to_period('M')
    missions_monthly = fm_monthly.groupby('MOIS')['EMISSION'].sum().reset_index()
    missions_monthly['MOIS'] = missions_monthly['MOIS'].astype(str)
    
    # Matériel mensuel
    fma_monthly = fma_joined.copy()
    fma_monthly['MOIS'] = pd.to_datetime(fma_monthly['ID_DATE_ACHAT']).dt.to_period('M')
    materiel_monthly = fma_monthly.groupby('MOIS')['IMPACT'].sum().reset_index()
    materiel_monthly['MOIS'] = materiel_monthly['MOIS'].astype(str)
    
    # Fusion
    monthly_data = missions_monthly.merge(
        materiel_monthly,
        on='MOIS',
        how='outer'
    ).fillna(0)
    monthly_data['Total'] = monthly_data['EMISSION'] + monthly_data['IMPACT']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_data['MOIS'], y=monthly_data['EMISSION'], name='Missions'))
    fig.add_trace(go.Bar(x=monthly_data['MOIS'], y=monthly_data['IMPACT'], name='Matériel'))
    # Ligne total (missions + matériel)
    fig.add_trace(go.Scatter(
        x=monthly_data['MOIS'],
        y=monthly_data['Total'],
        name='Total',
        mode='lines+markers',
        line=dict(color='red', width=3)
    ))
    fig.update_layout(
        title="Impact Carbone Mensuel (Missions + Matériel)",
        barmode='stack',
        xaxis_title="Mois",
        yaxis_title="Impact (tCO₂e)",
        height=500,
        margin=dict(t=50, b=60, l=60, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Carte mondiale: trajets (toutes les missions lorsque possible) et points pour les 6 sites
    st.subheader("Cartes des trajets de missions")
    # Coordonnées approximatives pour les 6 sites
    site_coords = {
        "Paris": (48.8566, 2.3522),
        "London": (51.5074, -0.1278),
        "Berlin": (52.5200, 13.4050),
        "Los Angeles": (34.0522, -118.2437),
        "New-York": (40.7128, -74.0060),
        "Shanghai": (31.2304, 121.4737)
    }

    # Table de rattrapage pour quelques grandes villes courantes (ajoutez si nécessaire)
    extra_coords = {
        "Paris": site_coords['Paris'],
        "London": site_coords['London'],
        "Berlin": site_coords['Berlin'],
        "Los Angeles": site_coords['Los Angeles'],
        "New-York": site_coords['New-York'],
        "New York": site_coords['New-York'],
        "NewYork": site_coords['New-York'],
        "Shanghai": site_coords['Shanghai'],
        "LosAngeles": site_coords['Los Angeles'],
        "Newyork": site_coords['New-York']
    }

    # Construire un mapping canonique pour chercher rapidement
    def canon(s):
        return ''.join(ch.lower() for ch in str(s) if ch.isalnum())

    # Dictionnaire étendu fourni (ville, pays) -> (lat, lon)
    extended_coords = {
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

    # Build canonical mapping from city names (and variants) to coords
    canonical_coords = {}
    for k, v in {**site_coords, **extra_coords}.items():
        canonical_coords[canon(k)] = v
    for (city, country), coord in extended_coords.items():
        canonical_coords[canon(city)] = coord
        canonical_coords[canon(f"{city}{country}")] = coord

    # Optionnel: essayer de géocoder dynamiquement les villes inconnues via geopy
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="ghg_dashboard")
        geopy_available = True
    except Exception:
        geopy_available = False

    geocode_cache = {}

    def geocode_city(name):
        key = canon(name)
        if key in geocode_cache:
            return geocode_cache[key]
        if not geopy_available:
            return None
        try:
            loc = geolocator.geocode(name, timeout=10)
            time.sleep(1)
            if loc:
                coord = (loc.latitude, loc.longitude)
                geocode_cache[key] = coord
                return coord
        except Exception:
            return None
        return None

    # Utiliser toutes les missions (pas seulement celles entre sites)
    map_missions = fm_missions.copy()

    if map_missions.empty:
        st.info("Aucune mission à afficher sur la carte.")
    else:
        routes = map_missions.groupby(['VILLE_DEPART', 'VILLE_DESTINATION'])['EMISSION'].sum().reset_index()
        max_em = routes['EMISSION'].max()

        map_fig = go.Figure()

        # Ajouter une trace par trajet (ligne entre points) si on a les coordonnées
        for _, row in routes.iterrows():
            start_key = canon(row['VILLE_DEPART'])
            end_key = canon(row['VILLE_DESTINATION'])
            start = canonical_coords.get(start_key)
            end = canonical_coords.get(end_key)
            # Si on ne connaît pas les coordonnées, on ignore ce trajet (ou ajouter des geocodes si disponible)
            if not start or not end:
                continue
            width = 1 + (row['EMISSION'] / max_em) * 6 if max_em > 0 else 1
            map_fig.add_trace(go.Scattergeo(
                lon=[start[1], end[1]],
                lat=[start[0], end[0]],
                mode='lines',
                line=dict(width=width, color='royalblue'),
                opacity=0.7,
                hoverinfo='text',
                text=f"{row['VILLE_DEPART']} → {row['VILLE_DESTINATION']}: {row['EMISSION']:.2f} tCO2e",
                showlegend=False
            ))

        # Ajouter les points des 6 sites (visibles même si pas de trajet)
        site_names = list(site_coords.keys())
        lats = [site_coords[s][0] for s in site_names]
        lons = [site_coords[s][1] for s in site_names]
        map_fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode='markers+text',
            text=site_names,
            textposition='top center',
            marker=dict(size=10, color='crimson'),
            showlegend=False
        ))

        map_fig.update_layout(
            title='Épaisseur de ligne proportionelle à la quantité d\'émissions',
            geo=dict(showland=True, landcolor='rgb(230, 230, 230)', showcountries=True),
            height=500,
            margin=dict(t=40, b=20, l=20, r=20),
            showlegend=False
        )

        st.plotly_chart(map_fig, use_container_width=True)

# ============================================================================
# ONGLET 2 - PERSONNEL & SITES
# ============================================================================

with tab2:
    st.header("Personnel et Sites")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution par Site")
        site_dist = dp_filtered['ID_SITE'].value_counts()
        fig = px.pie(
            values=site_dist.values,
            names=site_dist.index,
            title="Nombre d'employés par site"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Distribution par Fonction")
        fonction_dist = dp_filtered['FONCTION_PERSONNEL'].value_counts()
        fig = px.bar(
            y=fonction_dist.index,
            x=fonction_dist.values,
            title="Nombre d'employés par fonction",
            labels={'x': 'Nombre', 'y': 'Fonction'},
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Détail du Personnel")
    st.dataframe(dp_filtered, use_container_width=True)

# ============================================================================
# ONGLET 3 - MATÉRIEL INFORMATIQUE
# ============================================================================

with tab3:
    st.header("Matériel Informatique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Impact par Type de Matériel")
        impact_by_type = fma_joined.groupby('TYPE')['IMPACT'].sum().sort_values(ascending=False)
        fig = px.bar(
            y=impact_by_type.index,
            x=impact_by_type.values,
            title="Impact Carbone par Type de Matériel",
            labels={'x': 'Impact (tCO₂e)', 'y': 'Type'},
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Impact par Site")
        impact_by_site = fma_joined.groupby('ID_SITE')['IMPACT'].sum().sort_values(ascending=False)
        fig = px.bar(
            x=impact_by_site.index,
            y=impact_by_site.values,
            title="Impact Carbone du Matériel par Site",
            labels={'x': 'Site', 'y': 'Impact (tCO₂e)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Impact par Fonction Personnelle")
    impact_by_fonction = fma_joined.groupby('FONCTION_PERSONNEL')['IMPACT'].sum().sort_values(ascending=False)
    fig = px.bar(
        y=impact_by_fonction.index,
        x=impact_by_fonction.values,
        title="Impact du Matériel par Fonction",
        labels={'x': 'Impact (tCO₂e)', 'y': 'Fonction'},
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Matériel Détaillé")
    st.dataframe(fma_joined[['TYPE', 'MODELE', 'IMPACT', 'ID_SITE', 'FONCTION_PERSONNEL']], use_container_width=True)

# ============================================================================
# ONGLET 4 - MISSIONS
# ============================================================================

with tab4:
    st.header("Missions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Impact par Type de Transport")
        impact_by_transport = fm_joined.groupby('TRANSPORT')['EMISSION'].sum().sort_values(ascending=False)
        fig = px.bar(
            y=impact_by_transport.index,
            x=impact_by_transport.values,
            title="Impact Carbone par Type de Transport",
            labels={'x': 'Emission (tCO₂e)', 'y': 'Transport'},
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Impact par Type de Mission")
        impact_by_mission = fm_joined.groupby('TYPE_MISSION')['EMISSION'].sum().sort_values(ascending=False)
        fig = px.bar(
            y=impact_by_mission.index,
            x=impact_by_mission.values,
            title="Impact Carbone par Type de Mission",
            labels={'x': 'Emission (tCO₂e)', 'y': 'Type'},
            orientation='h'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Missions par Site")
    missions_by_site = fm_joined.groupby('ID_SITE')['EMISSION'].sum().sort_values(ascending=False)
    fig = px.bar(
        x=missions_by_site.index,
        y=missions_by_site.values,
        title="Impact des Missions par Site",
        labels={'x': 'Site', 'y': 'Emission (tCO₂e)'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Top 10 Destinations les Plus Impactantes")
    top_destinations = fm_joined.groupby('VILLE_DESTINATION')['EMISSION'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(
        y=top_destinations.index,
        x=top_destinations.values,
        title="Top 10 Destinations",
        labels={'x': 'Emission (tCO₂e)', 'y': 'Destination'},
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# ONGLET 5 - QUESTIONS ET RÉPONSES
# ============================================================================

with tab5:
    st.header("Réponses aux questions - Fiche projet")
    
    # Q1
    st.subheader("Q1: Combien de cadres travaillent sur le site de Paris?")
    q1 = dp[(dp['ID_SITE'] == 'PARIS') & (dp['FONCTION_PERSONNEL'] == 'Business Executive')].shape[0]
    st.metric("Nombre de cadres à Paris", q1)
    
    # Q2
    st.subheader("Q2: Combien d'ingénieurs Data travaillent sur les sites aux États-Unis?")
    q2 = dp[(dp['ID_SITE'].isin(['LOSANGELES', 'NEWYORK'])) & (dp['FONCTION_PERSONNEL'] == 'Data Engineer')].shape[0]
    st.metric("Ingénieurs Data aux USA", q2)
    
    # Q3
    st.subheader("Q3: Combien d'ingénieurs informaticiens travaillent dans l'organisation?")
    q3 = dp[dp['FONCTION_PERSONNEL'] == 'Computer Engineer'].shape[0]
    st.metric("Ingénieurs informaticiens totaux", q3)
    
    # Q4
    st.subheader("Q4: Combien de PC fixes ont été achetés entre juin et septembre 2026?")
    fma_types = fma.merge(dma, on='ID_MATERIEL', how='left')
    q4 = fma_types[
        (fma_types['TYPE'].isin(['PC fixe sans ecran', 'PC fixe tout-en-un'])) &
        (pd.to_datetime(fma_types['ID_DATE_ACHAT']).dt.date >= date(2026, 6, 1)) &
        (pd.to_datetime(fma_types['ID_DATE_ACHAT']).dt.date <= date(2026, 9, 30))
    ].shape[0]
    st.metric("PC fixes (juin-septembre 2026)", q4)
    
    # Q5
    st.subheader("Q5: Impact carbone des PC fixes sans écran (mai-octobre 2026)?")
    q5 = fma_types[
        (fma_types['TYPE'] == 'PC fixe sans ecran') &
        (pd.to_datetime(fma_types['ID_DATE_ACHAT']).dt.date >= date(2026, 5, 1)) &
        (pd.to_datetime(fma_types['ID_DATE_ACHAT']).dt.date <= date(2026, 10, 31))
    ]['IMPACT'].sum()
    st.metric("Impact (tCO2e)", f"{q5:.3f}")
    
    # Q6
    st.subheader("Q6: Impact PC portables achetés par Data Engineers à Londres et New-York (mai-octobre 2026)?")
    q6_personnel = dp[(dp['ID_SITE'].isin(['LONDON', 'NEWYORK'])) & (dp['FONCTION_PERSONNEL'] == 'Data Engineer')]
    q6 = fma_types[
        (fma_types['ID_PERSONNEL'].isin(q6_personnel['ID_PERSONNEL'])) &
        (fma_types['TYPE'] == 'PC portable') &
        (pd.to_datetime(fma_types['ID_DATE_ACHAT']).dt.date >= date(2026, 5, 1)) &
        (pd.to_datetime(fma_types['ID_DATE_ACHAT']).dt.date <= date(2026, 10, 31))
    ]['IMPACT'].sum()
    st.metric("Impact (tCO2e)", f"{q6:.3f}")
    
    # Q7
    st.subheader("Q7: Impact écrans achetés par cadres (juillet-septembre 2026)?")
    q7_personnel = dp[dp['FONCTION_PERSONNEL'] == 'Business Executive']
    q7 = fma_types[
        (fma_types['ID_PERSONNEL'].isin(q7_personnel['ID_PERSONNEL'])) &
        (fma_types['TYPE'] == 'Ecran') &
        (pd.to_datetime(fma_types['ID_DATE_ACHAT']).dt.date >= date(2026, 7, 1)) &
        (pd.to_datetime(fma_types['ID_DATE_ACHAT']).dt.date <= date(2026, 9, 30))
    ]['IMPACT'].sum()
    st.metric("Impact (tCO2e)", f"{q7:.3f}")
    
    # Q8
    st.subheader("Q8: Impact missions sur sites européens (mai-octobre 2026)?")
    fm_missions = fm_joined.copy()
    q8 = fm_missions[
        (fm_missions['ID_SITE'].isin(['PARIS', 'LONDON', 'BERLIN'])) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date >= date(2026, 5, 1)) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date <= date(2026, 10, 31))
    ]['EMISSION'].sum()
    st.metric("Emission (tCO2e)", f"{q8:.3f}")
    
    # Q9
    st.subheader("Q9: Top 5 jours les plus impactants pour missions en avion (sites européens)?")
    q9 = fm_missions[
        (fm_missions['TRANSPORT'] == 'Avion') &
        (fm_missions['ID_SITE'].isin(['PARIS', 'LONDON', 'BERLIN']))
    ].groupby('ID_DATE_MISSION')['EMISSION'].sum().sort_values(ascending=False).head(5)
    st.dataframe(q9.reset_index(), use_container_width=True)
    
    # Q10
    st.subheader("Q10: Secteur avec plus d'impact (missions + matériel)?")
    missions_by_fonction = fm_missions.merge(dp, on='ID_PERSONNEL', how='left').groupby('FONCTION_PERSONNEL')['EMISSION'].sum()
    materiel_by_fonction = fma_types.merge(dp, on='ID_PERSONNEL', how='left').groupby('FONCTION_PERSONNEL')['IMPACT'].sum()
    q10 = (missions_by_fonction.add(materiel_by_fonction, fill_value=0)).sort_values(ascending=False)
    fig = px.bar(
        y=q10.index,
        x=q10.values,
        title="Impact Total par Fonction",
        labels={'x': 'Impact (tCO2e)', 'y': 'Fonction'},
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Q11
    st.subheader("Q11: Site avec le plus d'impact (missions + matériel)?")
    missions_by_site = fm_missions.groupby('ID_SITE')['EMISSION'].sum()
    materiel_by_site = fma_types.groupby('ID_SITE')['IMPACT'].sum()
    q11 = (missions_by_site.add(materiel_by_site, fill_value=0)).sort_values(ascending=False)
    fig = px.bar(
        x=q11.index,
        y=q11.values,
        title="Impact Total par Site",
        labels={'x': 'Site', 'y': 'Impact (tCO2e)'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Q12
    st.subheader("Q12: Impact missions inter-sites en septembre 2026?")
    sites_missions = ["Los Angeles", "New-York", "Paris", "London", "Shanghai", "Berlin"]
    q12 = fm_missions[
        (fm_missions['VILLE_DEPART'].isin(sites_missions)) &
        (fm_missions['VILLE_DESTINATION'].isin(sites_missions)) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date >= date(2026, 9, 1)) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date <= date(2026, 9, 30))
    ]['EMISSION'].sum()
    st.metric("Emission (tCO2e)", f"{q12:.3f}")
    
    # Q13
    st.subheader("Q13: Impact conférences pour Los Angeles (juillet 2026)?")
    q13 = fm_missions[
        (fm_missions['TYPE_MISSION'] == 'Conference') &
        (fm_missions['ID_SITE'] == 'LOSANGELES') &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date >= date(2026, 7, 1)) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date <= date(2026, 7, 31))
    ]['EMISSION'].sum()
    st.metric("Emission (tCO2e)", f"{q13:.3f}")
    
    # Q14
    st.subheader("Q14: Fonction avec plus d'impact pour conférences (mai-septembre 2026)?")
    q14 = fm_missions[
        (fm_missions['TYPE_MISSION'] == 'Conference') &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date >= date(2026, 5, 1)) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date <= date(2026, 9, 30))
    ].merge(dp, on='ID_PERSONNEL', how='left').groupby('FONCTION_PERSONNEL')['EMISSION'].sum().sort_values(ascending=False)
    fig = px.bar(
        y=q14.index,
        x=q14.values,
        title="Impact Conférences par Fonction",
        labels={'x': 'Emission (tCO2e)', 'y': 'Fonction'},
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Q15
    st.subheader("Q15: Âge moyen Data Engineers en formations (juillet-septembre 2026)?")
    q15 = fm_missions[
        (fm_missions['TYPE_MISSION'] == 'Vocational Training') &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date >= date(2026, 7, 1)) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date <= date(2026, 9, 30))
    ].merge(dp, on='ID_PERSONNEL', how='left').query('FONCTION_PERSONNEL == "Data Engineer"')['AGE'].mean()
    if not np.isnan(q15):
        st.metric("Âge moyen", f"{q15:.1f}")
    else:
        st.info("Aucune donnée disponible")
    
    # Q16
    st.subheader("Q16: Destination la plus impactante (mai-octobre 2026)?")
    q16 = fm_missions[
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date >= date(2026, 5, 1)) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date <= date(2026, 10, 31))
    ].groupby('VILLE_DESTINATION')['EMISSION'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(
        y=q16.index,
        x=q16.values,
        title="Top 10 Destinations Impactantes",
        labels={'x': 'Emission (tCO2e)', 'y': 'Destination'},
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Q17
    st.subheader("Q17: Top 3 missions cadres (sites européens) en mai 2026?")
    q17 = fm_missions[
        (fm_missions['ID_SITE'].isin(['PARIS', 'LONDON', 'BERLIN'])) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date >= date(2026, 5, 1)) &
        (pd.to_datetime(fm_missions['ID_DATE_MISSION']).dt.date <= date(2026, 5, 31))
    ].merge(dp, on='ID_PERSONNEL', how='left').query('FONCTION_PERSONNEL == "Business Executive"').groupby('TYPE_MISSION')['EMISSION'].sum().sort_values(ascending=False).head(3)
    fig = px.bar(
        y=q17.index,
        x=q17.values,
        title="Top 3 Missions Cadres (mai)",
        labels={'x': 'Emission (tCO2e)', 'y': 'Type'},
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Q18
    st.subheader("Q18: Top 5 missions les plus impactantes à Paris?")
    q18 = fm_missions[fm_missions['ID_SITE'] == 'PARIS'].nlargest(5, 'EMISSION')[['TYPE_MISSION', 'VILLE_DEPART', 'VILLE_DESTINATION', 'TRANSPORT', 'EMISSION']]
    q18.columns = ['Type', 'Départ', 'Destination', 'Transport', 'Emission (tCO2e)']
    st.dataframe(q18, use_container_width=True)
    
    # Q19
    st.subheader("Q19: Impact missions mensuels par transport et site?")
    q19 = fm_missions.copy()
    q19['MOIS'] = pd.to_datetime(q19['ID_DATE_MISSION']).dt.to_period('M').astype(str)
    q19_pivot = q19.groupby(['ID_SITE', 'MOIS', 'TRANSPORT'])['EMISSION'].sum().reset_index()
    
    fig = px.bar(
        q19_pivot,
        x='MOIS',
        y='EMISSION',
        color='TRANSPORT',
        facet_col='ID_SITE',
        facet_col_wrap=3,
        title="Impact Mensuel par Transport et Site",
        labels={'EMISSION': 'Emission (tCO2e)', 'MOIS': 'Mois'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Q20
    st.subheader("Q20: Impact global mensuel (missions + matériel)?")
    q20_missions = fm_missions.copy()
    q20_missions['MOIS'] = pd.to_datetime(q20_missions['ID_DATE_MISSION']).dt.to_period('M').astype(str)
    q20_m = q20_missions.groupby('MOIS')['EMISSION'].sum().reset_index()
    
    q20_materiel = fma_types.copy()
    q20_materiel['MOIS'] = pd.to_datetime(q20_materiel['ID_DATE_ACHAT']).dt.to_period('M').astype(str)
    q20_ma = q20_materiel.groupby('MOIS')['IMPACT'].sum().reset_index()
    
    q20 = q20_m.merge(q20_ma, on='MOIS', how='outer').fillna(0)
    q20.columns = ['Mois', 'Missions', 'Matériel']
    q20['Total'] = q20['Missions'] + q20['Matériel']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=q20['Mois'], y=q20['Missions'], name='Missions'))
    fig.add_trace(go.Bar(x=q20['Mois'], y=q20['Matériel'], name='Matériel'))
    fig.add_trace(go.Scatter(x=q20['Mois'], y=q20['Total'], name='Total', mode='lines+markers', line=dict(color='red', width=3)))
    fig.update_layout(
        title="Impact Global Mensuel",
        barmode='stack',
        xaxis_title="Mois",
        yaxis_title="Impact (tCO2e)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
