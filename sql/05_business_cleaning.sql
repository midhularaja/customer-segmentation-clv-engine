-- Create clean table from staging
CREATE TABLE clean_data AS
SELECT *FROM staging_data;
-- Remove cancelled invoices + corresponding original invoices
DELETE FROM clean_data
WHERE InvoiceNo LIKE 'C%' 
   OR InvoiceNo IN (
       SELECT SUBSTRING(InvoiceNo, 2)
       FROM (SELECT InvoiceNo FROM clean_data WHERE InvoiceNo LIKE 'C%') AS temp_sub
   );
-- Remove invalid Quantity / UnitPrice
DELETE FROM clean_data
WHERE Quantity <= 0
   OR UnitPrice <= 0;
-- Remove rows with missing CustomerID
DELETE FROM clean_data
WHERE CustomerID IS NULL;

-- Remove rows with invalid StockCode pattern
DELETE FROM clean_data
WHERE NOT (
        (LENGTH(StockCode)=5 and StockCode BETWEEN '00000' AND '99999')
        OR
        (LENGTH(StockCode)=6
        AND SUBSTRING(StockCode,1,5) BETWEEN '00000' AND '99999'
        AND ASCII(SUBSTRING(StockCode,6,1)) BETWEEN 65 AND 90)
);

-- Remove duplicates (InvoiceNo + StockCode + CustomerID)
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY InvoiceNo, StockCode, CustomerID
               ORDER BY InvoiceDate, Quantity, UnitPrice
           ) AS rn
    FROM clean_data
)
DELETE FROM clean_data
WHERE EXISTS(
    SELECT 1
    FROM ranked r
    WHERE r.InvoiceNo = clean_data.InvoiceNo
    AND r.StockCode =clean_data.StockCode
    AND r.CustomerID = clean_data.CustomerID
    AND r.rn>1
);

-- Canonical description assignment per StockCode
UPDATE clean_data c
JOIN (
    SELECT s.StockCode, s.Description
    FROM clean_data s
    JOIN (
        -- Find the most frequent Description per StockCode
        SELECT StockCode, Description
        FROM clean_data
        GROUP BY StockCode, Description
        ORDER BY StockCode, COUNT(*) DESC
    ) freq
    ON s.StockCode = freq.StockCode AND s.Description = freq.Description
    GROUP BY s.StockCode
) canonical
ON c.StockCode = canonical.StockCode
SET c.Description = canonical.Description;
