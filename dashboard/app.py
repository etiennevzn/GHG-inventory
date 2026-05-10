"""
Dashboard BGES — Bilan de Gaz à Effet de Serre
NF26 — Université de Technologie de Compiègne
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data import (
    PALETTE, PALETTE_LIST, GRADIENT,
    SITES,
    Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15, Q16, Q17,
    IMPACT_TOTAL_SECTEUR, IMPACT_TOTAL_SITE,
    TOP3_CADRES_EUROPE_MAI, TOP_MISSIONS_PARIS,
    EMISSIONS_MENSUEL_TRANSPORT_SITE, EMISSIONS_MENSUEL_GLOBAL,
)
from star_model import (
    init_star_model,
    query_q1, query_q2, query_q3, query_q4, query_q5, query_q6, query_q7,
    calculate_total_impact,
    calculate_impact_per_site,
)

# ================================================================
# CONFIGURATION DE LA PAGE
# ================================================================
st.set_page_config(
    page_title="Projet BGES Dashboard — NF26",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# STYLE CSS CUSTOM
# ================================================================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Fond global clair */
    .stApp {{
        background: #f5f6fa;
    }}

    /* Sidebar — claire avec liseré violet */
    section[data-testid="stSidebar"] {{
        background: #ffffff !important;
        border-right: 1px solid #e8eaf0;
    }}
    section[data-testid="stSidebar"] * {{
        color: #2d2d3a !important;
    }}
    section[data-testid="stSidebar"] .stRadio label {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
    }}

    /* Titres */
    h1, h2, h3, h4 {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: #1a1a2e !important;
        letter-spacing: -0.02em;
    }}
    h1 {{
        font-weight: 700 !important;
        background: linear-gradient(135deg, {PALETTE["bleu_nuit"]} 0%, {PALETTE["bleu_violet"]} 50%, {PALETTE["orchidee"]} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* Texte */
    p, span, div, label {{
        color: #2d2d3a;
        font-family: 'Space Grotesk', sans-serif;
    }}

    /* Cards / containers métriques — fond blanc avec ombre douce */
    div[data-testid="stMetric"] {{
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 8px rgba(45, 27, 105, 0.04);
        transition: all 0.25s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        border-color: {PALETTE["bleu_violet"]};
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(87, 103, 214, 0.12);
    }}
    div[data-testid="stMetric"] label {{
        color: #6b6b80 !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {PALETTE["bleu_nuit"]} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 1.6rem !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        line-height: 1.2 !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
        color: {PALETTE["bleu_violet"]} !important;
    }}

    /* Onglets */
    div[data-baseweb="tab-list"] {{
        background: #ffffff;
        border-radius: 12px;
        padding: 4px;
    }}

    /* Cards custom (réponses aux questions) — fond blanc */
    .question-card {{
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(45, 27, 105, 0.04);
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
    }}
    .question-card:hover {{
        box-shadow: 0 8px 24px rgba(87, 103, 214, 0.10);
        transform: translateY(-1px);
    }}
    .question-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {PALETTE["bleu_nuit"]}, {PALETTE["bleu_violet"]}, {PALETTE["lavande"]}, {PALETTE["mauve"]}, {PALETTE["orchidee"]}, {PALETTE["rose_pastel"]});
    }}
    .question-num {{
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: {PALETTE["bleu_violet"]};
        background: rgba(87, 103, 214, 0.08);
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 0.8rem;
        letter-spacing: 0.1em;
        border: 1px solid rgba(87, 103, 214, 0.2);
    }}
    .question-text {{
        color: #4a4a5e;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 1.2rem;
        line-height: 1.55;
    }}
    .question-answer {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 700;
        color: {PALETTE["bleu_nuit"]};
    }}
    .question-answer-sub {{
        color: #8a8aa0;
        font-size: 0.88rem;
        margin-top: 0.4rem;
    }}

    /* Header banner */
    .hero-banner {{
        background: linear-gradient(135deg, #ffffff 0%, #f0f1ff 100%);
        border-radius: 20px;
        padding: 2.2rem 2.8rem;
        border: 1px solid #e8eaf0;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(45, 27, 105, 0.05);
    }}
    .hero-banner::after {{
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 380px;
        height: 380px;
        background: radial-gradient(circle, rgba(235, 156, 239, 0.18) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }}
    .hero-title {{
        font-size: 2.6rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.1;
    }}
    .hero-subtitle {{
        color: #6b6b80 !important;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.04em;
    }}

    /* Section dividers */
    .section-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a2e !important;
        margin: 1.8rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid;
        border-image: linear-gradient(90deg, {PALETTE["bleu_violet"]}, {PALETTE["orchidee"]}, transparent) 1;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }}

    /* Tables */
    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e8eaf0;
        background: #ffffff;
    }}

    /* Hide footer streamlit */
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}

    /* Plotly transparent backgrounds */
    .js-plotly-plot, .plotly {{
        background: transparent !important;
    }}

    /* Caption */
    .caption-mono {{
        font-family: 'JetBrains Mono', monospace;
        color: #6b6b80;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
    }}

    /* Plotly — forcer la lisibilité du texte sur fond clair */
    .js-plotly-plot .plotly text {{
        fill: #1a1a2e !important;
    }}
    .js-plotly-plot .legend text {{
        fill: #1a1a2e !important;
    }}
    
    </style>
    """,
    unsafe_allow_html=True,
)

# ================================================================
# INITIALISATION DU MODÈLE ÉTOILE
# ================================================================
placeholder = st.empty()
with placeholder.container():
    st.title("Initialisation des données...")

tables = init_star_model()

if not tables:
    st.error("Impossible de charger le modèle étoile. Avez-vous exécuté les cellules d'export du notebook ETL.ipynb ?")
    st.stop()

placeholder.empty()  # Enlever le message d'initialisation

# ================================================================
# HELPERS
# ================================================================

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk, sans-serif", color="#1a1a2e", size=13),
    xaxis=dict(
        gridcolor="rgba(45, 45, 58, 0.08)",
        zerolinecolor="rgba(45, 45, 58, 0.15)",
        tickfont=dict(color="#1a1a2e", size=12),
        title_font=dict(color="#1a1a2e", size=13),
    ),
    yaxis=dict(
        gridcolor="rgba(45, 45, 58, 0.08)",
        zerolinecolor="rgba(45, 45, 58, 0.15)",
        tickfont=dict(color="#1a1a2e", size=12),
        title_font=dict(color="#1a1a2e", size=13),
    ),
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#e8eaf0",
        borderwidth=1,
        font=dict(color="#1a1a2e", size=12),
    ),
    hoverlabel=dict(
        bgcolor="#ffffff",
        bordercolor="#5767D6",
        font=dict(family="Space Grotesk, sans-serif", color="#1a1a2e", size=13),
    ),
)

def apply_layout(fig, height=420, title=None):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=16, color="#1a1a2e")))
    return fig

def question_card(num, question, answer, sub=None):
    sub_html = f'<div class="question-answer-sub">{sub}</div>' if sub else ''
    st.markdown(
        f"""
        <div class="question-card">
            <div class="question-num">QUESTION {num}</div>
            <div class="question-text">{question}</div>
            <div class="question-answer">{answer}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_title(icon, title):
    st.markdown(f'<div class="section-title">{icon} {title}</div>', unsafe_allow_html=True)


# ================================================================
# SIDEBAR — NAVIGATION
# ================================================================
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid rgba(205, 155, 228, 0.2); margin-bottom: 1rem;">
            <div style="font-family: 'Space Grotesk'; font-weight: 700; font-size: 1.5rem; color: white;">
                BGES <span style="color: {PALETTE['orchidee']};">·</span> Dashboard
            </div>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #cd9be4; letter-spacing: 0.1em; margin-top: 4px;">
                NF26
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Accueil",
            "👥 Effectifs",
            "💻 Matériel informatique",
            "✈️ Missions & déplacements",
            "🌍 Analyses transverses",
            "📊 Visualisations globales",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #6b6b80; line-height: 1.6;">
            <div style="margin-bottom: 8px;"><strong style="color: {PALETTE['bleu_violet']};">PÉRIODE</strong><br>Avril → Novembre 2026</div>
            <div style="margin-bottom: 8px;"><strong style="color: {PALETTE['bleu_violet']};">SITES</strong><br>Paris, Berlin, Londres,<br>NY, LA, Shanghai</div>
            <div><strong style="color: {PALETTE['bleu_violet']};">UNITÉ</strong><br>tCO₂e (équivalent CO₂)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ================================================================
# PAGE : ACCUEIL
# ================================================================
if page == "🏠 Accueil":
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">Bilan Gaz à Effet de Serre</div>
            <div class="hero-subtitle">Organisation internationale · 6 sites · Avril – Novembre 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Indicateurs principaux — calculés dynamiquement depuis le modèle étoile
    with st.spinner("Calcul des indicateurs carbone en cours..."):
        total_emissions, total_materiel, total_missions = calculate_total_impact(tables)
        df_site_impacts = calculate_impact_per_site(tables)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Émissions totales", f"{total_emissions:,.0f} tCO₂e")
    with c2:
        mission_pct = (total_missions/total_emissions*100) if total_emissions > 0 else 0
        st.metric("Missions", f"{total_missions:,.0f} tCO₂e")
    with c3:
        materiel_pct = (total_materiel/total_emissions*100) if total_emissions > 0 else 0
        st.metric("Matériel info.", f"{total_materiel:,.0f} tCO₂e")
    with c4:
        if not df_site_impacts.empty:
            site_max = df_site_impacts.iloc[0]
            st.metric("Site le + impactant", site_max["ID_SITE"], f"{site_max['TOT_IMPACT']:,.0f} tCO₂e")
        else:
            st.error("Impossible de calculer le site le + impactant (DataFrame vide). Voir terminal pour debug.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Deux colonnes : impact par site + camembert missions/matériel
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        section_title("📍", "Impact carbone par site")
        df_site = pd.DataFrame(IMPACT_TOTAL_SITE).sort_values("TOT_IMPACT", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_site["ID_SITE"],
            x=df_site["Emission_tCO2e"],
            name="Missions",
            orientation="h",
            marker=dict(color=PALETTE["bleu_violet"], line=dict(color=PALETTE["bleu_nuit"], width=1)),
        ))
        fig.add_trace(go.Bar(
            y=df_site["ID_SITE"],
            x=df_site["sum(IMPACT)"],
            name="Matériel info.",
            orientation="h",
            marker=dict(color=PALETTE["rose_pastel"], line=dict(color=PALETTE["orchidee"], width=1)),
        ))
        fig.update_layout(barmode="stack")
        apply_layout(fig, height=420)
        fig.update_layout(xaxis_title="tCO₂e", yaxis_title="")
        st.plotly_chart(fig, width='stretch')

    with col_right:
        section_title("🥧", "Répartition des sources")
        fig = go.Figure(data=[go.Pie(
            labels=["Missions", "Matériel info."],
            values=[total_missions, total_materiel],
            hole=0.65,
            marker=dict(colors=[PALETTE["bleu_violet"], PALETTE["rose_pastel"]], line=dict(color="rgba(0,0,0,0)", width=2)),
            textfont=dict(family="Space Grotesk", size=14, color="#ffffff"),
        )])
        fig.update_layout(
            annotations=[dict(text=f"<b>{total_emissions:,.0f}</b><br><span style='font-size:11px'>tCO₂e</span>",
                              font=dict(size=22, color="#f5f0ff"), showarrow=False)],
        )
        apply_layout(fig, height=420)
        st.plotly_chart(fig, width='stretch')

    # Évolution mensuelle
    section_title("📈", "Évolution mensuelle de l'empreinte carbone")
    df_month = pd.DataFrame(EMISSIONS_MENSUEL_GLOBAL).sort_values("MOIS")
    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    df_month["MOIS_LABEL"] = df_month["MOIS"].apply(lambda m: mois_noms[m - 1])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_month["MOIS_LABEL"], y=df_month["Emission_tCO2e"],
        name="Missions", marker=dict(color=PALETTE["bleu_violet"]),
    ))
    fig.add_trace(go.Bar(
        x=df_month["MOIS_LABEL"], y=df_month["sum(IMPACT)"],
        name="Matériel", marker=dict(color=PALETTE["rose_pastel"]),
    ))
    fig.add_trace(go.Scatter(
        x=df_month["MOIS_LABEL"], y=df_month["TOT_IMPACT"],
        name="Total", mode="lines+markers+text",
        line=dict(color=PALETTE["orchidee"], width=3),
        marker=dict(size=10, color=PALETTE["rose_pastel"], line=dict(color="white", width=2)),
        text=[f"{v:,.0f}" for v in df_month["TOT_IMPACT"]],
        textposition="top center",
        textfont=dict(family="JetBrains Mono", size=11, color="#f5f0ff"),
    ))
    fig.update_layout(barmode="stack")
    apply_layout(fig, height=450)
    fig.update_layout(yaxis_title="tCO₂e", xaxis_title="")
    st.plotly_chart(fig, width='stretch')


# ================================================================
# PAGE : EFFECTIFS (Q1, Q2, Q3)
# ================================================================
elif page == "👥 Effectifs":
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">Effectifs par fonction</div>
            <div class="hero-subtitle">Répartition des employés sur les 6 sites</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Calcul des indicateurs effectifs en cours..."):
        q1_value = query_q1(tables)
        q2_value = query_q2(tables)
        q3_value = query_q3(tables)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Cadres à Paris", f"{q1_value:,}")
    with c2:
        st.metric("Ing. Data aux USA", f"{q2_value:,}")
    with c3:
        st.metric("Ing. Informaticiens", f"{q3_value:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    section_title("📋", "Détails des questions")

    question_card(1, "Combien de cadres travaillent sur le site de Paris ?",
                  f"{q1_value:,} cadres", "Site de Paris uniquement")

    question_card(2, "Combien d'ingénieurs Data travaillent sur les sites aux États-Unis ?",
                  f"{q2_value:,} ingénieurs Data", "Sites de New-York et Los Angeles")

    question_card(3, "Combien d'ingénieurs informaticiens travaillent dans l'organisation (tous sites compris) ?",
                  f"{q3_value:,} ingénieurs informaticiens", "Total sur les 6 sites de l'organisation")


# ================================================================
# PAGE : MATÉRIEL INFORMATIQUE (Q4, Q5, Q6, Q7)
# ================================================================
elif page == "💻 Matériel informatique":
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">Matériel informatique</div>
            <div class="hero-subtitle">Achats et empreinte carbone des équipements</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Calcul des impacts matériel en cours..."):
        q4_value = query_q4(tables)
        q5_value = query_q5(tables)
        q6_value = query_q6(tables)
        q7_value = query_q7(tables)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("PC fixes achetés", f"{q4_value:,} Juin–Sep 2026")
    with c2:
        st.metric("Impact PC fixes s/écran", f"{q5_value:,.1f} tCO₂e Mai–Oct 2026")
    with c3:
        st.metric("Impact PC portables", f"{q6_value:,.1f} tCO₂e Ing. Data · LON+NY")
    with c4:
        st.metric("Impact écrans cadres", f"{q7_value:,.1f} tCO₂e Juil–Sep 2026")

    st.markdown("<br>", unsafe_allow_html=True)

    # Comparaison visuelle des impacts
    section_title("📊", "Comparaison des impacts par catégorie")
    cat_data = pd.DataFrame({
        "Catégorie": [
            "PC fixes sans écran<br>(mai–oct, tous sites)",
            "PC portables<br>(ing. Data, LON+NY)",
            "Écrans cadres<br>(juil–sep, tous sites)",
        ],
        "Impact": [q5_value, q6_value, q7_value],
    })
    fig = go.Figure(go.Bar(
        x=cat_data["Catégorie"], y=cat_data["Impact"],
        marker=dict(
            color=cat_data["Impact"],
            colorscale=[[0, PALETTE["bleu_violet"]], [0.5, PALETTE["mauve"]], [1, PALETTE["rose_pastel"]]],
            line=dict(color="rgba(255,255,255,0.2)", width=1),
        ),
        text=[f"{v:.1f} tCO₂e" for v in cat_data["Impact"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=12, color="#f5f0ff"),
    ))
    apply_layout(fig, height=420)
    fig.update_layout(yaxis_title="tCO₂e", xaxis_title="", showlegend=False)
    st.plotly_chart(fig, width='stretch')

    section_title("📋", "Détails des questions")

    question_card(4, "Combien de PC fixes ont été achetés par l'organisation entre juin et septembre 2026 ?",
                  f"{q4_value:,} PC fixes", "PC fixe sans écran + PC fixe tout-en-un")

    question_card(5, "Quel a été l'impact carbone des PC fixes sans écran entre mai et octobre 2026 ?",
                  f"{q5_value:.3f} tCO₂e")

    question_card(6, "Quel a été l'impact carbone des PC portables achetés par les ingénieurs Data entre mai et octobre 2026 sur les sites de Londres et New-York ?",
                  f"{q6_value:.3f} tCO₂e")

    question_card(7, "Quel a été l'impact carbone des écrans achetés par les cadres entre juillet et septembre 2026 sur tous les sites ?",
                  f"{q7_value:.1f} tCO₂e")


# ================================================================
# PAGE : MISSIONS & DÉPLACEMENTS (Q8, Q9, Q12, Q13, Q16, Q18)
# ================================================================
elif page == "✈️ Missions & déplacements":
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">Missions & déplacements</div>
            <div class="hero-subtitle">Analyse fine des déplacements professionnels</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Missions Europe", f"{Q8:,.0f} tCO₂e Mai–Oct 2026")
    with c2:
        st.metric("Inter-sites Sept.", f"{Q12:,.0f} tCO₂e Septembre 2026")
    with c3:
        st.metric("Séminaires LA", f"{Q13:,.0f} tCO₂e Juillet 2026")
    with c4:
        st.metric("Top destination", f"{Q16['destination']} {Q16['emission']:,.0f} tCO₂e")

    st.markdown("<br>", unsafe_allow_html=True)

    # Top 5 jours en avion + top destination
    col_left, col_right = st.columns(2)

    with col_left:
        section_title("📅", "Top 5 jours · missions avion (Europe)")
        df_top5 = pd.DataFrame(Q9)
        fig = go.Figure(go.Bar(
            y=df_top5["Date"].astype(str),
            x=df_top5["Emission_tCO2e"],
            orientation="h",
            marker=dict(
                color=df_top5["Emission_tCO2e"],
                colorscale=[[0, PALETTE["bleu_violet"]], [1, PALETTE["rose_pastel"]]],
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            text=[f"{v:.1f}" for v in df_top5["Emission_tCO2e"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=11, color="#f5f0ff"),
        ))
        apply_layout(fig, height=380)
        fig.update_layout(xaxis_title="tCO₂e", yaxis_title="", showlegend=False,
                          yaxis=dict(autorange="reversed", gridcolor="rgba(205, 155, 228, 0.12)"))
        st.plotly_chart(fig, width='stretch')

    with col_right:
        section_title("🏆", "Top 5 missions · site Paris")
        df_top_paris = pd.DataFrame(TOP_MISSIONS_PARIS).head(5)
        df_top_paris["LABEL"] = df_top_paris["VILLE_DEPART"] + " → " + df_top_paris["VILLE_DESTINATION"]
        fig = go.Figure(go.Bar(
            y=df_top_paris["LABEL"],
            x=df_top_paris["EMISSION"],
            orientation="h",
            marker=dict(
                color=df_top_paris["EMISSION"],
                colorscale=[[0, PALETTE["lavande"]], [1, PALETTE["orchidee"]]],
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            text=[f"{v:.2f}" for v in df_top_paris["EMISSION"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=11, color="#f5f0ff"),
            customdata=df_top_paris[["TYPE_MISSION", "TRANSPORT"]].values,
            hovertemplate="<b>%{y}</b><br>Type: %{customdata[0]}<br>Transport: %{customdata[1]}<br>Émission: %{x:.4f} tCO₂e<extra></extra>",
        ))
        apply_layout(fig, height=380)
        fig.update_layout(xaxis_title="tCO₂e", yaxis_title="", showlegend=False,
                          yaxis=dict(autorange="reversed", gridcolor="rgba(205, 155, 228, 0.12)"))
        st.plotly_chart(fig, width='stretch')

    section_title("📋", "Détails des questions")

    question_card(8, "Quel a été l'impact carbone des missions sur les sites Européens entre mai et octobre 2026 ?",
                  f"{Q8:,.2f} tCO₂e", "Sites de Paris, Berlin et Londres")

    # Question 9 — top 5 jours
    st.markdown(
        f"""
        <div class="question-card">
            <div class="question-num">QUESTION 9</div>
            <div class="question-text">Quels ont été les 5 jours les plus impactants concernant les missions en avion pour les sites Européens de l'organisation ?</div>
            <div style="font-family: 'JetBrains Mono'; color: #f5f0ff; line-height: 2;">
                {''.join([f'<div><span style="color:{PALETTE["orchidee"]};">{i+1}.</span> <span style="color:#cd9be4;">{d["Date"]}</span> &nbsp;→&nbsp; <span style="font-weight:600;">{d["Emission_tCO2e"]:.2f} tCO₂e</span></div>' for i, d in enumerate(Q9)])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    question_card(12, "Quel a été l'impact carbone des missions reliant chaque site (départ et arrivée = sites de l'organisation) durant le mois de septembre 2026 ?",
                  f"{Q12:.2f} tCO₂e", "Septembre 2026 · trajets inter-sites")

    question_card(13, "Quel a été l'impact carbone des séminaires en juillet 2026 pour les employés de Los Angeles ?",
                  f"{Q13:.2f} tCO₂e", "Type de mission : Conference")

    question_card(16, "Quelle destination a été la plus impactante (en cumul) entre mai et octobre 2026 ?",
                  Q16["destination"], f"Cumul d'émissions : {Q16['emission']:.2f} tCO₂e")

    question_card(18, "Quelles ont été les 5 missions les plus impactantes sur le site de Paris ?",
                  "Voir graphique ci-dessus", "Trajets dominants : Paris ↔ Wellington (avion)")


# ================================================================
# PAGE : ANALYSES TRANSVERSES (Q10, Q11, Q14, Q15, Q17)
# ================================================================
elif page == "🌍 Analyses transverses":
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">Analyses transverses</div>
            <div class="hero-subtitle">Comparaisons par secteur, site et catégorie de mission</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Secteur le + impactant", f"{Q10['secteur']} {Q10['emission']:,.0f} tCO₂e")
    with c2:
        st.metric("Site le + impactant", f"{Q11['site']} {Q11['emission']:,.0f} tCO₂e")
    with c3:
        st.metric("Conférences (top secteur)", f"{Q14['secteur']} {Q14['emission']:,.0f} tCO₂e")
    with c4:
        st.metric("Âge moyen ing. Data", f"{Q15:.1f} ans Formations Juil–Sep")

    st.markdown("<br>", unsafe_allow_html=True)

    # Impact total par secteur (Q10)
    col_left, col_right = st.columns(2)

    with col_left:
        section_title("👔", "Impact total par secteur d'activité")
        df_sect = pd.DataFrame(IMPACT_TOTAL_SECTEUR).sort_values("TOT_IMPACT", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_sect["FONCTION_PERSONNEL"], x=df_sect["Emission_tCO2e"],
            name="Missions", orientation="h",
            marker=dict(color=PALETTE["bleu_violet"]),
        ))
        fig.add_trace(go.Bar(
            y=df_sect["FONCTION_PERSONNEL"], x=df_sect["sum(IMPACT)"],
            name="Matériel", orientation="h",
            marker=dict(color=PALETTE["rose_pastel"]),
        ))
        fig.update_layout(barmode="stack")
        apply_layout(fig, height=400)
        fig.update_layout(xaxis_title="tCO₂e", yaxis_title="")
    st.plotly_chart(fig, width='stretch')

    with col_right:
        section_title("🏢", "Impact total par site")
        df_site = pd.DataFrame(IMPACT_TOTAL_SITE).sort_values("TOT_IMPACT", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_site["ID_SITE"], x=df_site["Emission_tCO2e"],
            name="Missions", orientation="h",
            marker=dict(color=PALETTE["bleu_violet"]),
        ))
        fig.add_trace(go.Bar(
            y=df_site["ID_SITE"], x=df_site["sum(IMPACT)"],
            name="Matériel", orientation="h",
            marker=dict(color=PALETTE["rose_pastel"]),
        ))
        fig.update_layout(barmode="stack")
        apply_layout(fig, height=400)
        fig.update_layout(xaxis_title="tCO₂e", yaxis_title="")
    st.plotly_chart(fig, width='stretch')

    # Top 3 catégories cadres Europe Mai (Q17)
    section_title("🥇", "Top 3 catégories de missions · cadres Europe · mai 2026")
    df_top3 = pd.DataFrame(TOP3_CADRES_EUROPE_MAI)
    fig = go.Figure(go.Bar(
        x=df_top3["TYPE_MISSION"], y=df_top3["EMISSION"],
        marker=dict(
            color=[PALETTE["bleu_violet"], PALETTE["mauve"], PALETTE["rose_pastel"]],
            line=dict(color="rgba(255,255,255,0.2)", width=1),
        ),
        text=[f"{v:.2f} tCO₂e" for v in df_top3["EMISSION"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=12, color="#f5f0ff"),
    ))
    apply_layout(fig, height=380)
    fig.update_layout(yaxis_title="tCO₂e", xaxis_title="", showlegend=False)
    st.plotly_chart(fig, width='stretch')

    section_title("📋", "Détails des questions")

    question_card(10, "Quel a été le secteur d'activité qui a eu le plus d'impact concernant les missions et le matériel informatique sur l'ensemble des sites ?",
                  Q10["secteur"], f"Impact total : {Q10['emission']:,.2f} tCO₂e")

    question_card(11, "Quel site a eu le plus d'impact concernant les missions et le matériel informatique sur l'ensemble des sites ?",
                  Q11["site"], f"Impact total : {Q11['emission']:,.2f} tCO₂e")

    question_card(14, "Quel secteur d'activité a été le plus impactant pour les missions « conférences » entre mai et septembre 2026 ?",
                  Q14["secteur"], f"Impact : {Q14['emission']:,.2f} tCO₂e")

    question_card(15, "Quel a été l'âge moyen des employés Ingénieurs Data qui sont partis en formations entre juillet et septembre 2026 ?",
                  f"{Q15:.2f} ans", "Type de mission : Vocational Training")

    # Q17 — top 3
    st.markdown(
        f"""
        <div class="question-card">
            <div class="question-num">QUESTION 17</div>
            <div class="question-text">Quelles ont été les trois catégories de missions les plus impactantes pour les cadres dans les sites Européens en mai 2026 ?</div>
            <div style="font-family: 'JetBrains Mono'; color: #f5f0ff; line-height: 2;">
                {''.join([f'<div><span style="color:{PALETTE["orchidee"]};">{i+1}.</span> <span style="font-weight:600;">{d["TYPE_MISSION"]}</span> &nbsp;→&nbsp; <span style="color:#cd9be4;">{d["EMISSION"]:.2f} tCO₂e</span></div>' for i, d in enumerate(TOP3_CADRES_EUROPE_MAI)])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ================================================================
# PAGE : VISUALISATIONS GLOBALES (Q19, Q20)
# ================================================================
elif page == "📊 Visualisations globales":
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">Visualisations globales</div>
            <div class="hero-subtitle">Vue d'ensemble mensuelle · transports · sites</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Question 19 — Impact mensuel par transport et site (subplots)
    section_title("✈️", "Q19 · Impact carbone mensuel des missions par transport et par site")

    df = pd.DataFrame(EMISSIONS_MENSUEL_TRANSPORT_SITE)
    sites_present = sorted(df["ID_SITE"].unique())
    transports = sorted(df["TRANSPORT"].unique())
    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']

    # Couleurs distinctes par transport
    transport_colors = {
        "Avion": PALETTE["bleu_nuit"],
        "Train": PALETTE["bleu_violet"],
        "Taxi": PALETTE["mauve"],
        "Transports en commun": PALETTE["rose_pastel"],
    }

    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=sites_present,
        vertical_spacing=0.18, horizontal_spacing=0.08,
    )

    show_legend = {t: True for t in transports}
    for idx, site in enumerate(sites_present):
        row = idx // 3 + 1
        col = idx % 3 + 1
        site_data = df[df["ID_SITE"] == site]
        for transport in transports:
            t_data = site_data[site_data["TRANSPORT"] == transport].sort_values("MOIS")
            fig.add_trace(
                go.Bar(
                    x=[mois_noms[m - 1] for m in t_data["MOIS"]],
                    y=t_data["EMISSION"],
                    name=transport,
                    marker=dict(color=transport_colors.get(transport, PALETTE["lavande"])),
                    showlegend=show_legend[transport],
                    legendgroup=transport,
                ),
                row=row, col=col,
            )
            show_legend[transport] = False

    fig.update_layout(
        barmode="stack",
        height=620,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk, sans-serif", color="#e8e1ff", size=12),
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    fig.update_xaxes(gridcolor="rgba(205, 155, 228, 0.12)", showgrid=False)
    fig.update_yaxes(gridcolor="rgba(205, 155, 228, 0.12)", title_text="tCO₂e", title_font=dict(size=10))
    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(family="Space Grotesk", size=13, color="#f5f0ff")

    st.plotly_chart(fig, width='stretch')

    # Question 20 — Impact carbone global mensuel
    section_title("🌍", "Q20 · Impact carbone global mensuel de l'organisation")

    df_global = pd.DataFrame(EMISSIONS_MENSUEL_GLOBAL).sort_values("MOIS")
    df_global["MOIS_LABEL"] = df_global["MOIS"].apply(lambda m: mois_noms[m - 1])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_global["MOIS_LABEL"], y=df_global["Emission_tCO2e"],
        name="Missions",
        marker=dict(color=PALETTE["bleu_violet"], line=dict(color=PALETTE["bleu_nuit"], width=1)),
    ))
    fig.add_trace(go.Bar(
        x=df_global["MOIS_LABEL"], y=df_global["sum(IMPACT)"],
        name="Matériel informatique",
        marker=dict(color=PALETTE["rose_pastel"], line=dict(color=PALETTE["orchidee"], width=1)),
    ))
    fig.add_trace(go.Scatter(
        x=df_global["MOIS_LABEL"], y=df_global["TOT_IMPACT"],
        name="Total", mode="lines+markers+text",
        line=dict(color=PALETTE["orchidee"], width=3),
        marker=dict(size=12, color=PALETTE["rose_pastel"], line=dict(color="white", width=2)),
        text=[f"{v:,.0f}" for v in df_global["TOT_IMPACT"]],
        textposition="top center",
        textfont=dict(family="JetBrains Mono", size=11, color="#f5f0ff"),
    ))
    fig.update_layout(barmode="stack")
    apply_layout(fig, height=500)
    fig.update_layout(yaxis_title="tCO₂e", xaxis_title="Mois")
    st.plotly_chart(fig, width='stretch')

    # Tableau récapitulatif
    section_title("📋", "Données mensuelles détaillées")
    df_display = df_global[["MOIS_LABEL", "Emission_tCO2e", "sum(IMPACT)", "TOT_IMPACT"]].copy()
    df_display.columns = ["Mois", "Missions (tCO₂e)", "Matériel (tCO₂e)", "Total (tCO₂e)"]
    df_display["Missions (tCO₂e)"] = df_display["Missions (tCO₂e)"].round(2)
    df_display["Matériel (tCO₂e)"] = df_display["Matériel (tCO₂e)"].round(2)
    df_display["Total (tCO₂e)"] = df_display["Total (tCO₂e)"].round(2)
    st.dataframe(df_display, width='stretch', hide_index=True)
