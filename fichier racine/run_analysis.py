"""
Script principal : exécute le nettoyage + EDA + RFM en une seule commande.
Usage : python run_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # mode non-interactif (pas besoin d'affichage)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (12, 5)

# ── Chemins ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent
DATA_RAW   = ROOT / "data.csv"
DATA_DIR   = ROOT / "data"
REPORT_DIR = ROOT / "reports"
DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# ── 1. Chargement ──────────────────────────────────────────────────────────────
print("[1/6] Chargement des données brutes...")
df = pd.read_csv(DATA_RAW, encoding="ISO-8859-1", dtype={"CustomerID": str})
print(f"     {len(df):,} lignes chargées.")

# ── 2. Nettoyage ───────────────────────────────────────────────────────────────
print("[2/6] Nettoyage...")
df = df.dropna(subset=["CustomerID"])
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
df = df[df["Quantity"] > 0]
df = df[df["UnitPrice"] > 0]
df["InvoiceDate"]  = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M")
df["TotalAmount"]  = (df["Quantity"] * df["UnitPrice"]).round(2)
df["Year"]         = df["InvoiceDate"].dt.year
df["Month"]        = df["InvoiceDate"].dt.month
df["MonthName"]    = df["InvoiceDate"].dt.strftime("%b")
df["DayName"]      = df["InvoiceDate"].dt.day_name()
df["Hour"]         = df["InvoiceDate"].dt.hour
df["CustomerID"]   = df["CustomerID"].astype(str).str.strip().str.replace(".0", "", regex=False)
df.to_csv(DATA_DIR / "sales_clean.csv", index=False)
print(f"     {len(df):,} lignes valides → data/sales_clean.csv")

# ── 3. KPIs ────────────────────────────────────────────────────────────────────
revenue_total  = df["TotalAmount"].sum()
nb_commandes   = df["InvoiceNo"].nunique()
nb_clients     = df["CustomerID"].nunique()
panier_moyen   = revenue_total / nb_commandes
nb_produits    = df["StockCode"].nunique()

print("\n" + "="*50)
print(f"  CA Total          : £{revenue_total:>12,.2f}")
print(f"  Commandes         : {nb_commandes:>12,}")
print(f"  Clients           : {nb_clients:>12,}")
print(f"  Panier moyen      : £{panier_moyen:>12,.2f}")
print(f"  Produits distincts: {nb_produits:>12,}")
print("="*50 + "\n")

# ── 4. Visualisations ──────────────────────────────────────────────────────────
print("[3/6] Génération des graphiques...")

# Évolution mensuelle
monthly = (
    df.groupby(["Year", "Month"])["TotalAmount"].sum()
    .reset_index().sort_values(["Year", "Month"])
)
monthly["Period"] = monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)
fig, ax = plt.subplots()
ax.fill_between(monthly["Period"], monthly["TotalAmount"], alpha=0.3, color="#3498DB")
ax.plot(monthly["Period"], monthly["TotalAmount"], marker="o", linewidth=2, color="#3498DB")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}k"))
ax.set_title("Évolution mensuelle du Chiffre d'Affaires")
ax.set_xlabel("Période"); ax.set_ylabel("CA (£)")
plt.xticks(rotation=45, ha="right"); plt.tight_layout()
plt.savefig(REPORT_DIR / "monthly_revenue.png", dpi=150); plt.close()

# Top 10 produits
top_products = df.groupby("Description")["TotalAmount"].sum().nlargest(10).reset_index().sort_values("TotalAmount")
fig, ax = plt.subplots()
ax.barh(top_products["Description"], top_products["TotalAmount"], color=sns.color_palette("Blues_d", 10))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}k"))
ax.set_title("Top 10 Produits par Chiffre d'Affaires"); ax.set_xlabel("CA (£)")
plt.tight_layout(); plt.savefig(REPORT_DIR / "top10_products.png", dpi=150); plt.close()

# Top 10 clients
top_customers = df.groupby("CustomerID")["TotalAmount"].sum().nlargest(10).reset_index().sort_values("TotalAmount")
fig, ax = plt.subplots()
ax.barh(top_customers["CustomerID"], top_customers["TotalAmount"], color=sns.color_palette("Greens_d", 10))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}k"))
ax.set_title("Top 10 Clients par Chiffre d'Affaires"); ax.set_xlabel("CA (£)")
plt.tight_layout(); plt.savefig(REPORT_DIR / "top10_customers.png", dpi=150); plt.close()

# Top 10 pays
top_countries = df.groupby("Country")["TotalAmount"].sum().nlargest(10).reset_index().sort_values("TotalAmount")
fig, ax = plt.subplots()
ax.barh(top_countries["Country"], top_countries["TotalAmount"], color=sns.color_palette("OrRd_d", 10))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}k"))
ax.set_title("Top 10 Pays par Chiffre d'Affaires"); ax.set_xlabel("CA (£)")
plt.tight_layout(); plt.savefig(REPORT_DIR / "top10_countries.png", dpi=150); plt.close()

# Heatmap jour × heure
DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"]
pivot = (
    df.groupby(["DayName", "Hour"])["TotalAmount"].sum()
    .reset_index().pivot(index="DayName", columns="Hour", values="TotalAmount")
    .reindex([d for d in DAYS_ORDER if d in df["DayName"].unique()]).fillna(0)
)
fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(pivot, cmap="YlOrRd", linewidths=0.3, ax=ax)
ax.set_title("Heatmap : CA par Jour et Heure"); ax.set_xlabel("Heure"); ax.set_ylabel("Jour")
plt.tight_layout(); plt.savefig(REPORT_DIR / "heatmap_day_hour.png", dpi=150); plt.close()

print("     5 graphiques sauvegardés dans reports/")

# ── 5. Analyse RFM ─────────────────────────────────────────────────────────────
print("[4/6] Calcul RFM...")
snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)
rfm = (
    df.groupby("CustomerID")
    .agg(Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
         Frequency=("InvoiceNo", "nunique"),
         Monetary=("TotalAmount", "sum"))
    .reset_index()
)
rfm["Monetary"] = rfm["Monetary"].round(2)
rfm["R_Score"] = pd.qcut(rfm["Recency"],   5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"],  5, labels=[1, 2, 3, 4, 5]).astype(int)

def segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 4 and f >= 4 and m >= 4:   return "Champions"
    elif r >= 3 and f >= 3:             return "Clients fidèles"
    elif r >= 3 and f <= 2:             return "Clients potentiels"
    elif r <= 2 and f >= 3:             return "Clients à risque"
    else:                               return "Clients perdus"

rfm["Segment"] = rfm.apply(segment, axis=1)
rfm.to_csv(DATA_DIR / "rfm_segments.csv", index=False)
print(f"     {len(rfm):,} clients segmentés → data/rfm_segments.csv")
print(rfm["Segment"].value_counts().to_string())

# ── 6. Graphiques RFM ─────────────────────────────────────────────────────────
print("[5/6] Graphiques RFM...")
COLORS = {
    "Champions":          "#2ECC71",
    "Clients fidèles":    "#3498DB",
    "Clients potentiels": "#F39C12",
    "Clients à risque":   "#E67E22",
    "Clients perdus":     "#E74C3C",
}

# Distributions
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, col, color in zip(axes, ["Recency", "Frequency", "Monetary"],
                           ["#E74C3C", "#2ECC71", "#3498DB"]):
    ax.hist(rfm[col], bins=40, color=color, edgecolor="white")
    ax.set_title(f"Distribution : {col}")
plt.tight_layout(); plt.savefig(REPORT_DIR / "rfm_distributions.png", dpi=150); plt.close()

# Camembert
seg_counts = rfm["Segment"].value_counts()
fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(seg_counts, labels=seg_counts.index, autopct="%1.1f%%",
       colors=[COLORS.get(s, "grey") for s in seg_counts.index], startangle=140)
ax.set_title("Segmentation RFM des Clients")
plt.tight_layout(); plt.savefig(REPORT_DIR / "rfm_segments_pie.png", dpi=150); plt.close()

# Scatter
fig, ax = plt.subplots(figsize=(11, 7))
for seg, grp in rfm.groupby("Segment"):
    ax.scatter(grp["Recency"], grp["Monetary"], label=seg,
               alpha=0.5, s=25, color=COLORS.get(seg, "grey"))
ax.set_xlabel("Recency (jours)"); ax.set_ylabel("Monetary (£)")
ax.set_title("Segmentation RFM : Recency vs Monetary"); ax.legend(title="Segment")
plt.tight_layout(); plt.savefig(REPORT_DIR / "rfm_scatter.png", dpi=150); plt.close()

print("     3 graphiques RFM sauvegardés.")

# ── 7. Résumé ─────────────────────────────────────────────────────────────────
print("\n[6/6] Résumé final")
print("="*50)
best_month = monthly.loc[monthly["TotalAmount"].idxmax(), "Period"]
top_country = df.groupby("Country")["TotalAmount"].sum().idxmax()
print(f"  Meilleur mois   : {best_month}")
print(f"  Meilleur pays   : {top_country}")
print(f"  Fichiers générés:")
for f in sorted((DATA_DIR).glob("*.csv")) + sorted(REPORT_DIR.glob("*.png")):
    print(f"    ✓ {f.relative_to(ROOT)}")
print("\nAnalyse terminée avec succès.")
