-- use database
use customer_segmentation_db;

-- create table
create table if not exists  raw_data(InvoiceNo varchar(50),StockCode varchar(50),Description varchar(50),Quantity varchar(50),InvoiceDate varchar(50),UnitPrice varchar(50),CustomerID varchar(50),Country varchar(50));
