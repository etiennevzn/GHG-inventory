# Dashboard BGES — NF26

Dashboard Streamlit pour la visualisation du Bilan de Gaz à Effet de Serre (BGES) d'une organisation internationale, basé sur le notebook `ETL.ipynb`.

## 🚀 Lancement

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement de l'application
streamlit run app.py
```

L'app s'ouvrira automatiquement dans le navigateur (par défaut sur `http://localhost:8501`).

## 📂 Structure

```
dashboard_bges/
├── app.py              # Application Streamlit principale
├── data.py             # Données pré-calculées (réponses aux 20 questions)
├── requirements.txt    # Dépendances Python
└── README.md
```

## 🗺️ Navigation

Le dashboard est organisé en **6 menus** dans la sidebar :

| Menu | Questions couvertes | Contenu |
|------|---------------------|---------|
| 🏠 **Accueil** | — | KPIs principaux, vue d'ensemble |
| 👥 **Effectifs** | Q1, Q2, Q3 | Répartition RH par fonction |
| 💻 **Matériel informatique** | Q4, Q5, Q6, Q7 | Achats et impacts du matériel |
| ✈️ **Missions & déplacements** | Q8, Q9, Q12, Q13, Q16, Q18 | Analyses de déplacements |
| 🌍 **Analyses transverses** | Q10, Q11, Q14, Q15, Q17 | Comparaisons par secteur/site |
| 📊 **Visualisations globales** | Q19, Q20 | Vues mensuelles globales |

## 🎨 Palette de couleurs

| | Couleur | Hex |
|--|---------|-----|
| 🟦 | Bleu nuit | `#054A8D` |
| 🟪 | Bleu violet | `#5767D6` |
| 💜 | Lavande | `#9C91E0` |
| 🟣 | Mauve | `#CD9BE4` |
| 🌸 | Orchidée | `#EB9CEF` |
| 💗 | Rose pastel | `#FF9EEF` |

## 📝 Notes

- Toutes les données sont **hardcodées** dans `data.py` à partir des outputs du notebook (option dashboard "vitrine").
- Pour mettre à jour les valeurs, ré-exécuter le notebook puis modifier les constantes dans `data.py`.
- Les valeurs Q19 (impact mensuel par transport × site) sont des estimations cohérentes avec les totaux observés. Pour des valeurs exactes, exporter le DataFrame `emissions_monthly` du notebook (cellule 113) au format CSV et le charger dans `data.py`.
