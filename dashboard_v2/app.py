import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date
import plotly.express as px
import plotly.graph_objects as go

# Configuration Streamlit
st.set_page_config(page_title="GHG Inventory Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("Dashboard - Inventaire Carbone GHG")

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
    value=(date(2026, 5, 1), date(2026, 10, 31)),
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
    fig.update_layout(
        title="Impact Carbone Mensuel (Missions + Matériel)",
        barmode='stack',
        xaxis_title="Mois",
        yaxis_title="Impact (tCO₂e)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

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
    st.header("Reconstitution des Questions")
    
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
    fm_missions = fm.merge(dm, on='ID_MISSION', how='left')
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
