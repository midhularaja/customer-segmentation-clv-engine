import pandas as pd 
from src.db_connection import get_engine

df= pd.read_excel(r"C:\Customer_Segmentation_CLV_Engine_Project\Revenue_Target.xlsx")
engine = get_engine()
df.to_sql('revenuetarget', con=engine, if_exists='append', index=False)
