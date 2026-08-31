-- ============================================================
-- Projet BI : Analyse des Ventes E-commerce
-- Script 3 : Requêtes d'analyse business
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- A. KPIs GLOBAUX
-- ─────────────────────────────────────────────────────────────

SELECT
    ROUND(SUM(total_amount)::NUMERIC, 2)            AS chiffre_affaires_total,
    COUNT(DISTINCT invoice_no)                       AS nb_commandes,
    COUNT(DISTINCT customer_id)                      AS nb_clients,
    ROUND(SUM(total_amount) / COUNT(DISTINCT invoice_no), 2) AS panier_moyen,
    COUNT(DISTINCT stock_code)                       AS nb_produits_distincts
FROM sales;


-- ─────────────────────────────────────────────────────────────
-- B. CHIFFRE D'AFFAIRES PAR MOIS
-- ─────────────────────────────────────────────────────────────

SELECT
    year,
    month,
    TO_CHAR(invoice_date, 'YYYY-MM')         AS periode,
    ROUND(SUM(total_amount)::NUMERIC, 2)     AS ca_mensuel,
    COUNT(DISTINCT invoice_no)               AS nb_commandes,
    COUNT(DISTINCT customer_id)              AS nb_clients_actifs
FROM sales
GROUP BY year, month, TO_CHAR(invoice_date, 'YYYY-MM')
ORDER BY year, month;


-- ─────────────────────────────────────────────────────────────
-- C. TOP 10 PRODUITS PAR REVENU
-- ─────────────────────────────────────────────────────────────

SELECT
    stock_code,
    description,
    SUM(quantity)                            AS qte_vendue,
    ROUND(SUM(total_amount)::NUMERIC, 2)     AS ca_total,
    ROUND(AVG(unit_price)::NUMERIC, 2)       AS prix_moyen
FROM sales
GROUP BY stock_code, description
ORDER BY ca_total DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- D. TOP 10 PRODUITS PAR QUANTITÉ VENDUE
-- ─────────────────────────────────────────────────────────────

SELECT
    stock_code,
    description,
    SUM(quantity)                            AS qte_vendue,
    ROUND(SUM(total_amount)::NUMERIC, 2)     AS ca_total
FROM sales
GROUP BY stock_code, description
ORDER BY qte_vendue DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- E. TOP 10 CLIENTS PAR CHIFFRE D'AFFAIRES
-- ─────────────────────────────────────────────────────────────

SELECT
    customer_id,
    country,
    COUNT(DISTINCT invoice_no)               AS nb_commandes,
    ROUND(SUM(total_amount)::NUMERIC, 2)     AS ca_total,
    ROUND(AVG(total_amount)::NUMERIC, 2)     AS panier_moyen
FROM sales
GROUP BY customer_id, country
ORDER BY ca_total DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- F. CHIFFRE D'AFFAIRES PAR PAYS
-- ─────────────────────────────────────────────────────────────

SELECT
    country,
    COUNT(DISTINCT customer_id)              AS nb_clients,
    COUNT(DISTINCT invoice_no)               AS nb_commandes,
    ROUND(SUM(total_amount)::NUMERIC, 2)     AS ca_total,
    ROUND(100.0 * SUM(total_amount) /
          SUM(SUM(total_amount)) OVER (), 2) AS pct_ca
FROM sales
GROUP BY country
ORDER BY ca_total DESC
LIMIT 15;


-- ─────────────────────────────────────────────────────────────
-- G. PANIER MOYEN PAR PAYS
-- ─────────────────────────────────────────────────────────────

SELECT
    country,
    ROUND(SUM(total_amount) /
          COUNT(DISTINCT invoice_no), 2)     AS panier_moyen,
    COUNT(DISTINCT invoice_no)               AS nb_commandes
FROM sales
GROUP BY country
HAVING COUNT(DISTINCT invoice_no) >= 50
ORDER BY panier_moyen DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- H. VENTES PAR JOUR DE LA SEMAINE
-- ─────────────────────────────────────────────────────────────

SELECT
    day_name,
    COUNT(DISTINCT invoice_no)               AS nb_commandes,
    ROUND(SUM(total_amount)::NUMERIC, 2)     AS ca_total,
    ROUND(AVG(total_amount)::NUMERIC, 2)     AS ca_moyen_par_commande
FROM sales
GROUP BY day_name
ORDER BY ca_total DESC;


-- ─────────────────────────────────────────────────────────────
-- I. TAUX DE RÉACHAT (clients ayant commandé 2+ fois)
-- ─────────────────────────────────────────────────────────────

WITH orders_per_customer AS (
    SELECT customer_id, COUNT(DISTINCT invoice_no) AS nb_orders
    FROM sales
    GROUP BY customer_id
)
SELECT
    COUNT(*)                                         AS total_clients,
    SUM(CASE WHEN nb_orders >= 2 THEN 1 ELSE 0 END) AS clients_reachats,
    ROUND(100.0 * SUM(CASE WHEN nb_orders >= 2 THEN 1 ELSE 0 END)
          / COUNT(*), 2)                             AS taux_reachat_pct
FROM orders_per_customer;


-- ─────────────────────────────────────────────────────────────
-- J. ANALYSE RFM EN SQL (vue pour Power BI)
-- ─────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW v_rfm AS
WITH snapshot AS (
    SELECT MAX(invoice_date) + INTERVAL '1 day' AS ref_date FROM sales
),
rfm_base AS (
    SELECT
        s.customer_id,
        MAX(s.country)                           AS country,
        EXTRACT(DAY FROM (
            (SELECT ref_date FROM snapshot) - MAX(s.invoice_date)
        ))::INTEGER                              AS recency,
        COUNT(DISTINCT s.invoice_no)             AS frequency,
        ROUND(SUM(s.total_amount)::NUMERIC, 2)   AS monetary
    FROM sales s
    GROUP BY s.customer_id
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency DESC)   AS r_score,
        NTILE(5) OVER (ORDER BY frequency)      AS f_score,
        NTILE(5) OVER (ORDER BY monetary)       AS m_score
    FROM rfm_base
)
SELECT
    customer_id,
    country,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CONCAT(r_score, f_score, m_score)           AS rfm_code,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3                  THEN 'Clients fidèles'
        WHEN r_score >= 3 AND f_score <= 2                  THEN 'Clients potentiels'
        WHEN r_score <= 2 AND f_score >= 3                  THEN 'Clients à risque'
        ELSE 'Clients perdus'
    END                                          AS segment
FROM rfm_scored;

-- Test de la vue RFM
SELECT segment, COUNT(*) AS nb_clients,
       ROUND(AVG(monetary)::NUMERIC, 2) AS monetary_moyen
FROM v_rfm
GROUP BY segment
ORDER BY nb_clients DESC;


-- ─────────────────────────────────────────────────────────────
-- K. CROISSANCE MENSUELLE DU CA (MoM)
-- ─────────────────────────────────────────────────────────────

WITH monthly AS (
    SELECT
        TO_CHAR(invoice_date, 'YYYY-MM')        AS periode,
        SUM(total_amount)                        AS ca
    FROM sales
    GROUP BY TO_CHAR(invoice_date, 'YYYY-MM')
)
SELECT
    periode,
    ROUND(ca::NUMERIC, 2)                        AS ca,
    LAG(ca) OVER (ORDER BY periode)              AS ca_precedent,
    ROUND((ca - LAG(ca) OVER (ORDER BY periode))
          / NULLIF(LAG(ca) OVER (ORDER BY periode), 0) * 100, 2) AS croissance_pct
FROM monthly
ORDER BY periode;
