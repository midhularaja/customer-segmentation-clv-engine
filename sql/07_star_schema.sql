-- dimcustomer
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    Country VARCHAR(50),
    UNIQUE KEY uniq_customer (CustomerID, Country)
);

INSERT IGNORE INTO dim_customer (CustomerID, Country)
SELECT DISTINCT CustomerID, Country
FROM clean_data
WHERE CustomerID IS NOT NULL;

-- dimproduct
CREATE TABLE IF NOT EXISTS dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    StockCode VARCHAR(50) NOT NULL,
    Description VARCHAR(50),
    UNIQUE KEY uniq_product (StockCode)
);

INSERT IGNORE INTO dim_product (StockCode, Description)
SELECT DISTINCT StockCode, Description
FROM clean_data
WHERE StockCode IS NOT NULL;

-- DimDate
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,          
    full_date DATE NOT NULL,
    `year_col` SMALLINT,
    `month_col` TINYINT,
    month_name VARCHAR(10),
    year_month_col CHAR(7),            
    `day_col` TINYINT,
    weekday_name VARCHAR(10)
);


INSERT IGNORE INTO dim_date
(date_key, full_date, `year_col`, `month_col`, month_name, year_month_col, `day_col`, weekday_name)
SELECT DISTINCT
    DATE_FORMAT(InvoiceDate, '%Y%m%d'),
    DATE(InvoiceDate),
    YEAR(InvoiceDate),
    MONTH(InvoiceDate),
    MONTHNAME(InvoiceDate),
    DATE_FORMAT(InvoiceDate, '%Y-%m'),
    DAY(InvoiceDate),
    DAYNAME(InvoiceDate)
FROM clean_data
WHERE InvoiceDate IS NOT NULL;


CREATE INDEX idx_dim_date_year_month ON dim_date(year_month_col);

-- FactSales
CREATE TABLE fact_sales (
    sales_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    InvoiceNo VARCHAR(50),
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,

    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),

    INDEX idx_fact_date (date_key),
    INDEX idx_fact_customer (customer_key),
    INDEX idx_fact_product (product_key),
    INDEX idx_fact_date_amount (date_key, total_amount)
);

INSERT INTO fact_sales (date_key, customer_key, product_key, InvoiceNo, Quantity, UnitPrice, total_amount)
SELECT
    DATE_FORMAT(c.InvoiceDate, '%Y%m%d'),
    dc.customer_key,
    dp.product_key,
    c.InvoiceNo,
    c.Quantity,
    c.UnitPrice,
    c.Quantity * c.UnitPrice
FROM clean_data c
JOIN dim_customer dc
    ON c.CustomerID = dc.CustomerID
   AND c.Country = dc.Country
JOIN dim_product dp
    ON c.StockCode = dp.StockCode
WHERE c.Quantity > 0
  AND c.UnitPrice > 0
  AND c.InvoiceDate IS NOT NULL;

-- ERD Verification Queries
SELECT COUNT(*) AS missing_dates
FROM fact_sales f
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL;

SELECT COUNT(*) AS missing_customers
FROM fact_sales f
LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL;

SELECT COUNT(*) AS missing_products
FROM fact_sales f
LEFT JOIN dim_product p ON f.product_key = p.product_key
WHERE p.product_key IS NULL;


-- <Analytics Queries (<2 sec)
SELECT dp.StockCode, dp.Description, SUM(f.total_amount) AS total_sales
FROM fact_sales f
JOIN dim_product dp ON f.product_key = dp.product_key
GROUP BY dp.product_key
ORDER BY total_sales DESC;

SELECT dc.CustomerID, dc.Country, SUM(f.total_amount) AS total_sales
FROM fact_sales f
JOIN dim_customer dc ON f.customer_key = dc.customer_key
GROUP BY dc.customer_key
ORDER BY total_sales DESC;

SELECT d.year_month_col, SUM(f.total_amount) AS total_sales
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year_month_col
ORDER BY d.year_month_col;
