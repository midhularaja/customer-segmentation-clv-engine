DROP TABLE IF EXISTS clean_data_verification;
CREATE TABLE clean_data_verification AS
SELECT
    -- Cancelled invoices check
    (SELECT COUNT(*) FROM clean_data WHERE InvoiceNo LIKE 'C%') AS cancelled_invoice_count,

    -- Invalid Quantity or UnitPrice check
    (SELECT COUNT(*) FROM clean_data WHERE Quantity <= 0 OR UnitPrice <= 0) AS invalid_quantity_unitprice_count,

    -- CustomerID null check
    (SELECT COUNT(*) FROM clean_data WHERE CustomerID IS NULL) AS missing_customerid_count,

    -- StockCode pattern check
    (SELECT COUNT(*) FROM clean_data 
      WHERE NOT (
           (LENGTH(StockCode)=5 AND StockCode BETWEEN '00000' AND '99999')
            OR
           (LENGTH(StockCode)=6
           AND SUBSTRING(StockCode,1,5) BETWEEN '00000' AND '99999'
           AND ASCII(SUBSTRING(StockCode,6,1)) BETWEEN 65 AND 90)
           )) 
           AS invalid_stockcode_count,


    -- Duplicates check (InvoiceNo + StockCode + CustomerID)
    (SELECT COUNT(*) FROM (
        SELECT InvoiceNo, StockCode, CustomerID
        FROM clean_data
        GROUP BY InvoiceNo, StockCode, CustomerID
        HAVING COUNT(*) > 1
    ) AS dup_check) AS duplicates_count,


    -- Empty Description check
    (SELECT COUNT(*) FROM clean_data WHERE Description IS NULL OR TRIM(Description) = '') AS empty_description_count,


    -- Non-canonical Description check per StockCode
    (SELECT COUNT(*) FROM (
        SELECT StockCode
        FROM clean_data
        GROUP BY StockCode
        HAVING COUNT(DISTINCT Description) > 1
    ) AS canonical_check) AS non_canonical_description_count,


    -- Total rows
    (SELECT COUNT(*) FROM clean_data) AS total_rows;















