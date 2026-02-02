import pandas as pd 
from sqlalchemy import create_engine

df= pd.read_excel(r"C:\Customer_Segmentation_CLV_Engine_Project\Revenue_Target.xlsx")
engine = create_engine(
    "mysql+pymysql://root:Midhu%4029@localhost/customer_segmentation_db"
)
df.to_sql('revenuetarget', con=engine, if_exists='append', index=False)
