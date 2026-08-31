"""
Dashboard interactif E-commerce — Plotly
Génère un fichier HTML complet et autonome
Usage : python dashboard.py
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Couleurs ────────────────────────────────────────────────────────────────
C = {
    "navy":    "#1B3A6B",
    "blue":    "#3498DB",
    "green":   "#2ECC71",
    "orange":  "#F39C12",
    "red":     "#E74C3C",
    "purple":  "#8E44AD",
    "teal":    "#1ABC9C",
    "light":   "#EBF5FB",
    "gray":    "#7F8C8D",
    "white":   "#FFFFFF",
    "bg":      "#F4F6F7",
}

SEG_COLORS = {
    "Champions":          "#27AE60",
    "Clients fidèles":    "#2980B9",
    "Clients potentiels": "#F39C12",
    "Clients à risque":   "#E67E22",
    "Clients perdus":     "#E74C3C",
}

# ── Chargement des données ──────────────────────────────────────────────────
print("Chargement des données...")
sales = pd.read_csv("data/sales_clean.csv", parse_dates=["InvoiceDate"])
rfm   = pd.read_csv("data/rfm_segments.csv")
print(f"  sales : {len(sales):,} lignes | rfm : {len(rfm):,} clients")

# ── KPIs ────────────────────────────────────────────────────────────────────
ca_total      = sales["TotalAmount"].sum()
nb_commandes  = sales["InvoiceNo"].nunique()
nb_clients    = sales["CustomerID"].nunique()
panier_moyen  = ca_total / nb_commandes
clients_multi = sales.groupby("CustomerID")["InvoiceNo"].nunique()
taux_reachat  = (clients_multi >= 2).sum() / nb_clients * 100

# ── Données agrégées ────────────────────────────────────────────────────────
monthly = (
    sales.groupby(["Year","Month"])["TotalAmount"].sum()
    .reset_index().sort_values(["Year","Month"])
)
monthly["Period"] = monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)

top_products = (
    sales.groupby("Description")["TotalAmount"].sum()
    .nlargest(10).reset_index().sort_values("TotalAmount")
)

top_customers = (
    sales.groupby("CustomerID")["TotalAmount"].sum()
    .nlargest(10).reset_index().sort_values("TotalAmount")
)

by_country = (
    sales.groupby("Country")["TotalAmount"].sum()
    .nlargest(15).reset_index().sort_values("TotalAmount")
)

DAYS_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Sunday"]
heatmap_data = (
    sales.groupby(["DayName","Hour"])["TotalAmount"].sum()
    .reset_index()
    .pivot(index="DayName", columns="Hour", values="TotalAmount")
    .reindex([d for d in DAYS_ORDER if d in sales["DayName"].unique()])
    .fillna(0)
)

seg_counts = rfm["Segment"].value_counts().reset_index()
seg_counts.columns = ["Segment","Count"]
seg_ca = rfm.groupby("Segment")["Monetary"].sum().reset_index()
seg_ca.columns = ["Segment","CA"]

DAY_FR = {
    "Monday":"Lundi","Tuesday":"Mardi","Wednesday":"Mercredi",
    "Thursday":"Jeudi","Friday":"Vendredi","Sunday":"Dimanche"
}
heatmap_data.index = [DAY_FR.get(d,d) for d in heatmap_data.index]

# ════════════════════════════════════════════════════════════════════════════
# CONSTRUCTION DU DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
print("Construction du dashboard...")

# ── En-tête HTML + CSS ──────────────────────────────────────────────────────
html_header = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard E-commerce Sales Analysis</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }}
  body {{ background:{C['bg']}; color:#2C3E50; }}

  /* ── Bandeau titre ── */
  .header {{
    background:linear-gradient(135deg,{C['navy']} 0%,#2E5EAA 100%);
    padding:22px 40px; display:flex; justify-content:space-between;
    align-items:center; box-shadow:0 4px 15px rgba(0,0,0,0.2);
  }}
  .header h1 {{ color:{C['white']}; font-size:26px; font-weight:700; letter-spacing:0.5px; }}
  .header p  {{ color:#BDC3C7; font-size:12px; margin-top:4px; }}
  .header .badge {{
    background:rgba(255,255,255,0.15); color:{C['white']};
    padding:6px 14px; border-radius:20px; font-size:12px; font-weight:600;
  }}

  /* ── KPI cards ── */
  .kpi-section {{ display:flex; gap:16px; padding:24px 32px 8px; }}
  .kpi-card {{
    flex:1; background:{C['white']}; border-radius:12px;
    padding:20px 24px; box-shadow:0 2px 12px rgba(0,0,0,0.07);
    border-left:5px solid; transition:transform 0.2s;
  }}
  .kpi-card:hover {{ transform:translateY(-3px); box-shadow:0 6px 20px rgba(0,0,0,0.12); }}
  .kpi-card .value {{ font-size:28px; font-weight:700; line-height:1.2; }}
  .kpi-card .label {{ font-size:12px; color:{C['gray']}; margin-top:6px; text-transform:uppercase; letter-spacing:0.8px; }}
  .kpi-card .delta {{ font-size:11px; margin-top:8px; font-weight:600; }}

  /* ── Sections ── */
  .section-title {{
    font-size:13px; font-weight:700; color:{C['navy']}; text-transform:uppercase;
    letter-spacing:1px; padding:24px 32px 8px; border-left:4px solid {C['blue']};
    margin-left:32px; margin-top:8px;
  }}
  .charts-row {{ display:flex; gap:16px; padding:8px 32px; }}
  .chart-box {{
    background:{C['white']}; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,0.07);
    overflow:hidden; flex:1;
  }}
  .chart-box.full {{ flex:1 1 100%; }}
  .chart-box.half {{ flex:0 0 calc(50% - 8px); }}
  .chart-box.third {{ flex:0 0 calc(33.3% - 11px); }}
  .chart-box.twothird {{ flex:0 0 calc(66.6% - 8px); }}

  /* ── Footer ── */
  .footer {{
    text-align:center; padding:24px; color:{C['gray']}; font-size:12px;
    border-top:1px solid #ECF0F1; margin-top:24px;
  }}

  /* ── Filtres ── */
  .filter-bar {{
    background:{C['white']}; padding:12px 32px; display:flex; gap:20px;
    align-items:center; box-shadow:0 1px 4px rgba(0,0,0,0.06);
  }}
  .filter-bar label {{ font-size:12px; font-weight:600; color:{C['navy']}; }}
  .filter-bar select {{
    border:1px solid #DDE1E7; border-radius:6px; padding:5px 10px;
    font-size:12px; color:#2C3E50; cursor:pointer; background:{C['white']};
  }}
</style>
</head>
<body>
"""

# ── Bandeau header ───────────────────────────────────────────────────────────
html_header += f"""
<div class="header">
  <div>
    <h1>📊 Analyse des Ventes E-commerce</h1>
    <p>Période : Décembre 2010 – Décembre 2011 &nbsp;|&nbsp; Source : UCI E-commerce Dataset</p>
  </div>
  <div class="badge">BI Dashboard · Data Analyst Portfolio</div>
</div>
"""

# ── KPI Cards ────────────────────────────────────────────────────────────────
kpis = [
    {"label":"Chiffre d'Affaires",  "value":f"£{ca_total:,.0f}",     "color":C["blue"],   "delta":"↑ Pic en Nov 2011"},
    {"label":"Commandes",           "value":f"{nb_commandes:,}",      "color":C["green"],  "delta":f"~{nb_commandes/12:.0f} / mois"},
    {"label":"Clients Actifs",      "value":f"{nb_clients:,}",        "color":C["orange"], "delta":"4 338 clients uniques"},
    {"label":"Panier Moyen",        "value":f"£{panier_moyen:,.2f}",  "color":C["purple"], "delta":"Par commande"},
    {"label":"Taux de Réachat",     "value":f"{taux_reachat:.1f}%",   "color":C["teal"],   "delta":"Clients 2+ commandes"},
]

html_kpis = '<div class="kpi-section">'
for k in kpis:
    html_kpis += f"""
    <div class="kpi-card" style="border-left-color:{k['color']}">
      <div class="value" style="color:{k['color']}">{k['value']}</div>
      <div class="label">{k['label']}</div>
      <div class="delta" style="color:{k['color']}">{k['delta']}</div>
    </div>"""
html_kpis += "</div>"

# ════════════════════════════════════════════════════════════════════════════
# GRAPHIQUES PLOTLY
# ════════════════════════════════════════════════════════════════════════════

CHART_CFG = dict(displayModeBar=True, displaylogo=False,
                 modeBarButtonsToRemove=["select2d","lasso2d"])
LAYOUT = dict(
    paper_bgcolor=C["white"], plot_bgcolor=C["white"],
    font=dict(family="Segoe UI", color="#2C3E50"),
    margin=dict(l=40,r=20,t=50,b=40),
    hoverlabel=dict(bgcolor=C["navy"], font_color=C["white"], font_family="Segoe UI")
)

def to_html(fig, h=380):
    fig.update_layout(height=h)
    return fig.to_html(full_html=False, include_plotlyjs=False, config=CHART_CFG)

# ── 1. Évolution mensuelle ───────────────────────────────────────────────────
fig_monthly = go.Figure()
fig_monthly.add_trace(go.Bar(
    x=monthly["Period"], y=monthly["TotalAmount"],
    name="CA Mensuel", marker_color=C["blue"], opacity=0.3,
    hovertemplate="<b>%{x}</b><br>CA : £%{y:,.0f}<extra></extra>"
))
fig_monthly.add_trace(go.Scatter(
    x=monthly["Period"], y=monthly["TotalAmount"],
    mode="lines+markers", name="Tendance",
    line=dict(color=C["navy"], width=3),
    marker=dict(size=8, color=C["navy"], symbol="circle",
                line=dict(color=C["white"], width=2)),
    hovertemplate="<b>%{x}</b><br>CA : £%{y:,.0f}<extra></extra>"
))
fig_monthly.update_layout(**LAYOUT,
    title=dict(text="📈 Évolution Mensuelle du Chiffre d'Affaires", x=0.02, font_size=14),
    xaxis=dict(tickangle=-30, showgrid=False, title=""),
    yaxis=dict(tickformat="£,.0f", gridcolor="#F0F0F0", title=""),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=1, xanchor="right"),
    showlegend=True
)
chart_monthly = to_html(fig_monthly, 380)

# ── 2. Top 10 Produits ───────────────────────────────────────────────────────
fig_prod = go.Figure(go.Bar(
    x=top_products["TotalAmount"],
    y=[d[:40]+"…" if len(d)>40 else d for d in top_products["Description"]],
    orientation="h",
    marker=dict(
        color=top_products["TotalAmount"],
        colorscale=[[0,"#AED6F1"],[1,C["navy"]]],
        showscale=False
    ),
    text=[f"£{v:,.0f}" for v in top_products["TotalAmount"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>CA : £%{x:,.0f}<extra></extra>"
))
fig_prod.update_layout(**LAYOUT,
    title=dict(text="🏆 Top 10 Produits par Chiffre d'Affaires", x=0.02, font_size=14),
    xaxis=dict(tickformat="£,.0f", showgrid=True, gridcolor="#F0F0F0"),
    yaxis=dict(showgrid=False),
    height=420
)
chart_prod = to_html(fig_prod, 420)

# ── 3. Top 10 Clients ────────────────────────────────────────────────────────
fig_cust = go.Figure(go.Bar(
    x=top_customers["TotalAmount"],
    y=top_customers["CustomerID"].astype(str),
    orientation="h",
    marker=dict(
        color=top_customers["TotalAmount"],
        colorscale=[[0,"#A9DFBF"],[1,C["green"]]],
        showscale=False
    ),
    text=[f"£{v:,.0f}" for v in top_customers["TotalAmount"]],
    textposition="outside",
    hovertemplate="<b>Client %{y}</b><br>CA : £%{x:,.0f}<extra></extra>"
))
fig_cust.update_layout(**LAYOUT,
    title=dict(text="👑 Top 10 Clients par Chiffre d'Affaires", x=0.02, font_size=14),
    xaxis=dict(tickformat="£,.0f", showgrid=True, gridcolor="#F0F0F0"),
    yaxis=dict(showgrid=False),
)
chart_cust = to_html(fig_cust, 420)

# ── 4. CA par Pays ───────────────────────────────────────────────────────────
fig_country = go.Figure(go.Bar(
    x=by_country["TotalAmount"],
    y=by_country["Country"],
    orientation="h",
    marker=dict(
        color=by_country["TotalAmount"],
        colorscale=[[0,"#FADBD8"],[1,C["red"]]],
        showscale=False
    ),
    text=[f"£{v/1e3:,.0f}k" for v in by_country["TotalAmount"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>CA : £%{x:,.0f}<extra></extra>"
))
fig_country.update_layout(**LAYOUT,
    title=dict(text="🌍 Top 15 Pays par Chiffre d'Affaires", x=0.02, font_size=14),
    xaxis=dict(tickformat="£,.0f", showgrid=True, gridcolor="#F0F0F0"),
    yaxis=dict(showgrid=False),
)
chart_country = to_html(fig_country, 480)

# ── 5. Heatmap Jour × Heure ──────────────────────────────────────────────────
fig_heat = go.Figure(go.Heatmap(
    z=heatmap_data.values,
    x=[f"{h}h" for h in heatmap_data.columns],
    y=list(heatmap_data.index),
    colorscale=[[0,"#FDFEFE"],[0.5,C["orange"]],[1,C["red"]]],
    hoverongaps=False,
    hovertemplate="<b>%{y} à %{x}</b><br>CA : £%{z:,.0f}<extra></extra>",
    colorbar=dict(title="CA £", thickness=15)
))
fig_heat.update_layout(**LAYOUT,
    title=dict(text="🔥 Heatmap Activité — Jour × Heure (CA £)", x=0.02, font_size=14),
    xaxis=dict(title="Heure"),
    yaxis=dict(title=""),
)
chart_heat = to_html(fig_heat, 350)

# ── 6. Segmentation RFM — Donut ──────────────────────────────────────────────
fig_donut = go.Figure(go.Pie(
    labels=seg_counts["Segment"],
    values=seg_counts["Count"],
    hole=0.55,
    marker=dict(colors=[SEG_COLORS.get(s,"#95A5A6") for s in seg_counts["Segment"]],
                line=dict(color=C["white"], width=3)),
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>%{value} clients (%{percent})<extra></extra>"
))
fig_donut.update_layout(**LAYOUT,
    title=dict(text="🎯 Segmentation RFM des Clients", x=0.02, font_size=14),
    showlegend=False,
    annotations=[dict(text=f"<b>{nb_clients:,}</b><br>clients", x=0.5, y=0.5,
                      font_size=14, showarrow=False)]
)
chart_donut = to_html(fig_donut, 380)

# ── 7. CA par Segment ────────────────────────────────────────────────────────
seg_ca_sorted = seg_ca.sort_values("CA", ascending=False)
fig_seg = go.Figure(go.Bar(
    x=seg_ca_sorted["Segment"],
    y=seg_ca_sorted["CA"],
    marker_color=[SEG_COLORS.get(s,"#95A5A6") for s in seg_ca_sorted["Segment"]],
    text=[f"£{v/1e3:,.0f}k" for v in seg_ca_sorted["CA"]],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>CA : £%{y:,.0f}<extra></extra>"
))
fig_seg.update_layout(**LAYOUT,
    title=dict(text="💰 Contribution CA par Segment RFM", x=0.02, font_size=14),
    xaxis=dict(showgrid=False),
    yaxis=dict(tickformat="£,.0f", gridcolor="#F0F0F0"),
)
chart_seg = to_html(fig_seg, 380)

# ── 8. Scatter RFM ───────────────────────────────────────────────────────────
fig_scatter = px.scatter(
    rfm, x="Recency", y="Monetary",
    color="Segment",
    size="Frequency",
    color_discrete_map=SEG_COLORS,
    hover_data={"CustomerID":True, "Recency":True, "Frequency":True, "Monetary":":.2f"},
    labels={"Recency":"Récence (jours)", "Monetary":"Valeur (£)", "Frequency":"Fréquence"},
    opacity=0.6
)
fig_scatter.update_layout(**LAYOUT,
    title=dict(text="🔵 Carte RFM : Récence vs Valeur (taille = Fréquence)", x=0.02, font_size=14),
    legend=dict(title="Segment", orientation="v"),
)
chart_scatter = to_html(fig_scatter, 450)

# ── 9. Distributions RFM ────────────────────────────────────────────────────
fig_rfm_dist = make_subplots(rows=1, cols=3,
    subplot_titles=["Distribution Récence","Distribution Fréquence","Distribution Valeur"])
for i, (col, color) in enumerate([("Recency",C["red"]),("Frequency",C["green"]),("Monetary",C["blue"])], 1):
    fig_rfm_dist.add_trace(go.Histogram(x=rfm[col], marker_color=color,
                            opacity=0.8, nbinsx=40, name=col,
                            hovertemplate=f"{col}: %{{x}}<br>Clients: %{{y}}<extra></extra>"),
                           row=1, col=i)
fig_rfm_dist.update_layout(**LAYOUT,
    title=dict(text="📊 Distributions RFM", x=0.02, font_size=14),
    showlegend=False, height=320
)
chart_rfm_dist = to_html(fig_rfm_dist, 320)

# ════════════════════════════════════════════════════════════════════════════
# ASSEMBLAGE HTML
# ════════════════════════════════════════════════════════════════════════════
plotlyjs = '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'

html_body = f"""
{plotlyjs}

{html_header}
{html_kpis}

<!-- PAGE 1 : VUE GÉNÉRALE -->
<div class="section-title">Vue Générale — Évolution & Géographie</div>
<div class="charts-row">
  <div class="chart-box full">{chart_monthly}</div>
</div>

<!-- PAGE 2 : PRODUITS & CLIENTS -->
<div class="section-title">Produits & Clients</div>
<div class="charts-row">
  <div class="chart-box half">{chart_prod}</div>
  <div class="chart-box half">{chart_cust}</div>
</div>
<div class="charts-row">
  <div class="chart-box half">{chart_country}</div>
  <div class="chart-box half">{chart_heat}</div>
</div>

<!-- PAGE 3 : SEGMENTATION RFM -->
<div class="section-title">Segmentation RFM</div>
<div class="charts-row">
  <div class="chart-box half">{chart_donut}</div>
  <div class="chart-box half">{chart_seg}</div>
</div>
<div class="charts-row">
  <div class="chart-box full">{chart_scatter}</div>
</div>
<div class="charts-row">
  <div class="chart-box full">{chart_rfm_dist}</div>
</div>

<!-- FOOTER -->
<div class="footer">
  📊 E-commerce Sales Analysis Dashboard &nbsp;|&nbsp;
  Dataset : UCI Online Retail &nbsp;|&nbsp;
  Construit avec Python · Plotly · Pandas
  <br>
  👤 <strong>Data Analyst Portfolio</strong> &nbsp;|&nbsp;
  ✉️ <a href="mailto:sall1969@outlook.fr" style="color:#3498DB;">sall1969@outlook.fr</a> &nbsp;|&nbsp;
  📞 77 245 62 22
</div>

</body></html>
"""

# ── Export ───────────────────────────────────────────────────────────────────
output_path = "reports/dashboard.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_body)

print(f"\n{'='*50}")
print(f"  Dashboard généré : {output_path}")
print(f"  Ouvrir dans un navigateur pour visualiser.")
print(f"{'='*50}")
