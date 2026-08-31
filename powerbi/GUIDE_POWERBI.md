# Guide complet Power BI — E-commerce Sales Dashboard

> **Temps estimé :** 2h30 pour la première construction complète  
> **Version Power BI :** Desktop 2.x (gratuit) — avril 2024 ou plus récent  
> **Fichiers source :** `data/sales_clean.csv` · `data/rfm_segments.csv`

---

## Sommaire

1. [Import et transformation des données (Power Query)](#1-import-et-transformation-power-query)
2. [Modèle de données et relations](#2-modèle-de-données-et-relations)
3. [Table Calendrier](#3-table-calendrier)
4. [Toutes les mesures DAX](#4-toutes-les-mesures-dax)
5. [Page 1 — Vue Générale](#5-page-1--vue-générale)
6. [Page 2 — Produits & Clients](#6-page-2--produits--clients)
7. [Page 3 — Segmentation RFM](#7-page-3--segmentation-rfm)
8. [Filtres et slicers](#8-filtres-et-slicers)
9. [Thème et mise en forme](#9-thème-et-mise-en-forme)
10. [Interactions entre visuels](#10-interactions-entre-visuels)
11. [Tooltips personnalisés](#11-tooltips-personnalisés)
12. [Publication et partage](#12-publication-et-partage)

---

## 1. Import et transformation (Power Query)

### 1.1 Importer `sales_clean.csv`

1. Ouvrir Power BI Desktop
2. **Accueil → Obtenir des données → Texte/CSV**
3. Naviguer vers `C:\projet\bi1\data\sales_clean.csv` → **Ouvrir**
4. Dans la fenêtre d'aperçu, cliquer sur **Transformer les données** (ne pas cliquer Charger directement)

### 1.2 Transformations dans Power Query Editor

Dans l'éditeur Power Query, vérifier et corriger chaque colonne :

| Colonne | Type à appliquer | Comment faire |
|---|---|---|
| `InvoiceNo` | Texte | Clic droit sur l'en-tête → Type → Texte |
| `StockCode` | Texte | Idem |
| `Description` | Texte | Idem |
| `Quantity` | Nombre entier | Clic droit → Nombre entier |
| `InvoiceDate` | Date/Heure | Clic droit → Date/Heure |
| `UnitPrice` | Nombre décimal | Clic droit → Nombre décimal |
| `CustomerID` | Texte | **Important** : garder en Texte, pas en nombre |
| `Country` | Texte | Idem |
| `TotalAmount` | Nombre décimal | Idem |
| `Year` | Nombre entier | Idem |
| `Month` | Nombre entier | Idem |
| `MonthName` | Texte | Idem |
| `DayName` | Texte | Idem |
| `Hour` | Nombre entier | Idem |

> **Astuce :** Si Power Query détecte les types automatiquement, vérifiez quand même `InvoiceDate` — il arrive qu'il soit importé en Texte selon les paramètres régionaux. Si c'est le cas : clic droit → **Modifier le type → Utiliser les paramètres régionaux → Anglais (États-Unis)**.

#### Colonnes optionnelles à ajouter dans Power Query

Cliquer sur **Ajouter une colonne → Colonne personnalisée** :

**Trimestre :**
```
= "T" & Text.From(Date.QuarterOfYear([InvoiceDate]))
```

**Semaine ISO :**
```
= Date.WeekOfYear([InvoiceDate])
```

#### Renommer la requête

Dans le panneau de gauche "Requêtes", clic droit sur la requête → **Renommer** → `sales`

### 1.3 Importer `rfm_segments.csv`

1. **Accueil → Obtenir des données → Texte/CSV**
2. Sélectionner `C:\projet\bi1\data\rfm_segments.csv` → **Transformer les données**

Types à vérifier :

| Colonne | Type |
|---|---|
| `CustomerID` | Texte |
| `Recency` | Nombre entier |
| `Frequency` | Nombre entier |
| `Monetary` | Nombre décimal |
| `R_Score`, `F_Score`, `M_Score` | Nombre entier |
| `RFM_Score` | Texte |
| `Segment` | Texte |

Renommer la requête : `rfm`

### 1.4 Appliquer et fermer

Cliquer sur **Accueil → Fermer et appliquer**. Power BI charge les deux tables.

---

## 2. Modèle de données et relations

Aller dans la vue **Modèle** (icône diagramme dans le panneau gauche).

### 2.1 Relation principale : sales ↔ rfm

- Glisser `sales[CustomerID]` vers `rfm[CustomerID]`
- Dans la boîte de dialogue :
  - **Cardinalité :** Plusieurs à un (*:1)
  - **Direction du filtre croisé :** Unique (de rfm vers sales)
  - Cocher **Actif**

### 2.2 Relation avec le Calendrier (créé à l'étape 3)

- Relier `Calendrier[Date]` → `sales[InvoiceDate]`
- **Cardinalité :** Un à plusieurs (1:*)
- **Direction du filtre :** Unique (de Calendrier vers sales)

### 2.3 Vue finale du modèle

```
Calendrier ──(1:*)──► sales ──(*:1)──► rfm
    [Date]           [InvoiceDate]   [CustomerID]
                     [CustomerID]
```

---

## 3. Table Calendrier

Dans Power BI Desktop, aller dans **Modélisation → Nouvelle table** et coller :

```dax
Calendrier =
ADDCOLUMNS(
    CALENDAR(DATE(2010, 12, 1), DATE(2011, 12, 31)),
    "Année",        YEAR([Date]),
    "Mois_Num",     MONTH([Date]),
    "NomMois",      FORMAT([Date], "MMM YYYY"),
    "NomMoisCourt", FORMAT([Date], "MMM"),
    "Trimestre",    "T" & FORMAT(QUARTER([Date]), "0"),
    "SemaineFin",   WEEKNUM([Date]),
    "JourSemaine",  WEEKDAY([Date], 2),
    "NomJour",      FORMAT([Date], "dddd"),
    "AnnéeTrim",    FORMAT([Date], "YYYY") & " T" & FORMAT(QUARTER([Date]), "0")
)
```

> **Pourquoi une table Calendrier ?** Elle garantit une continuité des dates (même les jours sans vente apparaissent dans les graphiques temporels) et active les fonctions Time Intelligence de DAX (DATEADD, SAMEPERIODLASTYEAR…).

#### Trier NomMois par Mois_Num

1. Cliquer sur la colonne `NomMois` dans la vue Données
2. **Outils de colonne → Trier par colonne → Mois_Num**

Faire de même : `NomJour` → trier par `JourSemaine`

---

## 4. Toutes les mesures DAX

### 4.1 Créer le tableau de mesures

**Modélisation → Nouvelle table** :
```dax
_Mesures = ROW("info", "Tableau de mesures — ne pas supprimer")
```
Nommer cette table `_Mesures`. Toutes les mesures seront créées dans cette table pour garder le modèle organisé.

### 4.2 Mesures de base

```dax
-- ── Chiffre d'affaires ───────────────────────────────────────
CA Total =
SUM(sales[TotalAmount])

CA Formaté =
"£" & FORMAT([CA Total], "#,##0.00")

-- ── Volume ───────────────────────────────────────────────────
Nb Commandes =
DISTINCTCOUNT(sales[InvoiceNo])

Nb Clients =
DISTINCTCOUNT(sales[CustomerID])

Nb Produits =
DISTINCTCOUNT(sales[StockCode])

Quantité Totale =
SUM(sales[Quantity])

-- ── Moyennes ─────────────────────────────────────────────────
Panier Moyen =
DIVIDE([CA Total], [Nb Commandes])

CA Moyen Par Client =
DIVIDE([CA Total], [Nb Clients])

Quantité Moy Par Commande =
DIVIDE([Quantité Totale], [Nb Commandes])
```

### 4.3 Mesures temporelles (Time Intelligence)

> Ces mesures nécessitent la **table Calendrier** reliée à `sales[InvoiceDate]`.

```dax
-- ── Mois précédent ──────────────────────────────────────────
CA Mois Précédent =
CALCULATE(
    [CA Total],
    DATEADD(Calendrier[Date], -1, MONTH)
)

-- ── Croissance MoM ──────────────────────────────────────────
Croissance MoM % =
VAR _ca_courant   = [CA Total]
VAR _ca_precedent = [CA Mois Précédent]
RETURN
    DIVIDE(_ca_courant - _ca_precedent, _ca_precedent) * 100

-- ── Même période année précédente ───────────────────────────
CA Année Précédente =
CALCULATE(
    [CA Total],
    SAMEPERIODLASTYEAR(Calendrier[Date])
)

-- ── Croissance YoY ──────────────────────────────────────────
Croissance YoY % =
DIVIDE([CA Total] - [CA Année Précédente], [CA Année Précédente]) * 100

-- ── Cumul annuel (YTD) ───────────────────────────────────────
CA YTD =
TOTALYTD([CA Total], Calendrier[Date])

-- ── Meilleur mois (label pour carte) ────────────────────────
Meilleur Mois =
MAXX(
    TOPN(1,
        SUMMARIZE(Calendrier, Calendrier[NomMois], "CA", [CA Total]),
        [CA], DESC
    ),
    Calendrier[NomMois]
)
```

### 4.4 Mesures de rétention

```dax
-- ── Taux de réachat ─────────────────────────────────────────
Taux Réachat % =
VAR _clients_multi =
    CALCULATE(
        DISTINCTCOUNT(sales[CustomerID]),
        FILTER(
            VALUES(sales[CustomerID]),
            CALCULATE(DISTINCTCOUNT(sales[InvoiceNo])) >= 2
        )
    )
RETURN
    DIVIDE(_clients_multi, [Nb Clients]) * 100

-- ── Clients actifs ce mois ──────────────────────────────────
Clients Actifs Mois =
CALCULATE(
    DISTINCTCOUNT(sales[CustomerID]),
    DATESMTD(Calendrier[Date])
)

-- ── Nouveaux clients (1 seule commande) ─────────────────────
Nouveaux Clients =
CALCULATE(
    DISTINCTCOUNT(sales[CustomerID]),
    FILTER(
        VALUES(sales[CustomerID]),
        CALCULATE(DISTINCTCOUNT(sales[InvoiceNo])) = 1
    )
)
```

### 4.5 Mesures RFM et segments

```dax
-- ── CA par segment (pour les cartes) ────────────────────────
CA Champions =
CALCULATE([CA Total], rfm[Segment] = "Champions")

CA Fidèles =
CALCULATE([CA Total], rfm[Segment] = "Clients fidèles")

CA À Risque =
CALCULATE([CA Total], rfm[Segment] = "Clients à risque")

-- ── % du CA par segment ─────────────────────────────────────
Pct CA Segment =
DIVIDE([CA Total], CALCULATE([CA Total], ALL(rfm[Segment]))) * 100

-- ── Recency moyenne du segment sélectionné ──────────────────
Recency Moyenne =
AVERAGE(rfm[Recency])

-- ── Monetary moyen ──────────────────────────────────────────
Monetary Moyen =
AVERAGE(rfm[Monetary])

-- ── Frequency moyenne ───────────────────────────────────────
Frequency Moyenne =
AVERAGE(rfm[Frequency])
```

### 4.6 Mesures avancées pour les tooltips

```dax
-- ── Rang produit par CA ──────────────────────────────────────
Rang Produit CA =
RANKX(
    ALL(sales[Description]),
    [CA Total],
    ,
    DESC,
    DENSE
)

-- ── Rang client par CA ──────────────────────────────────────
Rang Client CA =
RANKX(
    ALL(sales[CustomerID]),
    [CA Total],
    ,
    DESC,
    DENSE
)

-- ── Part de marché pays ──────────────────────────────────────
Part Pays % =
DIVIDE(
    [CA Total],
    CALCULATE([CA Total], ALL(sales[Country]))
) * 100
```

---

## 5. Page 1 — Vue Générale

### 5.1 Mise en page

**Format de la page :** Affichage → Format de la page → 16:9 (1280 × 720 px)

Diviser la page en 3 zones :
- **Zone haute (hauteur ~120px) :** bande titre + logo
- **Zone KPI (hauteur ~120px) :** 5 cartes côte à côte
- **Zone graphiques (reste) :** 2 visuels principaux

### 5.2 Bandeau titre

- Insérer → **Zone de texte**
- Texte : `Analyse des Ventes E-commerce`
- Police : Segoe UI Bold, taille 20, couleur blanche
- Fond du rectangle : `#1B3A6B`
- Ajouter sous-titre : `Période : Dec 2010 – Dec 2011 | Source : UCI E-commerce Dataset`

### 5.3 Cartes KPI (5 cartes)

Créer une **Carte** pour chaque KPI. Pour chaque carte :

**Carte 1 — CA Total**
- Champ : `[CA Total]`
- Format → Valeur d'appel : Format → Devise → `£#,##0`
- Étiquette : `Chiffre d'Affaires`
- Couleur de fond : `#EBF5FB`
- Bordure gauche colorée : `#3498DB` (épaisseur 4px via Rectangle superposé)

**Carte 2 — Nb Commandes**
- Champ : `[Nb Commandes]`
- Format : `#,##0`
- Étiquette : `Commandes`
- Couleur fond : `#EAF7EF`, bordure : `#2ECC71`

**Carte 3 — Nb Clients**
- Champ : `[Nb Clients]`
- Étiquette : `Clients Actifs`
- Fond : `#FEF9E7`, bordure : `#F39C12`

**Carte 4 — Panier Moyen**
- Champ : `[Panier Moyen]`
- Format : `£#,##0.00`
- Étiquette : `Panier Moyen`
- Fond : `#FDEDEC`, bordure : `#E74C3C`

**Carte 5 — Taux Réachat**
- Champ : `[Taux Réachat %]`
- Format : `0.0"%"`
- Étiquette : `Taux de Réachat`
- Fond : `#F0E6FF`, bordure : `#8E44AD`

### 5.4 Graphique : Évolution mensuelle du CA

**Type :** Graphique en courbes et histogramme empilé

- **Axe X :** `Calendrier[NomMois]` (trié par Mois_Num)
- **Valeurs de la colonne :** `[Nb Commandes]` → barres grises en fond
- **Valeurs de la ligne :** `[CA Total]` → courbe bleue `#3498DB`
- **Axe Y gauche :** Nb Commandes (format `#,##0`)
- **Axe Y droit :** CA Total (format `£#,##0`)

**Formatage :**
- Activer les **marqueurs** sur la courbe (cercle, taille 5)
- Activer les **étiquettes de données** sur la courbe uniquement
- Titre : `Évolution Mensuelle — CA et Volume`
- Quadrillage : lignes horizontales légères (`#ECF0F1`)

### 5.5 Carte géographique : CA par pays

**Type :** Carte choroplèthe (Carte remplie)

- **Emplacement :** `sales[Country]`
- **Saturation des couleurs :** `[CA Total]`
- **Info-bulles :** `sales[Country]`, `[CA Total]`, `[Nb Clients]`, `[Part Pays %]`
- **Échelle de couleurs :** blanc → `#1B3A6B` (du minimum au maximum)
- Cocher **Afficher les étiquettes**

> **Astuce :** Si certains pays ne s'affichent pas sur la carte, aller dans Power Query → colonne `Country` → **Outils de colonne → Catégorie de données → Pays ou région**.

### 5.6 Mini-indicateur : Croissance MoM

**Type :** Carte avec mesure `[Croissance MoM %]`
- Format : `+0.0"% vs mois préc."` (formater côté mesure DAX si nécessaire)
- Ajouter un **indicateur de tendance** : icône flèche verte/rouge via formatage conditionnel

---

## 6. Page 2 — Produits & Clients

### 6.1 Top 10 Produits par CA

**Type :** Graphique à barres horizontales groupées

- **Axe Y :** `sales[Description]`
- **Axe X :** `[CA Total]`
- **Filtre visuel :** Rang Produit CA ≤ 10

Configuration du filtre :
1. Dans le volet Filtres → **Filtres sur ce visuel**
2. Glisser `[Rang Produit CA]`
3. Type de filtre : **Nombre inférieur ou égal à** → valeur `10`

**Formatage :**
- Couleur des barres : `#3498DB`
- Étiquettes de données : activées, format `£#,##0`
- Trier par `[CA Total]` décroissant
- Titre : `Top 10 Produits — Chiffre d'Affaires`

### 6.2 Top 10 Clients par CA

**Type :** Graphique à barres horizontales

- **Axe Y :** `sales[CustomerID]`
- **Axe X :** `[CA Total]`
- **Filtre visuel :** `[Rang Client CA]` ≤ 10
- Couleur : `#2ECC71`
- Info-bulles : `CustomerID`, `[CA Total]`, `[Nb Commandes]`, `rfm[Segment]`
- Titre : `Top 10 Clients — Chiffre d'Affaires`

### 6.3 Répartition CA par pays (Top 15)

**Type :** Graphique à barres verticales

- **Axe X :** `sales[Country]`
- **Axe Y :** `[CA Total]`
- **Filtre visuel :** `[Part Pays %]` — Top N 15
- Couleur dégradée selon `[CA Total]` (bleu clair → bleu foncé)
- Activer l'**axe logarithmique** (UK domine fortement → meilleure lisibilité)
- Titre : `CA par Pays`

### 6.4 Heatmap Jour × Heure

**Type :** Matrice

- **Lignes :** `sales[DayName]` (trié par JourSemaine via Calendrier)
- **Colonnes :** `sales[Hour]`
- **Valeurs :** `[CA Total]`

**Formatage conditionnel :**
1. Cliquer sur le chevron `▼` à côté de `[CA Total]` dans Valeurs
2. **Formatage conditionnel → Couleur d'arrière-plan**
3. Style : **Dégradé**
4. Couleur min : blanc `#FFFFFF`
5. Couleur max : rouge `#C0392B`
6. Centré sur : valeur médiane

**Formatage général :**
- Supprimer les en-têtes de lignes/colonnes inutiles
- Format des valeurs : `£#,##0`
- Titre : `Heatmap Activité — Jour et Heure (CA £)`

### 6.5 Ventes par jour de la semaine

**Type :** Histogramme (barres verticales)

- **Axe X :** `sales[DayName]` (trié par JourSemaine)
- **Axe Y :** `[Nb Commandes]`
- Couleur : dégradé basé sur la valeur (faible = vert, élevé = orange)
- Activer les **étiquettes de données**
- Titre : `Commandes par Jour de la Semaine`

---

## 7. Page 3 — Segmentation RFM

### 7.1 Graphique anneau : Répartition des clients par segment

**Type :** Graphique en anneau (Donut)

- **Légende :** `rfm[Segment]`
- **Valeurs :** `[Nb Clients]`
- **Info-bulles :** `Segment`, `[Nb Clients]`, `[CA Total]`, `[Monetary Moyen]`

**Couleurs par segment (formatage des couleurs) :**
| Segment | Couleur |
|---|---|
| Champions | `#27AE60` |
| Clients fidèles | `#2980B9` |
| Clients potentiels | `#F39C12` |
| Clients à risque | `#E67E22` |
| Clients perdus | `#E74C3C` |

- Épaisseur intérieure : 60 %
- Ajouter étiquette au centre via **Zone de texte** superposée : `4 338\nClients`

### 7.2 Graphique barres : CA par segment

**Type :** Graphique à barres horizontales

- **Axe Y :** `rfm[Segment]`
- **Axe X :** `[CA Total]`
- **Couleurs :** reprendre les mêmes couleurs que le donut (formatage conditionnel par valeur de catégorie)
- **Étiquettes :** `[CA Total]` format `£#,##0` + `[Pct CA Segment]` format `0.0%`
- Trier par `[CA Total]` décroissant
- Titre : `Contribution CA par Segment`

**Ajouter une 2ème axe :**
- Axe Y secondaire : `[Pct CA Segment]` affiché comme courbe

### 7.3 Scatter plot : Recency vs Monetary

**Type :** Nuage de points

- **Axe X :** `[Recency Moyenne]` (ou `rfm[Recency]` avec niveau détails = CustomerID)
- **Axe Y :** `[Monetary Moyen]` (ou `rfm[Monetary]`)
- **Légende :** `rfm[Segment]`
- **Taille des bulles :** `[Frequency Moyenne]`
- **Détails :** `rfm[CustomerID]`

> **Astuce :** Pour afficher chaque client individuellement, glisser `rfm[CustomerID]` dans le champ **Détails** du nuage de points.

**Formatage :**
- Opacité des bulles : 60 %
- Quadrillage : `#ECF0F1`
- Axe X inversé (Recency faible = bon client, doit apparaître à droite)
  → Activer **Axe X → Inverser la plage**
- Titre : `Carte RFM : Récence vs Valeur (taille = Fréquence)`

### 7.4 Tableau détail RFM

**Type :** Table

Colonnes à afficher :
| Colonne | Format |
|---|---|
| `rfm[CustomerID]` | Texte |
| `rfm[Segment]` | Texte (avec mise en forme conditionnelle couleur) |
| `rfm[Recency]` | `0 "j"` |
| `rfm[Frequency]` | `0 "cmd"` |
| `rfm[Monetary]` | `£#,##0.00` |
| `rfm[R_Score]` | Barres de données (0→5) |
| `rfm[F_Score]` | Barres de données (0→5) |
| `rfm[M_Score]` | Barres de données (0→5) |

**Mise en forme conditionnelle sur la colonne Segment :**
1. Clic sur `▼` à côté de `Segment` → Formatage conditionnel → Couleur d'arrière-plan
2. Règles :
   - `Champions` → fond `#D5F5E3`
   - `Clients fidèles` → fond `#D6EAF8`
   - `Clients potentiels` → fond `#FDEBD0`
   - `Clients à risque` → fond `#FAE5D3`
   - `Clients perdus` → fond `#FADBD8`

### 7.5 Cartes KPI RFM (4 petites cartes)

| Carte | Mesure | Format |
|---|---|---|
| Recency moyenne | `[Recency Moyenne]` | `0 "jours"` |
| Frequency moyenne | `[Frequency Moyenne]` | `0.0 "cmd"` |
| Monetary moyen | `[Monetary Moyen]` | `£#,##0` |
| Taux Réachat | `[Taux Réachat %]` | `0.0"%"` |

---

## 8. Filtres et Slicers

### 8.1 Panneau de filtres commun (toutes les pages)

Créer un **panneau latéral** sur chaque page (rectangle fond `#F2F3F4`, largeur 180px, hauteur pleine page).

#### Slicer 1 — Année
- **Type visuel :** Segment (Slicer)
- **Champ :** `Calendrier[Année]`
- **Style :** Liste déroulante
- **Sélection unique** activée
- Titre : `Année`

#### Slicer 2 — Trimestre
- **Champ :** `Calendrier[Trimestre]`
- **Style :** Boutons (Horizontal)
- Valeurs : T1, T2, T3, T4
- Titre : `Trimestre`

#### Slicer 3 — Pays
- **Champ :** `sales[Country]`
- **Style :** Liste (avec recherche activée)
- **Sélection multiple** activée (Ctrl+clic)
- Titre : `Pays`

#### Slicer 4 — Segment client (Page 3 seulement)
- **Champ :** `rfm[Segment]`
- **Style :** Liste avec cases à cocher
- Titre : `Segment RFM`

### 8.2 Synchronisation des slicers entre pages

**Affichage → Synchroniser les segments :**

| Slicer | Page 1 | Page 2 | Page 3 |
|---|---|---|---|
| Année | ✓ visible + sync | ✓ visible + sync | ✓ visible + sync |
| Trimestre | ✓ | ✓ | ✓ |
| Pays | ✓ | ✓ | - (optionnel) |
| Segment | - | - | ✓ |

---

## 9. Thème et mise en forme

### 9.1 Thème JSON personnalisé

Aller dans **Affichage → Thèmes → Personnaliser le thème actuel → Importer le thème**.

Créer le fichier `powerbi/theme_ecommerce.json` avec ce contenu :

```json
{
  "name": "Ecommerce BI Theme",
  "dataColors": [
    "#1B3A6B",
    "#3498DB",
    "#2ECC71",
    "#F39C12",
    "#E74C3C",
    "#8E44AD",
    "#1ABC9C",
    "#E67E22"
  ],
  "background": "#FFFFFF",
  "foreground": "#2C3E50",
  "tableAccent": "#3498DB",
  "visualStyles": {
    "*": {
      "*": {
        "fontFamily": [{ "value": "Segoe UI" }],
        "fontSize": [{ "value": 11 }]
      }
    },
    "card": {
      "*": {
        "fontSize": [{ "value": 28 }],
        "fontFamily": [{ "value": "Segoe UI Semibold" }],
        "labelFontSize": [{ "value": 11 }]
      }
    }
  }
}
```

### 9.2 Format des mesures monétaires

Pour toutes les mesures en £ : dans le volet **Outils de mesure → Format → Personnalisé** → saisir `£#,##0.00`

### 9.3 Formatage des nombres

| Type | Format |
|---|---|
| Montants | `£#,##0.00` |
| Grands montants | `£#,##0,,\M` (millions) |
| Pourcentages | `0.0%` |
| Entiers | `#,##0` |
| Jours | `0 "jours"` |

---

## 10. Interactions entre visuels

Par défaut, cliquer sur un élément d'un visuel filtre les autres. Personnaliser les interactions :

**Affichage → Modifier les interactions**

### Règles recommandées — Page 1

| Visuel source | Action | Visuel cible | Comportement |
|---|---|---|---|
| Carte pays | Clic sur un pays | Graphique courbes | Filtrer |
| Carte pays | Clic sur un pays | Cartes KPI | Filtrer |
| Graphique courbes | Clic sur un mois | Carte pays | Mettre en surbrillance |

### Règles recommandées — Page 3

| Visuel source | Action | Visuel cible | Comportement |
|---|---|---|---|
| Donut segments | Clic sur segment | Scatter | Filtrer |
| Donut segments | Clic sur segment | Tableau RFM | Filtrer |
| Scatter | Clic sur bulle | Tableau RFM | Filtrer |

---

## 11. Tooltips personnalisés

### Créer une page Tooltip pour les produits

1. Ajouter une nouvelle page → **Format → Type de page → Info-bulle**
2. Nommer : `Tooltip_Produit`
3. Ajouter sur cette page :
   - Titre dynamique (Zone de texte liée)
   - Carte : `[CA Total]`
   - Carte : `[Quantité Totale]`
   - Carte : `[Nb Commandes]`
   - Mini graphique courbe : évolution mensuelle

4. Sur le visuel Top 10 Produits → **Format → Info-bulle → Page → Tooltip_Produit**

### Créer une page Tooltip pour les clients

1. Nouvelle page → Type Info-bulle → `Tooltip_Client`
2. Ajouter :
   - Carte : `[CA Total]`
   - Carte : `rfm[Segment]`
   - Carte : `rfm[Recency]`
   - Carte : `rfm[Frequency]`
   - Mini donut : répartition des achats par catégorie

---

## 12. Publication et partage

### 12.1 Sauvegarder le fichier

**Fichier → Enregistrer sous** → `C:\projet\bi1\powerbi\ecommerce_dashboard.pbix`

### 12.2 Exporter en PDF

**Fichier → Exporter → Exporter au format PDF**

- Sélectionner toutes les pages
- Options : inclure les signets, inclure les pages masquées : Non

### 12.3 Publier sur Power BI Service

> Nécessite un compte Power BI Pro ou une licence organisationnelle.

1. **Accueil → Publier**
2. Sélectionner **Mon espace de travail** (ou un espace d'équipe)
3. URL d'accès générée automatiquement
4. Pour partager : **Power BI Service → Partager → Copier le lien**

### 12.4 Créer une application Power BI (facultatif)

Si vous voulez un portail complet :
1. Power BI Service → **Espaces de travail → Créer une application**
2. Ajouter le rapport comme contenu
3. Configurer les permissions d'accès
4. Publier l'application → lien partageable

---

## Récapitulatif — Checklist finale

### Données
- [ ] `sales_clean.csv` importé et types vérifiés
- [ ] `rfm_segments.csv` importé et types vérifiés
- [ ] Table Calendrier créée
- [ ] Relations configurées (sales↔rfm, Calendrier↔sales)

### Mesures DAX
- [ ] Mesures de base (CA, commandes, clients, panier)
- [ ] Mesures Time Intelligence (MoM, YoY, YTD)
- [ ] Mesures RFM (CA par segment, Pct CA, moyennes)
- [ ] Mesures de rang (produits, clients)

### Pages
- [ ] Page 1 : 5 KPI + courbe mensuelle + carte géographique
- [ ] Page 2 : Top 10 produits + Top 10 clients + Heatmap + Barres jours
- [ ] Page 3 : Donut + Barres segments + Scatter + Tableau RFM

### Filtres
- [ ] Slicer Année synchronisé toutes pages
- [ ] Slicer Trimestre synchronisé
- [ ] Slicer Pays synchronisé
- [ ] Slicer Segment (Page 3)

### Mise en forme
- [ ] Thème JSON appliqué
- [ ] Formats monétaires £ configurés
- [ ] Couleurs RFM cohérentes entre visuels
- [ ] Tris chronologiques corrects (NomMois, NomJour)
- [ ] Tooltips personnalisés

### Export
- [ ] Fichier .pbix sauvegardé
- [ ] Export PDF généré
- [ ] Publié sur Power BI Service (si compte disponible)
