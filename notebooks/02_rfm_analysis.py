# ============================================================
# Projet BI : Analyse des Ventes E-commerce
# Notebook 2 : Analyse RFM approfondie & Recommandations
# ============================================================

# %% [markdown]
# # 1. Chargement des données RFM

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

rfm = pd.read_csv("../data/rfm_segments.csv")
print(f"Clients analysés : {len(rfm):,}")
rfm.head()

# %% [markdown]
# # 2. Statistiques par segment

seg_stats = (
    rfm.groupby("Segment")
    .agg(
        Nb_clients   =("CustomerID", "count"),
        Recency_moy  =("Recency",    "mean"),
        Frequency_moy=("Frequency",  "mean"),
        Monetary_moy =("Monetary",   "mean"),
        CA_total     =("Monetary",   "sum"),
    )
    .round(1)
    .reset_index()
)
seg_stats["Pct_clients"] = (seg_stats["Nb_clients"] / seg_stats["Nb_clients"].sum() * 100).round(1)
seg_stats["Pct_CA"]      = (seg_stats["CA_total"] / seg_stats["CA_total"].sum() * 100).round(1)
seg_stats = seg_stats.sort_values("CA_total", ascending=False)
print(seg_stats.to_string(index=False))

# %% [markdown]
# # 3. Scatter RFM : Recency vs Monetary

COLORS = {
    "Champions":          "#2ECC71",
    "Clients fidèles":    "#3498DB",
    "Clients potentiels": "#F39C12",
    "Clients à risque":   "#E67E22",
    "Clients perdus":     "#E74C3C",
}

fig, ax = plt.subplots(figsize=(11, 7))
for seg, grp in rfm.groupby("Segment"):
    ax.scatter(grp["Recency"], grp["Monetary"],
               label=seg, alpha=0.5, s=30, color=COLORS.get(seg, "grey"))
ax.set_xlabel("Recency (jours depuis dernier achat)")
ax.set_ylabel("Monetary (£ dépensés)")
ax.set_title("Segmentation RFM : Recency vs Monetary")
ax.legend(title="Segment")
plt.tight_layout()
plt.savefig("../reports/rfm_scatter.png", dpi=150)
plt.show()

# %% [markdown]
# # 4. Treemap des segments (taille = CA total)

try:
    import squarify
    fig, ax = plt.subplots(figsize=(11, 6))
    sizes  = seg_stats["CA_total"].values
    labels = [f"{r['Segment']}\n{r['Nb_clients']} clients\n£{r['CA_total']:,.0f}" for _, r in seg_stats.iterrows()]
    colors = [COLORS.get(s, "#95A5A6") for s in seg_stats["Segment"]]
    squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.85, ax=ax)
    ax.set_title("Treemap : Poids des segments par CA")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("../reports/rfm_treemap.png", dpi=150)
    plt.show()
except ImportError:
    print("squarify non installé — pip install squarify")

# %% [markdown]
# # 5. Recommandations marketing par segment

recommendations = {
    "Champions": [
        "Programme VIP exclusif (accès anticipé aux nouveautés).",
        "Récompenses de fidélité : cashback ou points doublés.",
        "Solliciter des avis / ambassadeurs de marque.",
    ],
    "Clients fidèles": [
        "Offres personnalisées basées sur l'historique d'achats.",
        "Ventes croisées (cross-sell) et montées en gamme (up-sell).",
        "Newsletter premium avec avant-premières.",
    ],
    "Clients potentiels": [
        "Emails de ré-engagement avec code promo limité dans le temps.",
        "Recommandations produits basées sur le premier achat.",
        "Programme de parrainage pour augmenter la fréquence.",
    ],
    "Clients à risque": [
        "Campagne win-back : « Vous nous manquez ! » avec réduction 20 %.",
        "Sondage de satisfaction pour comprendre le désengagement.",
        "Offre flash valable 48h.",
    ],
    "Clients perdus": [
        "Email de dernière chance avec offre exceptionnelle (-30 %).",
        "Si pas de réponse, archiver et réallouer le budget marketing.",
        "Analyser les raisons de la perte (prix, UX, concurrence).",
    ],
}

print("\n" + "=" * 60)
print("  RECOMMANDATIONS MARKETING PAR SEGMENT RFM")
print("=" * 60)
for seg, recs in recommendations.items():
    print(f"\n▶  {seg.upper()}")
    for r in recs:
        print(f"   • {r}")

# %% [markdown]
# # 6. Export rapport CSV

output = rfm.merge(
    seg_stats[["Segment", "CA_total", "Pct_CA"]],
    on="Segment", how="left"
)
output.to_csv("../data/rfm_full_report.csv", index=False)
print("\nRapport complet exporté : ../data/rfm_full_report.csv")
