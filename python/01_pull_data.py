import pandas as pd 
from sqlalchemy import create_engine


#Create SQLAlchemy engine
engine = create_engine("mysql+pymysql://root:Midhu%4029@localhost/customer_segmentation_db")

# pull tables into dataframes
fact_sales = pd.read_sql("select * from fact_sales",engine)
dim_customer = pd.read_sql("select * from  dim_customer",engine) 
dim_product = pd.read_sql("select * from  dim_product",engine)
dim_date = pd.read_sql("select * from  dim_date",engine)

