import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="GHG Inventory Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Personnalisation CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5em;
        color: #1f77b4;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<div class="main-title">🌍 Tableau de Bord BGES - Inventaire des Émissions de Gaz à Effet de Serre</div>', unsafe_allow_html=True)

# Sidebar pour la navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Sélectionnez une page:",
    [
        "📈 Aperçu Général",
        "🎯 Questions d'Analyse",
        "📉 Visualisations",
        "🔍 Détails des Données"
    ]
)

# Charger les données de démonstration
@st.cache_data
def load_sample_data():
    """Charge des données d'exemple pour la démonstration"""
    
    # Données des missions
    missions_data = {
        'ID_MISSION': list(range(1, 51)),
        'ID_SITE': np.random.choice(['PARIS', 'LONDON', 'BERLIN', 'NEWYORK', 'LOSANGELES', 'SHANGHAI'], 50),
        'VILLE_DEPART': np.random.choice(['Paris', 'London', 'Berlin', 'New York', 'Los Angeles', 'Shanghai'], 50),
        'VILLE_DESTINATION': np.random.choice(['Paris', 'London', 'Berlin', 'New York', 'Los Angeles', 'Shanghai'], 50),
        'TRANSPORT': np.random.choice(['Avion', 'Train', 'Taxi', 'Bus', 'Métro'], 50),
        'TYPE_MISSION': np.random.choice(['Séminaire', 'Conférence', 'Formation', 'Business Meeting', 'Team Meeting'], 50),
        'DATE_MISSION': [datetime(2026, 5, 1) + timedelta(days=x*10) for x in range(50)],
        'EMISSION_tCO2e': np.random.uniform(0.5, 300, 50),
        'DISTANCE_KM': np.random.uniform(100, 20000, 50)
    }
    
    df_missions = pd.DataFrame(missions_data)
    
    # Données du personnel
    personnel_data = {
        'ID_PERSONNEL': list(range(1, 151)),
        'ID_SITE': np.random.choice(['PARIS', 'LONDON', 'BERLIN', 'NEWYORK', 'LOSANGELES', 'SHANGHAI'], 150),
        'FONCTION': np.random.choice(['Data Engineer', 'Computer Engineer', 'Economist', 'Business Executive', 'HRD'], 150),
        'AGE': np.random.randint(25, 65, 150)
    }
    
    df_personnel = pd.DataFrame(personnel_data)
    
    # Données du matériel informatique
    materiel_data = {
        'ID_MATERIEL': list(range(1, 101)),
        'ID_SITE': np.random.choice(['PARIS', 'LONDON', 'BERLIN', 'NEWYORK', 'LOSANGELES', 'SHANGHAI'], 100),
        'TYPE': np.random.choice(['Laptop', 'Desktop', 'Serveur', 'Écran'], 100),
        'DATE_ACHAT': [datetime(2026, 5, 1) + timedelta(days=x*3) for x in range(100)],
        'IMPACT_tCO2e': np.random.uniform(0.1, 50, 100)
    }
    
    df_materiel = pd.DataFrame(materiel_data)
    
    return df_missions, df_personnel, df_materiel

# Charger les données
df_missions, df_personnel, df_materiel = load_sample_data()

# PAGE 1: APERÇU GÉNÉRAL
if page == "📈 Aperçu Général":
    st.header("📈 Aperçu Général du Bilan GES")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_emission_missions = df_missions['EMISSION_tCO2e'].sum()
    total_emission_materiel = df_materiel['IMPACT_tCO2e'].sum()
    total_emission = total_emission_missions + total_emission_materiel
    total_missions = len(df_missions)
    
    with col1:
        st.metric("📊 Total Émissions Missions", f"{total_emission_missions:.2f} tCO₂e", 
                 f"+{total_emission_missions/total_emission*100:.1f}%")
    
    with col2:
        st.metric("💻 Total Émissions Matériel", f"{total_emission_materiel:.2f} tCO₂e",
                 f"+{total_emission_materiel/total_emission*100:.1f}%")
    
    with col3:
        st.metric("🌍 Total Émissions", f"{total_emission:.2f} tCO₂e", delta=None)
    
    with col4:
        st.metric("✈️ Nombre de Missions", f"{total_missions}", delta=None)
    
    st.divider()
    
    # Graphique des émissions par site
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Émissions par Site (Missions)")
        emissions_by_site = df_missions.groupby('ID_SITE')['EMISSION_tCO2e'].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 6))
        emissions_by_site.plot(kind='barh', ax=ax, color='steelblue', edgecolor='white')
        ax.set_xlabel('Émissions (tCO₂e)')
        ax.set_title('Émissions totales par site')
        ax.grid(axis='x', alpha=0.3)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.subheader("Répartition des Transports")
        transport_dist = df_missions['TRANSPORT'].value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(transport_dist.values, labels=transport_dist.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribution des types de transport')
        st.pyplot(fig)
        plt.close()

# PAGE 2: QUESTIONS D'ANALYSE
elif page == "🎯 Questions d'Analyse":
    st.header("🎯 Questions d'Analyse - Réponses Interactives")
    
    # Sélecteur de question
    questions_dict = {
        "Q12": "Impact carbone des missions reliant chaque site",
        "Q13": "Impact des séminaires en juillet 2026 (Los Angeles)",
        "Q14": "Secteur d'activité le plus impactant (conférences mai-sep 2026)",
        "Q15": "Âge moyen des Data Engineers en formation (juil-sep 2026)",
        "Q16": "Destination la plus impactante (mai-oct 2026)",
        "Q17": "3 catégories de missions les plus impactantes (cadres, sites européens, mai 2026)",
        "Q18": "5 missions les plus impactantes à Paris",
        "Q19": "Impact carbone mensuel par transport et site",
        "Q20": "Impact carbone global mensuel"
    }
    
    selected_question = st.selectbox("Sélectionnez une question:", list(questions_dict.values()))
    question_key = [k for k, v in questions_dict.items() if v == selected_question][0]
    
    st.divider()
    
    if question_key == "Q12":
        st.subheader("Q12: Impact carbone des missions reliant chaque site")
        
        # Filtrages
        col1, col2 = st.columns(2)
        with col1:
            date_min = st.date_input("Date minimale:", value=datetime(2026, 5, 1).date())
        with col2:
            date_max = st.date_input("Date maximale:", value=datetime(2026, 10, 31).date())
        
        # Filtrer les données
        df_filtered = df_missions[
            (df_missions['DATE_MISSION'].dt.date >= date_min) &
            (df_missions['DATE_MISSION'].dt.date <= date_max)
        ]
        
        # Calculer les émissions par paire de sites
        emissions_inter_sites = df_filtered.groupby(['ID_SITE', 'VILLE_DESTINATION'])['EMISSION_tCO2e'].sum().reset_index()
        emissions_inter_sites = emissions_inter_sites.sort_values('EMISSION_tCO2e', ascending=False)
        
        st.write("**Émissions par route inter-sites:**")
        st.dataframe(emissions_inter_sites, use_container_width=True)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        top_routes = emissions_inter_sites.head(10)
        ax.barh(range(len(top_routes)), top_routes['EMISSION_tCO2e'].values, color='coral', edgecolor='white')
        ax.set_yticks(range(len(top_routes)))
        ax.set_yticklabels([f"{row['ID_SITE']} → {row['VILLE_DESTINATION']}" for _, row in top_routes.iterrows()])
        ax.set_xlabel('Émissions (tCO₂e)')
        ax.set_title('Top 10 des routes les plus impactantes')
        ax.grid(axis='x', alpha=0.3)
        st.pyplot(fig)
        plt.close()
    
    elif question_key == "Q13":
        st.subheader("Q13: Impact des séminaires en juillet 2026 (Los Angeles)")
        
        # Filtrer pour les séminaires en juillet 2026 à Los Angeles
        df_filtered = df_missions[
            (df_missions['ID_SITE'] == 'LOSANGELES') &
            (df_missions['TYPE_MISSION'] == 'Séminaire') &
            (df_missions['DATE_MISSION'].dt.month == 7) &
            (df_missions['DATE_MISSION'].dt.year == 2026)
        ]
        
        if len(df_filtered) > 0:
            total_impact = df_filtered['EMISSION_tCO2e'].sum()
            st.metric("Impact total des séminaires", f"{total_impact:.2f} tCO₂e")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Détails des séminaires:**")
                st.dataframe(df_filtered[['DATE_MISSION', 'TRANSPORT', 'DISTANCE_KM', 'EMISSION_tCO2e']], use_container_width=True)
            
            with col2:
                fig, ax = plt.subplots(figsize=(10, 6))
                df_filtered.groupby('TRANSPORT')['EMISSION_tCO2e'].sum().plot(kind='bar', ax=ax, color='skyblue', edgecolor='white')
                ax.set_ylabel('Émissions (tCO₂e)')
                ax.set_xlabel('Type de transport')
                ax.set_title('Impact par type de transport')
                plt.xticks(rotation=45)
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
                plt.close()
        else:
            st.warning("Aucune donnée trouvée pour cette requête")
    
    elif question_key == "Q14":
        st.subheader("Q14: Secteur d'activité le plus impactant (conférences mai-sep 2026)")
        
        # Filtrer pour les conférences mai-sep 2026
        df_filtered = df_missions[
            (df_missions['TYPE_MISSION'] == 'Conférence') &
            (df_missions['DATE_MISSION'].dt.month >= 5) &
            (df_missions['DATE_MISSION'].dt.month <= 9) &
            (df_missions['DATE_MISSION'].dt.year == 2026)
        ]
        
        if len(df_filtered) > 0:
            sector_impact = df_filtered.groupby('TRANSPORT')['EMISSION_tCO2e'].sum().sort_values(ascending=False)
            st.metric("Secteur le plus impactant", sector_impact.index[0], f"{sector_impact.iloc[0]:.2f} tCO₂e")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sector_impact.plot(kind='bar', ax=ax, color='lightgreen', edgecolor='white')
            ax.set_ylabel('Émissions (tCO₂e)')
            ax.set_xlabel('Secteur')
            ax.set_title('Impact carbone par secteur (conférences)')
            plt.xticks(rotation=45)
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Aucune donnée trouvée pour cette requête")
    
    elif question_key == "Q15":
        st.subheader("Q15: Âge moyen des Data Engineers en formation (juil-sep 2026)")
        
        # Filtrer pour les Data Engineers en formation juillet-septembre
        df_filtered_missions = df_missions[
            (df_missions['TYPE_MISSION'] == 'Formation') &
            (df_missions['DATE_MISSION'].dt.month >= 7) &
            (df_missions['DATE_MISSION'].dt.month <= 9) &
            (df_missions['DATE_MISSION'].dt.year == 2026)
        ]
        
        if len(df_filtered_missions) > 0:
            avg_age = df_personnel[df_personnel['FONCTION'] == 'Data Engineer']['AGE'].mean()
            st.metric("Âge moyen des Data Engineers", f"{avg_age:.2f} ans")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            age_dist = df_personnel[df_personnel['FONCTION'] == 'Data Engineer']['AGE']
            ax.hist(age_dist, bins=20, color='mediumpurple', edgecolor='white', alpha=0.7)
            ax.axvline(avg_age, color='red', linestyle='--', linewidth=2, label=f'Moyenne: {avg_age:.2f}')
            ax.set_xlabel('Âge')
            ax.set_ylabel('Nombre de personnes')
            ax.set_title('Distribution des âges - Data Engineers')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Aucune donnée trouvée pour cette requête")
    
    elif question_key == "Q16":
        st.subheader("Q16: Destination la plus impactante (mai-oct 2026)")
        
        # Filtrer pour mai-octobre 2026
        df_filtered = df_missions[
            (df_missions['DATE_MISSION'].dt.month >= 5) &
            (df_missions['DATE_MISSION'].dt.month <= 10) &
            (df_missions['DATE_MISSION'].dt.year == 2026)
        ]
        
        if len(df_filtered) > 0:
            dest_impact = df_filtered.groupby('VILLE_DESTINATION')['EMISSION_tCO2e'].sum().sort_values(ascending=False)
            st.metric("Destination la plus impactante", dest_impact.index[0], f"{dest_impact.iloc[0]:.2f} tCO₂e")
            
            st.write("**Top destinations:**")
            st.dataframe(dest_impact.head(10).reset_index().rename(columns={'VILLE_DESTINATION': 'Destination', 'EMISSION_tCO2e': 'Émissions (tCO₂e)'}), use_container_width=True)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            dest_impact.head(10).plot(kind='barh', ax=ax, color='salmon', edgecolor='white')
            ax.set_xlabel('Émissions (tCO₂e)')
            ax.set_title('Top 10 destinations les plus impactantes')
            ax.grid(axis='x', alpha=0.3)
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Aucune donnée trouvée pour cette requête")
    
    elif question_key == "Q17":
        st.subheader("Q17: 3 catégories de missions les plus impactantes (cadres, sites européens, mai 2026)")
        
        # Filtrer pour cadres, sites européens, mai 2026
        european_sites = ['PARIS', 'LONDON', 'BERLIN']
        df_filtered = df_missions[
            (df_missions['ID_SITE'].isin(european_sites)) &
            (df_missions['DATE_MISSION'].dt.month == 5) &
            (df_missions['DATE_MISSION'].dt.year == 2026)
        ]
        
        if len(df_filtered) > 0:
            mission_type_impact = df_filtered.groupby('TYPE_MISSION')['EMISSION_tCO2e'].sum().sort_values(ascending=False)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if len(mission_type_impact) > 0:
                    st.metric("1ère", mission_type_impact.index[0], f"{mission_type_impact.iloc[0]:.2f} tCO₂e")
            with col2:
                if len(mission_type_impact) > 1:
                    st.metric("2ème", mission_type_impact.index[1], f"{mission_type_impact.iloc[1]:.2f} tCO₂e")
            with col3:
                if len(mission_type_impact) > 2:
                    st.metric("3ème", mission_type_impact.index[2], f"{mission_type_impact.iloc[2]:.2f} tCO₂e")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            mission_type_impact.head(3).plot(kind='bar', ax=ax, color='orange', edgecolor='white')
            ax.set_ylabel('Émissions (tCO₂e)')
            ax.set_xlabel('Catégorie de mission')
            ax.set_title('Top 3 catégories de missions')
            plt.xticks(rotation=45)
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Aucune donnée trouvée pour cette requête")
    
    elif question_key == "Q18":
        st.subheader("Q18: 5 missions les plus impactantes à Paris")
        
        # Filtrer pour Paris
        df_filtered = df_missions[df_missions['ID_SITE'] == 'PARIS'].sort_values('EMISSION_tCO2e', ascending=False)
        
        if len(df_filtered) > 0:
            top_5 = df_filtered.head(5)
            st.write("**Top 5 missions les plus impactantes à Paris:**")
            st.dataframe(top_5[['DATE_MISSION', 'VILLE_DESTINATION', 'TRANSPORT', 'DISTANCE_KM', 'EMISSION_tCO2e']], use_container_width=True)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(range(len(top_5)), top_5['EMISSION_tCO2e'].values, color='teal', edgecolor='white')
            ax.set_yticks(range(len(top_5)))
            ax.set_yticklabels([f"Mission {i+1}" for i in range(len(top_5))])
            ax.set_xlabel('Émissions (tCO₂e)')
            ax.set_title('Top 5 missions à Paris')
            ax.grid(axis='x', alpha=0.3)
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Aucune donnée trouvée pour cette requête")

# PAGE 3: VISUALISATIONS
elif page == "📉 Visualisations":
    st.header("📉 Visualisations Avancées")
    
    viz_type = st.selectbox(
        "Sélectionnez le type de visualisation:",
        [
            "Q19 - Impact carbone mensuel par transport et site",
            "Q20 - Impact carbone global mensuel",
            "Émissions par type de mission",
            "Distribution des distances"
        ]
    )
    
    if viz_type == "Q19 - Impact carbone mensuel par transport et site":
        st.subheader("Impact carbone mensuel des missions par type de transport et site")
        
        # Extraire le mois
        df_missions['MOIS'] = df_missions['DATE_MISSION'].dt.month
        
        # Pivot et agrégation
        emissions_monthly = df_missions.groupby(['ID_SITE', 'MOIS', 'TRANSPORT'])['EMISSION_tCO2e'].sum().reset_index()
        
        # Créer des sous-graphiques
        sites = sorted(df_missions['ID_SITE'].unique())
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        axes = axes.flatten()
        
        mois_noms = ['', 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        
        for idx, site in enumerate(sites):
            ax = axes[idx]
            site_data = emissions_monthly[emissions_monthly['ID_SITE'] == site]
            pivot_data = site_data.pivot(index='MOIS', columns='TRANSPORT', values='EMISSION_tCO2e').fillna(0)
            
            pivot_data.plot(kind='bar', stacked=True, ax=ax, edgecolor='white')
            ax.set_title(f"Site: {site}", fontweight='bold', fontsize=12)
            ax.set_xlabel("Mois")
            ax.set_ylabel("Émissions (tCO₂e)")
            ax.set_xticklabels([mois_noms[int(m)] if 1 <= int(m) <= 12 else str(m) for m in pivot_data.index], rotation=45)
            ax.legend(title="Transport", fontsize=8, loc='upper left')
            ax.grid(axis='y', alpha=0.3)
        
        plt.suptitle("Impact carbone mensuel des missions par type de transport et site", fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    elif viz_type == "Q20 - Impact carbone global mensuel":
        st.subheader("Impact carbone global mensuel de l'organisation")
        
        # Calcul par mois
        df_missions['MOIS'] = df_missions['DATE_MISSION'].dt.month
        emissions_par_mois = df_missions.groupby('MOIS')['EMISSION_tCO2e'].sum().reset_index()
        emissions_par_mois.columns = ['MOIS', 'Emission_missions']
        
        df_materiel['MOIS'] = df_materiel['DATE_ACHAT'].dt.month
        impact_mat_par_mois = df_materiel.groupby('MOIS')['IMPACT_tCO2e'].sum().reset_index()
        impact_mat_par_mois.columns = ['MOIS', 'Impact_materiel']
        
        # Fusion
        global_impact = emissions_par_mois.merge(impact_mat_par_mois, on='MOIS', how='outer').fillna(0)
        global_impact['TOT_IMPACT'] = global_impact['Emission_missions'] + global_impact['Impact_materiel']
        global_impact = global_impact.sort_values('MOIS')
        
        mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        global_impact['MOIS_LABEL'] = global_impact['MOIS'].apply(lambda m: mois_noms[int(m)-1] if 1 <= int(m) <= 12 else str(m))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        x = range(len(global_impact))
        
        ax.bar(x, global_impact['Emission_missions'], label='Missions', color='steelblue', edgecolor='white')
        ax.bar(x, global_impact['Impact_materiel'], bottom=global_impact['Emission_missions'], label='Matériel', color='orange', edgecolor='white')
        ax.plot(x, global_impact['TOT_IMPACT'], marker='o', color='red', linewidth=2, markersize=8, label='Total', zorder=5)
        
        for i, val in enumerate(global_impact['TOT_IMPACT']):
            ax.text(i, val + global_impact['TOT_IMPACT'].max() * 0.02, f"{val:.0f}",
                    ha='center', fontweight='bold', color='red', fontsize=9)
        
        ax.set_xticks(x)
        ax.set_xticklabels(global_impact['MOIS_LABEL'])
        ax.set_xlabel("Mois")
        ax.set_ylabel("Émission (tCO₂e)")
        ax.set_title("Impact carbone global mensuel de l'organisation")
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.dataframe(global_impact[['MOIS_LABEL', 'Emission_missions', 'Impact_materiel', 'TOT_IMPACT']], use_container_width=True)
    
    elif viz_type == "Émissions par type de mission":
        st.subheader("Émissions par type de mission")
        
        mission_impact = df_missions.groupby('TYPE_MISSION')['EMISSION_tCO2e'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        mission_impact.plot(kind='barh', ax=ax, color='mediumseagreen', edgecolor='white')
        ax.set_xlabel('Émissions (tCO₂e)')
        ax.set_title('Émissions totales par type de mission')
        ax.grid(axis='x', alpha=0.3)
        st.pyplot(fig)
        plt.close()
        
        st.dataframe(mission_impact.reset_index().rename(columns={'TYPE_MISSION': 'Type de Mission', 'EMISSION_tCO2e': 'Émissions (tCO₂e)'}), use_container_width=True)
    
    elif viz_type == "Distribution des distances":
        st.subheader("Distribution des distances parcourues")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.hist(df_missions['DISTANCE_KM'], bins=30, color='indianred', edgecolor='white', alpha=0.7)
        ax.axvline(df_missions['DISTANCE_KM'].mean(), color='blue', linestyle='--', linewidth=2, label=f'Moyenne: {df_missions["DISTANCE_KM"].mean():.0f} km')
        ax.axvline(df_missions['DISTANCE_KM'].median(), color='green', linestyle='--', linewidth=2, label=f'Médiane: {df_missions["DISTANCE_KM"].median():.0f} km')
        ax.set_xlabel('Distance (km)')
        ax.set_ylabel('Nombre de missions')
        ax.set_title('Distribution des distances parcourues')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        st.pyplot(fig)
        plt.close()

# PAGE 4: DÉTAILS DES DONNÉES
elif page == "🔍 Détails des Données":
    st.header("🔍 Données Détaillées")
    
    data_type = st.selectbox(
        "Sélectionnez le type de données:",
        ["Missions", "Personnel", "Matériel Informatique"]
    )
    
    if data_type == "Missions":
        st.subheader("Données des Missions")
        
        col1, col2 = st.columns(2)
        with col1:
            site_filter = st.multiselect("Filtrer par site:", df_missions['ID_SITE'].unique(), default=df_missions['ID_SITE'].unique())
        with col2:
            transport_filter = st.multiselect("Filtrer par transport:", df_missions['TRANSPORT'].unique(), default=df_missions['TRANSPORT'].unique())
        
        df_display = df_missions[
            (df_missions['ID_SITE'].isin(site_filter)) &
            (df_missions['TRANSPORT'].isin(transport_filter))
        ].sort_values('EMISSION_tCO2e', ascending=False)
        
        st.dataframe(df_display, use_container_width=True)
        
        # Statistiques
        st.subheader("Statistiques")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nombre de missions", len(df_display))
        with col2:
            st.metric("Émissions moyennes", f"{df_display['EMISSION_tCO2e'].mean():.2f} tCO₂e")
        with col3:
            st.metric("Distance moyenne", f"{df_display['DISTANCE_KM'].mean():.0f} km")
        with col4:
            st.metric("Émissions totales", f"{df_display['EMISSION_tCO2e'].sum():.2f} tCO₂e")
    
    elif data_type == "Personnel":
        st.subheader("Données du Personnel")
        
        col1, col2 = st.columns(2)
        with col1:
            site_filter = st.multiselect("Filtrer par site:", df_personnel['ID_SITE'].unique(), default=df_personnel['ID_SITE'].unique())
        with col2:
            fonction_filter = st.multiselect("Filtrer par fonction:", df_personnel['FONCTION'].unique(), default=df_personnel['FONCTION'].unique())
        
        df_display = df_personnel[
            (df_personnel['ID_SITE'].isin(site_filter)) &
            (df_personnel['FONCTION'].isin(fonction_filter))
        ]
        
        st.dataframe(df_display, use_container_width=True)
        
        # Statistiques
        st.subheader("Statistiques")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nombre d'employés", len(df_display))
        with col2:
            st.metric("Âge moyen", f"{df_display['AGE'].mean():.2f} ans")
        with col3:
            st.metric("Âge médian", f"{df_display['AGE'].median():.0f} ans")
    
    elif data_type == "Matériel Informatique":
        st.subheader("Données du Matériel Informatique")
        
        col1, col2 = st.columns(2)
        with col1:
            site_filter = st.multiselect("Filtrer par site:", df_materiel['ID_SITE'].unique(), default=df_materiel['ID_SITE'].unique())
        with col2:
            type_filter = st.multiselect("Filtrer par type:", df_materiel['TYPE'].unique(), default=df_materiel['TYPE'].unique())
        
        df_display = df_materiel[
            (df_materiel['ID_SITE'].isin(site_filter)) &
            (df_materiel['TYPE'].isin(type_filter))
        ].sort_values('IMPACT_tCO2e', ascending=False)
        
        st.dataframe(df_display, use_container_width=True)
        
        # Statistiques
        st.subheader("Statistiques")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nombre d'équipements", len(df_display))
        with col2:
            st.metric("Impact moyen", f"{df_display['IMPACT_tCO2e'].mean():.2f} tCO₂e")
        with col3:
            st.metric("Impact total", f"{df_display['IMPACT_tCO2e'].sum():.2f} tCO₂e")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px; margin-top: 30px;'>
    <p>📊 Tableau de Bord BGES - Inventaire des Émissions de Gaz à Effet de Serre</p>
    <p>UV NF26 - UTC | Année 2026</p>
    <p>Données générées pour la démonstration</p>
</div>
""", unsafe_allow_html=True)
