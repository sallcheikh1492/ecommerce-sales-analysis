-- ============================================================
-- Projet BI : Analyse des Ventes E-commerce
-- Script 1 : Création de la table sales
-- Compatible : PostgreSQL 14+ / MySQL 8+
-- ============================================================

-- PostgreSQL version
CREATE TABLE IF NOT EXISTS sales (
    id            SERIAL PRIMARY KEY,
    invoice_no    VARCHAR(20)    NOT NULL,
    stock_code    VARCHAR(20)    NOT NULL,
    description   TEXT,
    quantity      INTEGER        NOT NULL,
    invoice_date  TIMESTAMP      NOT NULL,
    unit_price    NUMERIC(10,2)  NOT NULL,
    customer_id   VARCHAR(20),
    country       VARCHAR(100),
    total_amount  NUMERIC(12,2)  NOT NULL,
    year          SMALLINT,
    month         SMALLINT,
    day_name      VARCHAR(15),
    hour          SMALLINT
);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_sales_customer   ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_date       ON sales(invoice_date);
CREATE INDEX IF NOT EXISTS idx_sales_country    ON sales(country);
CREATE INDEX IF NOT EXISTS idx_sales_stock      ON sales(stock_code);

-- ============================================================
-- MySQL version (décommentez si vous utilisez MySQL)
-- ============================================================
/*
CREATE TABLE IF NOT EXISTS sales (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    invoice_no    VARCHAR(20)    NOT NULL,
    stock_code    VARCHAR(20)    NOT NULL,
    description   TEXT,
    quantity      INT            NOT NULL,
    invoice_date  DATETIME       NOT NULL,
    unit_price    DECIMAL(10,2)  NOT NULL,
    customer_id   VARCHAR(20),
    country       VARCHAR(100),
    total_amount  DECIMAL(12,2)  NOT NULL,
    year          SMALLINT,
    month         SMALLINT,
    day_name      VARCHAR(15),
    hour          SMALLINT,
    INDEX idx_customer (customer_id),
    INDEX idx_date     (invoice_date),
    INDEX idx_country  (country),
    INDEX idx_stock    (stock_code)
);
*/
