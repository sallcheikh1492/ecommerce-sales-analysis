# ============================================================
# Projet BI : Analyse des Ventes E-commerce
# Notebook 1 : Nettoyage des données & Analyse Exploratoire
# ============================================================

# %% [markdown]
# # 1. Importation des librairies

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (12, 5)

DATA_RAW  = Path("../data.csv")
DATA_CLEAN = Path("../data/sales_clean.csv")
DATA_RFM   = Path("../data/rfm_segments.csv")

# %% [markdown]
# # 2. Chargement des données brutes

df_raw = pd.read_csv(DATA_RAW, encoding="ISO-8859-1", dtype={"CustomerID": str})
print(f"Shape brut : {df_raw.shape}")
print(df_raw.dtypes)
df_raw.head()

# %% [markdown]
# ## 2.1 Aperçu statistique

df_raw.describe(include="all")

# %% [markdown]
# ## 2.2 Valeurs manquantes

missing = df_raw.isnull().sum().rename("missing").to_frame()
missing["pct"] = (missing["missing"] / len(df_raw) * 100).round(2)
print(missing[missing["missing"] > 0])

# %% [markdown]
# # 3. Nettoyage des données

df = df_raw.copy()

# 3.1 Supprimer les lignes sans CustomerID
df = df.dropna(subset=["CustomerID"])

# 3.2 Exclure les annulations (InvoiceNo commençant par C) et retours (Quantity < 0)
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
df = df[df["Quantity"] > 0]

# 3.3 Exclure les UnitPrice nuls ou négatifs
df = df[df["UnitPrice"] > 0]

# 3.4 Convertir InvoiceDate
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M")

# 3.5 Créer TotalAmount
df["TotalAmount"] = (df["Quantity"] * df["UnitPrice"]).round(2)

# 3.6 Colonnes temporelles utiles
df["Year"]    = df["InvoiceDate"].dt.year
df["Month"]   = df["InvoiceDate"].dt.month
df["MonthName"] = df["InvoiceDate"].dt.strftime("%b")
df["Week"]    = df["InvoiceDate"].dt.isocalendar().week.astype(int)
df["DayName"] = df["InvoiceDate"].dt.day_name()
df["Hour"]    = df["InvoiceDate"].dt.hour

# 3.7 Nettoyage CustomerID
df["CustomerID"] = df["CustomerID"].astype(str).str.strip().str.replace(".0", "", regex=False)

print(f"\nShape après nettoyage : {df.shape}")
print(f"Période : {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}")
df.head()

# %% [markdown]
# # 4. Export des données nettoyées

df.to_csv(DATA_CLEAN, index=False)
print(f"Fichier exporté : {DATA_CLEAN}")

# %% [markdown]
# # 5. Analyse Exploratoire (EDA)

# %% [markdown]
# ## 5.1 KPIs Globaux

revenue_total   = df["TotalAmount"].sum()
nb_commandes    = df["InvoiceNo"].nunique()
nb_clients      = df["CustomerID"].nunique()
panier_moyen    = revenue_total / nb_commandes
nb_produits     = df["StockCode"].nunique()

print("=" * 45)
print(f"  Chiffre d'affaires total : £{revenue_total:,.2f}")
print(f"  Nombre de commandes      : {nb_commandes:,}")
print(f"  Nombre de clients        : {nb_clients:,}")
print(f"  Panier moyen             : £{panier_moyen:,.2f}")
print(f"  Produits distincts       : {nb_produits:,}")
print("=" * 45)

# %% [markdown]
# ## 5.2 Évolution mensuelle du CA

monthly = (
    df.groupby(["Year", "Month", "MonthName"])["TotalAmount"]
    .sum()
    .reset_index()
    .sort_values(["Year", "Month"])
)
monthly["Period"] = monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)

fig, ax = plt.subplots()
ax.fill_between(monthly["Period"], monthly["TotalAmount"], alpha=0.3)
ax.plot(monthly["Period"], monthly["TotalAmount"], marker="o", linewidth=2)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}k"))
ax.set_xlabel("Période")
ax.set_ylabel("CA (£)")
ax.set_title("Évolution mensuelle du Chiffre d'Affaires")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("../reports/monthly_revenue.png", dpi=150)
plt.show()

# %% [markdown]
# ## 5.3 Top 10 produits par revenu

top_products = (
    df.groupby("Description")["TotalAmount"]
    .sum()
    .nlargest(10)
    .reset_index()
    .sort_values("TotalAmount")
)

fig, ax = plt.subplots()
bars = ax.barh(top_products["Description"], top_products["TotalAmount"], color=sns.color_palette("Blues_d", 10))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}k"))
ax.set_title("Top 10 Produits par Chiffre d'Affaires")
ax.set_xlabel("CA (£)")
for bar in bars:
    ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
            f"£{bar.get_width():,.0f}", va="center", fontsize=8)
plt.tight_layout()
plt.savefig("../reports/top10_products.png", dpi=150)
plt.show()

# %% [markdown]
# ## 5.4 Top 10 clients par revenu

top_customers = (
    df.groupby("CustomerID")["TotalAmount"]
    .sum()
    .nlargest(10)
    .reset_index()
    .sort_values("TotalAmount")
)

fig, ax = plt.subplots()
ax.barh(top_customers["CustomerID"], top_customers["TotalAmount"],
        color=sns.color_palette("Greens_d", 10))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}k"))
ax.set_title("Top 10 Clients par Chiffre d'Affaires")
ax.set_xlabel("CA (£)")
plt.tight_layout()
plt.savefig("../reports/top10_customers.png", dpi=150)
plt.show()

# %% [markdown]
# ## 5.5 Répartition des ventes par pays (Top 10)

top_countries = (
    df.groupby("Country")["TotalAmount"]
    .sum()
    .nlargest(10)
    .reset_index()
    .sort_values("TotalAmount")
)

fig, ax = plt.subplots()
colors = sns.color_palette("OrRd_d", 10)
ax.barh(top_countries["Country"], top_countries["TotalAmount"], color=colors)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}k"))
ax.set_title("Top 10 Pays par Chiffre d'Affaires")
ax.set_xlabel("CA (£)")
plt.tight_layout()
plt.savefig("../reports/top10_countries.png", dpi=150)
plt.show()

# %% [markdown]
# ## 5.6 Heatmap ventes par jour et heure

pivot_day_hour = (
    df.groupby(["DayName", "Hour"])["TotalAmount"]
    .sum()
    .reset_index()
    .pivot(index="DayName", columns="Hour", values="TotalAmount")
    .reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"])
    .fillna(0)
)

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(pivot_day_hour, cmap="YlOrRd", fmt=".0f", linewidths=0.3, ax=ax)
ax.set_title("Heatmap : CA par Jour et Heure")
ax.set_xlabel("Heure")
ax.set_ylabel("Jour")
plt.tight_layout()
plt.savefig("../reports/heatmap_day_hour.png", dpi=150)
plt.show()

# %% [markdown]
# # 6. Analyse RFM

snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = (
    df.groupby("CustomerID")
    .agg(
        Recency   =("InvoiceDate",  lambda x: (snapshot_date - x.max()).days),
        Frequency =("InvoiceNo",    "nunique"),
        Monetary  =("TotalAmount",  "sum"),
    )
    .reset_index()
)
rfm["Monetary"] = rfm["Monetary"].round(2)

# Scores RFM (quintiles, 5 = meilleur)
rfm["R_Score"] = pd.qcut(rfm["Recency"],   5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"],  5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

def segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Clients fidèles"
    elif r >= 3 and f <= 2:
        return "Clients potentiels"
    elif r <= 2 and f >= 3:
        return "Clients à risque"
    else:
        return "Clients perdus"

rfm["Segment"] = rfm.apply(segment, axis=1)

print(rfm["Segment"].value_counts())
rfm.head(10)

# %% [markdown]
# ## 6.1 Visualisation RFM

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, col, color in zip(axes, ["Recency", "Frequency", "Monetary"], ["#E74C3C", "#2ECC71", "#3498DB"]):
    ax.hist(rfm[col], bins=40, color=color, edgecolor="white")
    ax.set_title(f"Distribution : {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Clients")
plt.tight_layout()
plt.savefig("../reports/rfm_distributions.png", dpi=150)
plt.show()

# Camembert segments
seg_counts = rfm["Segment"].value_counts()
fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    seg_counts, labels=seg_counts.index, autopct="%1.1f%%",
    colors=sns.color_palette("Set2"), startangle=140)
ax.set_title("Segmentation RFM des Clients")
plt.tight_layout()
plt.savefig("../reports/rfm_segments_pie.png", dpi=150)
plt.show()

# %% [markdown]
# ## 6.2 Export RFM

rfm.to_csv(DATA_RFM, index=False)
print(f"RFM exporté : {DATA_RFM}")

# %% [markdown]
# # 7. Résumé des insights

insights = {
    "CA Total (£)":       f"{revenue_total:,.2f}",
    "Commandes":          f"{nb_commandes:,}",
    "Clients":            f"{nb_clients:,}",
    "Panier moyen (£)":   f"{panier_moyen:,.2f}",
    "Produits":           f"{nb_produits:,}",
    "Meilleur mois":      monthly.loc[monthly["TotalAmount"].idxmax(), "Period"],
    "Top pays":           df.groupby("Country")["TotalAmount"].sum().idxmax(),
}
for k, v in insights.items():
    print(f"  {k:<22}: {v}")
