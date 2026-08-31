# Analyse des Ventes E-commerce — Projet BI Complet

## 🔗 Liens
[![Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen)](https://sallcheikh1492.github.io/ecommerce-sales-analysis/reports/dashboard.html)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/sallcheikh1492/ecommerce-sales-analysis)

👉 **[Dashboard Interactif en ligne](https://sallcheikh1492.github.io/ecommerce-sales-analysis/reports/dashboard.html)**

> Projet Business Intelligence démontrant des compétences en **SQL**, **Python**, **Analyse RFM** et **Power BI**,
> construit sur le dataset UCI E-commerce (Dec 2010 – Dec 2011).

---

## Structure du projet

```
bi1/
├── data.csv                        ← Dataset brut (source)
├── data/
│   ├── sales_clean.csv             ← Données nettoyées (généré par notebook 1)
│   ├── rfm_segments.csv            ← Segmentation RFM (généré par notebook 1)
│   └── rfm_full_report.csv         ← Rapport RFM complet (généré par notebook 2)
├── notebooks/
│   ├── 01_data_cleaning_eda.py     ← Nettoyage, EDA, visualisations
│   └── 02_rfm_analysis.py          ← Analyse RFM approfondie & recommandations
├── sql/
│   ├── 01_create_table.sql         ← Création de la table sales
│   ├── 02_import_data.sql          ← Import des données nettoyées
│   └── 03_analysis_queries.sql     ← Requêtes d'analyse business complètes
├── powerbi/
│   ├── GUIDE_POWERBI.md            ← Guide de construction du dashboard
│   └── ecommerce_dashboard.pbix    ← Dashboard Power BI (à générer)
├── reports/
│   ├── RAPPORT_INSIGHTS.md         ← Rapport d'analyse et recommandations
│   ├── monthly_revenue.png         ← Graphique évolution mensuelle CA
│   ├── top10_products.png          ← Top 10 produits
│   ├── top10_customers.png         ← Top 10 clients
│   ├── top10_countries.png         ← Top 10 pays
│   ├── heatmap_day_hour.png        ← Heatmap jour × heure
│   ├── rfm_distributions.png       ← Distributions RFM
│   ├── rfm_segments_pie.png        ← Camembert segments
│   └── rfm_scatter.png             ← Scatter Recency vs Monetary
├── requirements.txt                ← Dépendances Python
└── README.md
```

---

## Technologies utilisées

| Outil | Usage |
|---|---|
| **Python 3.10+** | Nettoyage, EDA, analyse RFM, visualisations |
| **Pandas / NumPy** | Manipulation des données |
| **Matplotlib / Seaborn** | Visualisations statiques |
| **PostgreSQL** | Stockage et analyse SQL |
| **Power BI Desktop** | Dashboard interactif |
| **Jupyter Notebook** | Environnement d'exploration |

---

## Installation & Exécution

### Prérequis

```bash
pip install -r requirements.txt
```

### Étape 1 : Nettoyage et EDA

```bash
# Depuis le dossier bi1/
jupyter notebook notebooks/01_data_cleaning_eda.py
# ou directement :
python notebooks/01_data_cleaning_eda.py
```

**Sorties générées :**
- `data/sales_clean.csv`
- `data/rfm_segments.csv`
- Graphiques dans `reports/`

### Étape 2 : Analyse RFM

```bash
python notebooks/02_rfm_analysis.py
```

**Sorties générées :**
- `data/rfm_full_report.csv`
- `reports/rfm_scatter.png`
- `reports/rfm_treemap.png`

### Étape 3 : Base SQL (PostgreSQL)

```bash
# 1. Créer la base de données
psql -U postgres -c "CREATE DATABASE ecommerce_bi;"

# 2. Créer la table
psql -U postgres -d ecommerce_bi -f sql/01_create_table.sql

# 3. Importer les données
# Modifier le chemin dans 02_import_data.sql, puis :
psql -U postgres -d ecommerce_bi -f sql/02_import_data.sql

# 4. Lancer les analyses
psql -U postgres -d ecommerce_bi -f sql/03_analysis_queries.sql
```

### Étape 4 : Dashboard Power BI

Suivre le guide détaillé dans [`powerbi/GUIDE_POWERBI.md`](powerbi/GUIDE_POWERBI.md).

---

## KPIs & Résultats clés

| KPI | Valeur |
|---|---|
| Chiffre d'affaires total | £8 911 407.90 |
| Nombre de commandes | 18 532 |
| Clients actifs | 4 338 |
| Panier moyen | £480.87 |
| Produits distincts | 3 665 |
| Marché dominant | United Kingdom |
| Pic de ventes | Novembre 2011 |

---

## Segmentation RFM

| Segment | % Clients | % CA | Priorité |
|---|---|---|---|
| Champions | ~15 % | ~45 % | Fidéliser |
| Clients fidèles | ~20 % | ~25 % | Cross-sell |
| Clients potentiels | ~20 % | ~15 % | Ré-engager |
| Clients à risque | ~25 % | ~10 % | Win-back |
| Clients perdus | ~20 % | ~5 % | Abandon ciblé |

---

## Pages du Dashboard Power BI

1. **Vue Générale** — KPIs, évolution mensuelle, carte géographique
2. **Produits & Clients** — Top 10 produits, top 10 clients, heatmap activité
3. **Segmentation RFM** — Répartition, CA par segment, scatter R×M

**Filtres disponibles :** Année · Mois · Pays · Segment client

---

## Recommandations principales

1. **Programme VIP** pour les Champions (15 % des clients, 45 % du CA).
2. **Campagne win-back** pour les Clients à risque (email + coupon -20 %).
3. **Anticiper les stocks** en octobre pour le pic de novembre.
4. **Expansion européenne** : Pays-Bas et EIRE ont le panier moyen le plus élevé.
5. **Automatiser les emails** selon le segment RFM (Brevo, Klaviyo).

---

## Compétences démontrées

- Nettoyage et transformation de données avec **Pandas**
- Analyse exploratoire et visualisations avancées (**Matplotlib**, **Seaborn**)
- Modélisation relationnelle et requêtes analytiques **SQL** (fenêtres, CTE, vues)
- Segmentation **RFM** et scoring client
- Construction de **dashboards interactifs Power BI** avec DAX
- Interprétation business et **recommandations actionnables**

---

## Auteur

**Data Analyst / BI Developer**  
Dataset source : [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail)
