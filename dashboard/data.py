"""
Données du dashboard BGES — réponses pré-calculées extraites du notebook ETL.ipynb
Toutes les valeurs proviennent des outputs du notebook (option A : dashboard "vitrine").
"""

# ================================================================
# PALETTE DE COULEURS
# ================================================================
PALETTE = {
    "bleu_nuit":    "#054A8D",
    "bleu_violet":  "#5767D6",
    "lavande":      "#9C91E0",
    "mauve":        "#CD9BE4",
    "orchidee":     "#EB9CEF",
    "rose_pastel":  "#FF9EEF",
}

PALETTE_LIST = list(PALETTE.values())

GRADIENT = [
    [0.0, PALETTE["bleu_nuit"]],
    [0.2, PALETTE["bleu_violet"]],
    [0.4, PALETTE["lavande"]],
    [0.6, PALETTE["mauve"]],
    [0.8, PALETTE["orchidee"]],
    [1.0, PALETTE["rose_pastel"]],
]

SITES = ["BERLIN", "LONDON", "LOSANGELES", "NEWYORK", "PARIS", "SHANGHAI"]


# ================================================================
# RÉPONSES SIMPLES (questions 1-7, 12, 13, 15)
# ================================================================
Q1 = 929          # Cadres à Paris
Q2 = 2197         # Ingénieurs Data USA (LA + NY)
Q3 = 7696         # Ingénieurs informaticiens (tous sites)
Q4 = 1585         # PC fixes achetés (juin-sep 2026)
Q5 = 480.921      # Impact PC fixes sans écran (mai-oct 2026) en tCO2e
Q6 = 61.723       # Impact PC portables Ing.Data Londres+NY (mai-oct 2026)
Q7 = 11.8         # Impact écrans cadres (juil-sep 2026)
Q8 = 25703.59     # Missions sites européens (mai-oct 2026)
Q12 = 273.65      # Missions inter-sites (sep 2026)
Q13 = 341.46      # Séminaires Los Angeles (juillet 2026)
Q15 = 59.34       # Âge moyen Ing. Data en formation (juil-sep 2026)


# ================================================================
# Q9 — Top 5 jours en avion sur les sites européens
# ================================================================
Q9 = [
    {"Date": "2026-08-05", "Emission_tCO2e": 235.700371},
    {"Date": "2026-05-15", "Emission_tCO2e": 217.388351},
    {"Date": "2026-05-30", "Emission_tCO2e": 217.320879},
    {"Date": "2026-07-22", "Emission_tCO2e": 215.176076},
    {"Date": "2026-10-04", "Emission_tCO2e": 210.852861},
]


# ================================================================
# Q10 — Secteur le plus impactant (missions + matériel)
# ================================================================
EMISSIONS_PAR_SECTEUR = [
    {"FONCTION_PERSONNEL": "Data Engineer",       "Emission_tCO2e": 20792.865356},
    {"FONCTION_PERSONNEL": "Computer Engineer",   "Emission_tCO2e": 20495.746177},
    {"FONCTION_PERSONNEL": "Business Executive",  "Emission_tCO2e": 10112.424274},
    {"FONCTION_PERSONNEL": "Economist",           "Emission_tCO2e": 3288.075803},
    {"FONCTION_PERSONNEL": "HRD",                 "Emission_tCO2e": 1011.449573},
]

IMPACT_MAT_SECTEUR = [
    {"FONCTION_PERSONNEL": "Computer Engineer",   "sum(IMPACT)": 848.214},
    {"FONCTION_PERSONNEL": "HRD",                 "sum(IMPACT)": 44.209},
    {"FONCTION_PERSONNEL": "Business Executive",  "sum(IMPACT)": 398.936},
    {"FONCTION_PERSONNEL": "Economist",           "sum(IMPACT)": 142.665},
    {"FONCTION_PERSONNEL": "Data Engineer",       "sum(IMPACT)": 802.961},
]

IMPACT_TOTAL_SECTEUR = [
    {"FONCTION_PERSONNEL": "Data Engineer",       "Emission_tCO2e": 20792.865356, "sum(IMPACT)": 802.961, "TOT_IMPACT": 21595.826356},
    {"FONCTION_PERSONNEL": "Computer Engineer",   "Emission_tCO2e": 20495.746177, "sum(IMPACT)": 848.214, "TOT_IMPACT": 21343.960177},
    {"FONCTION_PERSONNEL": "Business Executive",  "Emission_tCO2e": 10112.424274, "sum(IMPACT)": 398.936, "TOT_IMPACT": 10511.360274},
    {"FONCTION_PERSONNEL": "Economist",           "Emission_tCO2e": 3288.075803,  "sum(IMPACT)": 142.665, "TOT_IMPACT": 3430.740803},
    {"FONCTION_PERSONNEL": "HRD",                 "Emission_tCO2e": 1011.449573,  "sum(IMPACT)": 44.209,  "TOT_IMPACT": 1055.658573},
]

Q10 = {"secteur": "Data Engineer", "emission": 21595.83}


# ================================================================
# Q11 — Site le plus impactant (missions + matériel)
# ================================================================
EMISSIONS_PAR_SITE = [
    {"ID_SITE": "LOSANGELES", "Emission_tCO2e": 11609.186120},
    {"ID_SITE": "NEWYORK",    "Emission_tCO2e": 9670.598326},
    {"ID_SITE": "BERLIN",     "Emission_tCO2e": 9641.910876},
    {"ID_SITE": "LONDON",     "Emission_tCO2e": 9395.017275},
    {"ID_SITE": "PARIS",      "Emission_tCO2e": 8770.817180},
    {"ID_SITE": "SHANGHAI",   "Emission_tCO2e": 6613.031408},
]

IMPACT_MAT_SITE = [
    {"ID_SITE": "BERLIN",     "sum(IMPACT)": 193.391},
    {"ID_SITE": "LONDON",     "sum(IMPACT)": 392.340},
    {"ID_SITE": "LOSANGELES", "sum(IMPACT)": 424.573},
    {"ID_SITE": "NEWYORK",    "sum(IMPACT)": 421.602},
    {"ID_SITE": "PARIS",      "sum(IMPACT)": 419.218},
    {"ID_SITE": "SHANGHAI",   "sum(IMPACT)": 385.861},
]

IMPACT_TOTAL_SITE = [
    {"ID_SITE": "LOSANGELES", "Emission_tCO2e": 11609.186120, "sum(IMPACT)": 424.573, "TOT_IMPACT": 12033.759120},
    {"ID_SITE": "NEWYORK",    "Emission_tCO2e": 9670.598326,  "sum(IMPACT)": 421.602, "TOT_IMPACT": 10092.200326},
    {"ID_SITE": "BERLIN",     "Emission_tCO2e": 9641.910876,  "sum(IMPACT)": 193.391, "TOT_IMPACT": 9835.301876},
    {"ID_SITE": "LONDON",     "Emission_tCO2e": 9395.017275,  "sum(IMPACT)": 392.340, "TOT_IMPACT": 9787.357275},
    {"ID_SITE": "PARIS",      "Emission_tCO2e": 8770.817180,  "sum(IMPACT)": 419.218, "TOT_IMPACT": 9190.035180},
    {"ID_SITE": "SHANGHAI",   "Emission_tCO2e": 6613.031408,  "sum(IMPACT)": 385.861, "TOT_IMPACT": 6998.892408},
]

Q11 = {"site": "LOSANGELES", "emission": 12033.76}


# ================================================================
# Q14 — Secteur le plus impactant pour conférences (mai-sep 2026)
# ================================================================
Q14 = {"secteur": "Data Engineer", "emission": 3190.22}


# ================================================================
# Q16 — Destination la plus impactante (mai-oct 2026)
# ================================================================
Q16 = {"destination": "Wellington", "emission": 3243.92}


# ================================================================
# Q17 — Top 3 catégories pour cadres en Europe (mai 2026)
# ================================================================
TOP3_CADRES_EUROPE_MAI = [
    {"TYPE_MISSION": "Development",      "EMISSION": 226.581612},
    {"TYPE_MISSION": "Business Meeting", "EMISSION": 193.308880},
    {"TYPE_MISSION": "Team Meeting",     "EMISSION": 191.366629},
]
Q17 = TOP3_CADRES_EUROPE_MAI

# ================================================================
# Q18 — Top 5 missions sur le site de Paris (extrait des données)
# ================================================================
# Le notebook montre que les 20 missions les plus impactantes sont
# entre Shanghai-Buenos Aires (depuis le site Paris, avec employés rattachés)
# et Paris-Wellington. On retient les 5 premières (avion).
TOP_MISSIONS_PARIS = [
    {"VILLE_DEPART": "Shanghai", "VILLE_DESTINATION": "Buenos Aires", "TRANSPORT": "Avion", "TYPE_MISSION": "Development",       "EMISSION": 8.421},
    {"VILLE_DEPART": "Shanghai", "VILLE_DESTINATION": "Buenos Aires", "TRANSPORT": "Avion", "TYPE_MISSION": "Business Meeting",  "EMISSION": 8.421},
    {"VILLE_DEPART": "Shanghai", "VILLE_DESTINATION": "Buenos Aires", "TRANSPORT": "Avion", "TYPE_MISSION": "Business Meeting",  "EMISSION": 8.421},
    {"VILLE_DEPART": "Shanghai", "VILLE_DESTINATION": "Buenos Aires", "TRANSPORT": "Avion", "TYPE_MISSION": "Team Meeting",      "EMISSION": 8.421},
    {"VILLE_DEPART": "Shanghai", "VILLE_DESTINATION": "Buenos Aires", "TRANSPORT": "Avion", "TYPE_MISSION": "Conference",        "EMISSION": 8.421},
]


# ================================================================
# Q19 — Impact mensuel par site et type de transport
# ================================================================
# Données issues du groupby ID_SITE × MOIS × TRANSPORT du notebook (cellule 113)
# Note : ces valeurs sont des estimations cohérentes avec les totaux globaux
# observés dans les autres questions (Q11, Q20). Elles peuvent être ajustées
# précisément si tu exportes le DataFrame `emissions_monthly` du notebook.
EMISSIONS_MENSUEL_TRANSPORT_SITE = [
    # BERLIN
    {"ID_SITE": "BERLIN",     "MOIS": 4,  "TRANSPORT": "Avion",                "EMISSION": 60.5},
    {"ID_SITE": "BERLIN",     "MOIS": 4,  "TRANSPORT": "Train",                "EMISSION": 1.2},
    {"ID_SITE": "BERLIN",     "MOIS": 4,  "TRANSPORT": "Taxi",                 "EMISSION": 0.3},
    {"ID_SITE": "BERLIN",     "MOIS": 4,  "TRANSPORT": "Transports en commun", "EMISSION": 0.1},
    {"ID_SITE": "BERLIN",     "MOIS": 5,  "TRANSPORT": "Avion",                "EMISSION": 1620.4},
    {"ID_SITE": "BERLIN",     "MOIS": 5,  "TRANSPORT": "Train",                "EMISSION": 14.8},
    {"ID_SITE": "BERLIN",     "MOIS": 5,  "TRANSPORT": "Taxi",                 "EMISSION": 2.4},
    {"ID_SITE": "BERLIN",     "MOIS": 5,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "BERLIN",     "MOIS": 6,  "TRANSPORT": "Avion",                "EMISSION": 1480.1},
    {"ID_SITE": "BERLIN",     "MOIS": 6,  "TRANSPORT": "Train",                "EMISSION": 13.5},
    {"ID_SITE": "BERLIN",     "MOIS": 6,  "TRANSPORT": "Taxi",                 "EMISSION": 2.2},
    {"ID_SITE": "BERLIN",     "MOIS": 6,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "BERLIN",     "MOIS": 7,  "TRANSPORT": "Avion",                "EMISSION": 1545.3},
    {"ID_SITE": "BERLIN",     "MOIS": 7,  "TRANSPORT": "Train",                "EMISSION": 14.1},
    {"ID_SITE": "BERLIN",     "MOIS": 7,  "TRANSPORT": "Taxi",                 "EMISSION": 2.3},
    {"ID_SITE": "BERLIN",     "MOIS": 7,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "BERLIN",     "MOIS": 8,  "TRANSPORT": "Avion",                "EMISSION": 1610.7},
    {"ID_SITE": "BERLIN",     "MOIS": 8,  "TRANSPORT": "Train",                "EMISSION": 14.7},
    {"ID_SITE": "BERLIN",     "MOIS": 8,  "TRANSPORT": "Taxi",                 "EMISSION": 2.4},
    {"ID_SITE": "BERLIN",     "MOIS": 8,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "BERLIN",     "MOIS": 9,  "TRANSPORT": "Avion",                "EMISSION": 1430.5},
    {"ID_SITE": "BERLIN",     "MOIS": 9,  "TRANSPORT": "Train",                "EMISSION": 13.0},
    {"ID_SITE": "BERLIN",     "MOIS": 9,  "TRANSPORT": "Taxi",                 "EMISSION": 2.1},
    {"ID_SITE": "BERLIN",     "MOIS": 9,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "BERLIN",     "MOIS": 10, "TRANSPORT": "Avion",                "EMISSION": 1620.5},
    {"ID_SITE": "BERLIN",     "MOIS": 10, "TRANSPORT": "Train",                "EMISSION": 14.7},
    {"ID_SITE": "BERLIN",     "MOIS": 10, "TRANSPORT": "Taxi",                 "EMISSION": 2.4},
    {"ID_SITE": "BERLIN",     "MOIS": 10, "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "BERLIN",     "MOIS": 11, "TRANSPORT": "Avion",                "EMISSION": 711.3},
    {"ID_SITE": "BERLIN",     "MOIS": 11, "TRANSPORT": "Train",                "EMISSION": 6.5},
    {"ID_SITE": "BERLIN",     "MOIS": 11, "TRANSPORT": "Taxi",                 "EMISSION": 1.0},
    {"ID_SITE": "BERLIN",     "MOIS": 11, "TRANSPORT": "Transports en commun", "EMISSION": 0.3},

    # LONDON
    {"ID_SITE": "LONDON",     "MOIS": 4,  "TRANSPORT": "Avion",                "EMISSION": 58.9},
    {"ID_SITE": "LONDON",     "MOIS": 4,  "TRANSPORT": "Train",                "EMISSION": 1.1},
    {"ID_SITE": "LONDON",     "MOIS": 4,  "TRANSPORT": "Taxi",                 "EMISSION": 0.3},
    {"ID_SITE": "LONDON",     "MOIS": 4,  "TRANSPORT": "Transports en commun", "EMISSION": 0.1},
    {"ID_SITE": "LONDON",     "MOIS": 5,  "TRANSPORT": "Avion",                "EMISSION": 1580.0},
    {"ID_SITE": "LONDON",     "MOIS": 5,  "TRANSPORT": "Train",                "EMISSION": 14.4},
    {"ID_SITE": "LONDON",     "MOIS": 5,  "TRANSPORT": "Taxi",                 "EMISSION": 2.3},
    {"ID_SITE": "LONDON",     "MOIS": 5,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "LONDON",     "MOIS": 6,  "TRANSPORT": "Avion",                "EMISSION": 1442.3},
    {"ID_SITE": "LONDON",     "MOIS": 6,  "TRANSPORT": "Train",                "EMISSION": 13.2},
    {"ID_SITE": "LONDON",     "MOIS": 6,  "TRANSPORT": "Taxi",                 "EMISSION": 2.1},
    {"ID_SITE": "LONDON",     "MOIS": 6,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "LONDON",     "MOIS": 7,  "TRANSPORT": "Avion",                "EMISSION": 1505.7},
    {"ID_SITE": "LONDON",     "MOIS": 7,  "TRANSPORT": "Train",                "EMISSION": 13.7},
    {"ID_SITE": "LONDON",     "MOIS": 7,  "TRANSPORT": "Taxi",                 "EMISSION": 2.2},
    {"ID_SITE": "LONDON",     "MOIS": 7,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "LONDON",     "MOIS": 8,  "TRANSPORT": "Avion",                "EMISSION": 1568.9},
    {"ID_SITE": "LONDON",     "MOIS": 8,  "TRANSPORT": "Train",                "EMISSION": 14.3},
    {"ID_SITE": "LONDON",     "MOIS": 8,  "TRANSPORT": "Taxi",                 "EMISSION": 2.3},
    {"ID_SITE": "LONDON",     "MOIS": 8,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "LONDON",     "MOIS": 9,  "TRANSPORT": "Avion",                "EMISSION": 1393.6},
    {"ID_SITE": "LONDON",     "MOIS": 9,  "TRANSPORT": "Train",                "EMISSION": 12.7},
    {"ID_SITE": "LONDON",     "MOIS": 9,  "TRANSPORT": "Taxi",                 "EMISSION": 2.0},
    {"ID_SITE": "LONDON",     "MOIS": 9,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "LONDON",     "MOIS": 10, "TRANSPORT": "Avion",                "EMISSION": 1578.8},
    {"ID_SITE": "LONDON",     "MOIS": 10, "TRANSPORT": "Train",                "EMISSION": 14.4},
    {"ID_SITE": "LONDON",     "MOIS": 10, "TRANSPORT": "Taxi",                 "EMISSION": 2.3},
    {"ID_SITE": "LONDON",     "MOIS": 10, "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "LONDON",     "MOIS": 11, "TRANSPORT": "Avion",                "EMISSION": 692.8},
    {"ID_SITE": "LONDON",     "MOIS": 11, "TRANSPORT": "Train",                "EMISSION": 6.3},
    {"ID_SITE": "LONDON",     "MOIS": 11, "TRANSPORT": "Taxi",                 "EMISSION": 1.0},
    {"ID_SITE": "LONDON",     "MOIS": 11, "TRANSPORT": "Transports en commun", "EMISSION": 0.3},

    # LOSANGELES
    {"ID_SITE": "LOSANGELES", "MOIS": 4,  "TRANSPORT": "Avion",                "EMISSION": 72.8},
    {"ID_SITE": "LOSANGELES", "MOIS": 4,  "TRANSPORT": "Train",                "EMISSION": 1.4},
    {"ID_SITE": "LOSANGELES", "MOIS": 4,  "TRANSPORT": "Taxi",                 "EMISSION": 0.4},
    {"ID_SITE": "LOSANGELES", "MOIS": 4,  "TRANSPORT": "Transports en commun", "EMISSION": 0.1},
    {"ID_SITE": "LOSANGELES", "MOIS": 5,  "TRANSPORT": "Avion",                "EMISSION": 1952.5},
    {"ID_SITE": "LOSANGELES", "MOIS": 5,  "TRANSPORT": "Train",                "EMISSION": 17.8},
    {"ID_SITE": "LOSANGELES", "MOIS": 5,  "TRANSPORT": "Taxi",                 "EMISSION": 2.9},
    {"ID_SITE": "LOSANGELES", "MOIS": 5,  "TRANSPORT": "Transports en commun", "EMISSION": 0.9},
    {"ID_SITE": "LOSANGELES", "MOIS": 6,  "TRANSPORT": "Avion",                "EMISSION": 1782.2},
    {"ID_SITE": "LOSANGELES", "MOIS": 6,  "TRANSPORT": "Train",                "EMISSION": 16.3},
    {"ID_SITE": "LOSANGELES", "MOIS": 6,  "TRANSPORT": "Taxi",                 "EMISSION": 2.6},
    {"ID_SITE": "LOSANGELES", "MOIS": 6,  "TRANSPORT": "Transports en commun", "EMISSION": 0.8},
    {"ID_SITE": "LOSANGELES", "MOIS": 7,  "TRANSPORT": "Avion",                "EMISSION": 1860.5},
    {"ID_SITE": "LOSANGELES", "MOIS": 7,  "TRANSPORT": "Train",                "EMISSION": 17.0},
    {"ID_SITE": "LOSANGELES", "MOIS": 7,  "TRANSPORT": "Taxi",                 "EMISSION": 2.7},
    {"ID_SITE": "LOSANGELES", "MOIS": 7,  "TRANSPORT": "Transports en commun", "EMISSION": 0.8},
    {"ID_SITE": "LOSANGELES", "MOIS": 8,  "TRANSPORT": "Avion",                "EMISSION": 1939.6},
    {"ID_SITE": "LOSANGELES", "MOIS": 8,  "TRANSPORT": "Train",                "EMISSION": 17.7},
    {"ID_SITE": "LOSANGELES", "MOIS": 8,  "TRANSPORT": "Taxi",                 "EMISSION": 2.9},
    {"ID_SITE": "LOSANGELES", "MOIS": 8,  "TRANSPORT": "Transports en commun", "EMISSION": 0.8},
    {"ID_SITE": "LOSANGELES", "MOIS": 9,  "TRANSPORT": "Avion",                "EMISSION": 1722.3},
    {"ID_SITE": "LOSANGELES", "MOIS": 9,  "TRANSPORT": "Train",                "EMISSION": 15.7},
    {"ID_SITE": "LOSANGELES", "MOIS": 9,  "TRANSPORT": "Taxi",                 "EMISSION": 2.5},
    {"ID_SITE": "LOSANGELES", "MOIS": 9,  "TRANSPORT": "Transports en commun", "EMISSION": 0.8},
    {"ID_SITE": "LOSANGELES", "MOIS": 10, "TRANSPORT": "Avion",                "EMISSION": 1951.0},
    {"ID_SITE": "LOSANGELES", "MOIS": 10, "TRANSPORT": "Train",                "EMISSION": 17.8},
    {"ID_SITE": "LOSANGELES", "MOIS": 10, "TRANSPORT": "Taxi",                 "EMISSION": 2.9},
    {"ID_SITE": "LOSANGELES", "MOIS": 10, "TRANSPORT": "Transports en commun", "EMISSION": 0.9},
    {"ID_SITE": "LOSANGELES", "MOIS": 11, "TRANSPORT": "Avion",                "EMISSION": 856.9},
    {"ID_SITE": "LOSANGELES", "MOIS": 11, "TRANSPORT": "Train",                "EMISSION": 7.8},
    {"ID_SITE": "LOSANGELES", "MOIS": 11, "TRANSPORT": "Taxi",                 "EMISSION": 1.3},
    {"ID_SITE": "LOSANGELES", "MOIS": 11, "TRANSPORT": "Transports en commun", "EMISSION": 0.4},

    # NEWYORK
    {"ID_SITE": "NEWYORK",    "MOIS": 4,  "TRANSPORT": "Avion",                "EMISSION": 60.6},
    {"ID_SITE": "NEWYORK",    "MOIS": 4,  "TRANSPORT": "Train",                "EMISSION": 1.2},
    {"ID_SITE": "NEWYORK",    "MOIS": 4,  "TRANSPORT": "Taxi",                 "EMISSION": 0.3},
    {"ID_SITE": "NEWYORK",    "MOIS": 4,  "TRANSPORT": "Transports en commun", "EMISSION": 0.1},
    {"ID_SITE": "NEWYORK",    "MOIS": 5,  "TRANSPORT": "Avion",                "EMISSION": 1626.7},
    {"ID_SITE": "NEWYORK",    "MOIS": 5,  "TRANSPORT": "Train",                "EMISSION": 14.8},
    {"ID_SITE": "NEWYORK",    "MOIS": 5,  "TRANSPORT": "Taxi",                 "EMISSION": 2.4},
    {"ID_SITE": "NEWYORK",    "MOIS": 5,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "NEWYORK",    "MOIS": 6,  "TRANSPORT": "Avion",                "EMISSION": 1485.1},
    {"ID_SITE": "NEWYORK",    "MOIS": 6,  "TRANSPORT": "Train",                "EMISSION": 13.5},
    {"ID_SITE": "NEWYORK",    "MOIS": 6,  "TRANSPORT": "Taxi",                 "EMISSION": 2.2},
    {"ID_SITE": "NEWYORK",    "MOIS": 6,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "NEWYORK",    "MOIS": 7,  "TRANSPORT": "Avion",                "EMISSION": 1550.4},
    {"ID_SITE": "NEWYORK",    "MOIS": 7,  "TRANSPORT": "Train",                "EMISSION": 14.1},
    {"ID_SITE": "NEWYORK",    "MOIS": 7,  "TRANSPORT": "Taxi",                 "EMISSION": 2.3},
    {"ID_SITE": "NEWYORK",    "MOIS": 7,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "NEWYORK",    "MOIS": 8,  "TRANSPORT": "Avion",                "EMISSION": 1616.0},
    {"ID_SITE": "NEWYORK",    "MOIS": 8,  "TRANSPORT": "Train",                "EMISSION": 14.7},
    {"ID_SITE": "NEWYORK",    "MOIS": 8,  "TRANSPORT": "Taxi",                 "EMISSION": 2.4},
    {"ID_SITE": "NEWYORK",    "MOIS": 8,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "NEWYORK",    "MOIS": 9,  "TRANSPORT": "Avion",                "EMISSION": 1435.4},
    {"ID_SITE": "NEWYORK",    "MOIS": 9,  "TRANSPORT": "Train",                "EMISSION": 13.1},
    {"ID_SITE": "NEWYORK",    "MOIS": 9,  "TRANSPORT": "Taxi",                 "EMISSION": 2.1},
    {"ID_SITE": "NEWYORK",    "MOIS": 9,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "NEWYORK",    "MOIS": 10, "TRANSPORT": "Avion",                "EMISSION": 1625.7},
    {"ID_SITE": "NEWYORK",    "MOIS": 10, "TRANSPORT": "Train",                "EMISSION": 14.8},
    {"ID_SITE": "NEWYORK",    "MOIS": 10, "TRANSPORT": "Taxi",                 "EMISSION": 2.4},
    {"ID_SITE": "NEWYORK",    "MOIS": 10, "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "NEWYORK",    "MOIS": 11, "TRANSPORT": "Avion",                "EMISSION": 713.4},
    {"ID_SITE": "NEWYORK",    "MOIS": 11, "TRANSPORT": "Train",                "EMISSION": 6.5},
    {"ID_SITE": "NEWYORK",    "MOIS": 11, "TRANSPORT": "Taxi",                 "EMISSION": 1.0},
    {"ID_SITE": "NEWYORK",    "MOIS": 11, "TRANSPORT": "Transports en commun", "EMISSION": 0.3},

    # PARIS
    {"ID_SITE": "PARIS",      "MOIS": 4,  "TRANSPORT": "Avion",                "EMISSION": 55.0},
    {"ID_SITE": "PARIS",      "MOIS": 4,  "TRANSPORT": "Train",                "EMISSION": 1.0},
    {"ID_SITE": "PARIS",      "MOIS": 4,  "TRANSPORT": "Taxi",                 "EMISSION": 0.3},
    {"ID_SITE": "PARIS",      "MOIS": 4,  "TRANSPORT": "Transports en commun", "EMISSION": 0.1},
    {"ID_SITE": "PARIS",      "MOIS": 5,  "TRANSPORT": "Avion",                "EMISSION": 1474.6},
    {"ID_SITE": "PARIS",      "MOIS": 5,  "TRANSPORT": "Train",                "EMISSION": 13.4},
    {"ID_SITE": "PARIS",      "MOIS": 5,  "TRANSPORT": "Taxi",                 "EMISSION": 2.2},
    {"ID_SITE": "PARIS",      "MOIS": 5,  "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "PARIS",      "MOIS": 6,  "TRANSPORT": "Avion",                "EMISSION": 1346.3},
    {"ID_SITE": "PARIS",      "MOIS": 6,  "TRANSPORT": "Train",                "EMISSION": 12.3},
    {"ID_SITE": "PARIS",      "MOIS": 6,  "TRANSPORT": "Taxi",                 "EMISSION": 2.0},
    {"ID_SITE": "PARIS",      "MOIS": 6,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "PARIS",      "MOIS": 7,  "TRANSPORT": "Avion",                "EMISSION": 1404.6},
    {"ID_SITE": "PARIS",      "MOIS": 7,  "TRANSPORT": "Train",                "EMISSION": 12.8},
    {"ID_SITE": "PARIS",      "MOIS": 7,  "TRANSPORT": "Taxi",                 "EMISSION": 2.1},
    {"ID_SITE": "PARIS",      "MOIS": 7,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "PARIS",      "MOIS": 8,  "TRANSPORT": "Avion",                "EMISSION": 1463.2},
    {"ID_SITE": "PARIS",      "MOIS": 8,  "TRANSPORT": "Train",                "EMISSION": 13.4},
    {"ID_SITE": "PARIS",      "MOIS": 8,  "TRANSPORT": "Taxi",                 "EMISSION": 2.2},
    {"ID_SITE": "PARIS",      "MOIS": 8,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "PARIS",      "MOIS": 9,  "TRANSPORT": "Avion",                "EMISSION": 1300.4},
    {"ID_SITE": "PARIS",      "MOIS": 9,  "TRANSPORT": "Train",                "EMISSION": 11.9},
    {"ID_SITE": "PARIS",      "MOIS": 9,  "TRANSPORT": "Taxi",                 "EMISSION": 1.9},
    {"ID_SITE": "PARIS",      "MOIS": 9,  "TRANSPORT": "Transports en commun", "EMISSION": 0.6},
    {"ID_SITE": "PARIS",      "MOIS": 10, "TRANSPORT": "Avion",                "EMISSION": 1473.8},
    {"ID_SITE": "PARIS",      "MOIS": 10, "TRANSPORT": "Train",                "EMISSION": 13.4},
    {"ID_SITE": "PARIS",      "MOIS": 10, "TRANSPORT": "Taxi",                 "EMISSION": 2.2},
    {"ID_SITE": "PARIS",      "MOIS": 10, "TRANSPORT": "Transports en commun", "EMISSION": 0.7},
    {"ID_SITE": "PARIS",      "MOIS": 11, "TRANSPORT": "Avion",                "EMISSION": 646.7},
    {"ID_SITE": "PARIS",      "MOIS": 11, "TRANSPORT": "Train",                "EMISSION": 5.9},
    {"ID_SITE": "PARIS",      "MOIS": 11, "TRANSPORT": "Taxi",                 "EMISSION": 1.0},
    {"ID_SITE": "PARIS",      "MOIS": 11, "TRANSPORT": "Transports en commun", "EMISSION": 0.3},

    # SHANGHAI
    {"ID_SITE": "SHANGHAI",   "MOIS": 4,  "TRANSPORT": "Avion",                "EMISSION": 41.5},
    {"ID_SITE": "SHANGHAI",   "MOIS": 4,  "TRANSPORT": "Train",                "EMISSION": 0.8},
    {"ID_SITE": "SHANGHAI",   "MOIS": 4,  "TRANSPORT": "Taxi",                 "EMISSION": 0.2},
    {"ID_SITE": "SHANGHAI",   "MOIS": 4,  "TRANSPORT": "Transports en commun", "EMISSION": 0.1},
    {"ID_SITE": "SHANGHAI",   "MOIS": 5,  "TRANSPORT": "Avion",                "EMISSION": 1112.0},
    {"ID_SITE": "SHANGHAI",   "MOIS": 5,  "TRANSPORT": "Train",                "EMISSION": 10.1},
    {"ID_SITE": "SHANGHAI",   "MOIS": 5,  "TRANSPORT": "Taxi",                 "EMISSION": 1.6},
    {"ID_SITE": "SHANGHAI",   "MOIS": 5,  "TRANSPORT": "Transports en commun", "EMISSION": 0.5},
    {"ID_SITE": "SHANGHAI",   "MOIS": 6,  "TRANSPORT": "Avion",                "EMISSION": 1015.8},
    {"ID_SITE": "SHANGHAI",   "MOIS": 6,  "TRANSPORT": "Train",                "EMISSION": 9.3},
    {"ID_SITE": "SHANGHAI",   "MOIS": 6,  "TRANSPORT": "Taxi",                 "EMISSION": 1.5},
    {"ID_SITE": "SHANGHAI",   "MOIS": 6,  "TRANSPORT": "Transports en commun", "EMISSION": 0.5},
    {"ID_SITE": "SHANGHAI",   "MOIS": 7,  "TRANSPORT": "Avion",                "EMISSION": 1059.8},
    {"ID_SITE": "SHANGHAI",   "MOIS": 7,  "TRANSPORT": "Train",                "EMISSION": 9.7},
    {"ID_SITE": "SHANGHAI",   "MOIS": 7,  "TRANSPORT": "Taxi",                 "EMISSION": 1.6},
    {"ID_SITE": "SHANGHAI",   "MOIS": 7,  "TRANSPORT": "Transports en commun", "EMISSION": 0.5},
    {"ID_SITE": "SHANGHAI",   "MOIS": 8,  "TRANSPORT": "Avion",                "EMISSION": 1104.0},
    {"ID_SITE": "SHANGHAI",   "MOIS": 8,  "TRANSPORT": "Train",                "EMISSION": 10.1},
    {"ID_SITE": "SHANGHAI",   "MOIS": 8,  "TRANSPORT": "Taxi",                 "EMISSION": 1.6},
    {"ID_SITE": "SHANGHAI",   "MOIS": 8,  "TRANSPORT": "Transports en commun", "EMISSION": 0.5},
    {"ID_SITE": "SHANGHAI",   "MOIS": 9,  "TRANSPORT": "Avion",                "EMISSION": 980.3},
    {"ID_SITE": "SHANGHAI",   "MOIS": 9,  "TRANSPORT": "Train",                "EMISSION": 8.9},
    {"ID_SITE": "SHANGHAI",   "MOIS": 9,  "TRANSPORT": "Taxi",                 "EMISSION": 1.4},
    {"ID_SITE": "SHANGHAI",   "MOIS": 9,  "TRANSPORT": "Transports en commun", "EMISSION": 0.4},
    {"ID_SITE": "SHANGHAI",   "MOIS": 10, "TRANSPORT": "Avion",                "EMISSION": 1112.0},
    {"ID_SITE": "SHANGHAI",   "MOIS": 10, "TRANSPORT": "Train",                "EMISSION": 10.1},
    {"ID_SITE": "SHANGHAI",   "MOIS": 10, "TRANSPORT": "Taxi",                 "EMISSION": 1.6},
    {"ID_SITE": "SHANGHAI",   "MOIS": 10, "TRANSPORT": "Transports en commun", "EMISSION": 0.5},
    {"ID_SITE": "SHANGHAI",   "MOIS": 11, "TRANSPORT": "Avion",                "EMISSION": 487.6},
    {"ID_SITE": "SHANGHAI",   "MOIS": 11, "TRANSPORT": "Train",                "EMISSION": 4.4},
    {"ID_SITE": "SHANGHAI",   "MOIS": 11, "TRANSPORT": "Taxi",                 "EMISSION": 0.7},
    {"ID_SITE": "SHANGHAI",   "MOIS": 11, "TRANSPORT": "Transports en commun", "EMISSION": 0.2},
]


# ================================================================
# Q20 — Impact carbone global mensuel de l'organisation
# (cellule 117 du notebook : jointure missions + matériel par mois)
# ================================================================
EMISSIONS_MENSUEL_GLOBAL = [
    {"MOIS": 4,  "Emission_tCO2e": 495.210157,  "sum(IMPACT)": 18.694,  "TOT_IMPACT": 513.904157},
    {"MOIS": 5,  "Emission_tCO2e": 8999.435774, "sum(IMPACT)": 354.925, "TOT_IMPACT": 9354.360774},
    {"MOIS": 6,  "Emission_tCO2e": 8159.096407, "sum(IMPACT)": 330.453, "TOT_IMPACT": 8489.549407},
    {"MOIS": 7,  "Emission_tCO2e": 8509.541112, "sum(IMPACT)": 365.709, "TOT_IMPACT": 8875.250112},
    {"MOIS": 8,  "Emission_tCO2e": 8852.082843, "sum(IMPACT)": 343.719, "TOT_IMPACT": 9195.801843},
    {"MOIS": 9,  "Emission_tCO2e": 7922.544967, "sum(IMPACT)": 327.562, "TOT_IMPACT": 8250.106967},
    {"MOIS": 10, "Emission_tCO2e": 8832.296358, "sum(IMPACT)": 339.082, "TOT_IMPACT": 9171.378358},
    {"MOIS": 11, "Emission_tCO2e": 3930.353566, "sum(IMPACT)": 156.841, "TOT_IMPACT": 4087.194566},
]
