-- Create staging table from raw data (raw_data untouched)
create table staging_data as select * from raw_data;

-- Technical cleaning in staging
-- 1. clean numeric column
-- handle empty numeric identifiers before type conversion
UPDATE staging_data
SET CustomerID = NULL
WHERE CustomerID = '';

-- Convert Quantity column to integer type
ALTER TABLE staging_data 
MODIFY Quantity INT;

-- Convert UnitPrice column to decimal type 
ALTER TABLE staging_data 
MODIFY UnitPrice DECIMAL(10,2);

-- Convert CustomerID column to integer type
ALTER TABLE staging_data
MODIFY CustomerID INT;

--2. clean string column
-- Description → remove extra spaces + convert to uppercase
UPDATE staging_data
SET Description = UPPER(TRIM(Description))
WHERE Description IS NOT NULL;

-- Country → convert to uppercase 
UPDATE staging_data
SET Country = UPPER(TRIM(Country))
WHERE Country IS NOT NULL;

-- StockCode → convert to uppercase 
UPDATE staging_data
SET StockCode = UPPER(TRIM(StockCode))
WHERE StockCode IS NOT NULL;

-- 3. Convert InvoiceDate from string to proper DATETIME format
UPDATE staging_data
SET InvoiceDate = STR_TO_DATE(InvoiceDate, '%m/%d/%Y %H:%i')
WHERE InvoiceDate IS NOT NULL;

--4. Handle missing / empty Description by assigning temporary placeholder 'UNKNOWN'
UPDATE staging_data
SET Description = 'UNKNOWN'
WHERE Description IS NULL OR TRIM(Description)= '';

--5. Remove minor duplicates (exact row duplicates) only
CREATE TABLE staging_data_dedup AS
SELECT DISTINCT *
FROM staging_data;
-- Drop old staging table (with duplicates)
DROP TABLE staging_data;
-- Rename dedup table to original staging table name
RENAME TABLE staging_data_dedup TO staging_data;






