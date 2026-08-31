-- ============================================================
-- Script 2 : Import des données nettoyées
-- ============================================================

-- PostgreSQL : COPY depuis CSV
COPY sales (invoice_no, stock_code, description, quantity, invoice_date,
            unit_price, customer_id, country, total_amount, year, month,
            day_name, hour)
FROM '/chemin/vers/data/sales_clean.csv'
DELIMITER ','
CSV HEADER;

-- Vérification
SELECT COUNT(*) AS nb_lignes FROM sales;
SELECT MIN(invoice_date) AS debut, MAX(invoice_date) AS fin FROM sales;
