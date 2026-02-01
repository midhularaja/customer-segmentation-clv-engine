import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import DateTime

engine = create_engine(
    "mysql+pymysql://root:Midhu%4029@localhost/customer_segmentation_db"
)

fact_sales = pd.read_sql(
    "SELECT customer_key, InvoiceNo, total_amount, date_key FROM fact_sales",
    engine
)

fact_sales["invoice_date"] = pd.to_datetime(
    fact_sales["date_key"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)

analysis_date = fact_sales["invoice_date"].max() + pd.Timedelta(days=1)

rfm = fact_sales.groupby("customer_key").agg({
    "invoice_date": [
        lambda x: (analysis_date - x.max()).days,  
        "max"                                    
    ],
    "InvoiceNo": "nunique",                       
    "total_amount": "sum"                        
}).reset_index()

rfm.columns = [
    "customer_key",
    "recency",
    "lastpurchase",  
    "frequency",
    "monetary"
]

rfm["lastpurchase"] = pd.to_datetime(rfm["lastpurchase"])

rfm["r_score"] = pd.qcut(
    rfm["recency"], 5, labels=[5, 4, 3, 2, 1], duplicates="drop"
)

rfm["f_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
)

rfm["m_score"] = pd.qcut(
    rfm["monetary"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop"
)

def assign_segment(row):
    r = int(row["r_score"])
    f = int(row["f_score"])
    m = int(row["m_score"])

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 3:
        return "Potential Loyalist"
    elif r == 5 and f == 1:
        return "New Customers"
    elif r == 4 and f == 1:
        return "Promising"
    elif r <= 2 and f >= 3:
        return "At Risk"
    elif r <= 2 and f <= 2:
        return "Hibernating"
    elif r == 3 and f <= 2:
        return "About to Sleep"
    else:
        return "Needs Attention"

rfm["segment"] = rfm.apply(assign_segment, axis=1)

dim_customer = pd.read_sql(
    "SELECT customer_key, Country FROM dim_customer",
    engine
)

rfm["customer_key"] = rfm["customer_key"].astype(int)
dim_customer["customer_key"] = dim_customer["customer_key"].astype(int)
dim_customer["Country"] = dim_customer["Country"].str.strip()

rfm = rfm.merge(dim_customer, on="customer_key", how="left")

rfm["rfm_score"] = (
    rfm["r_score"].astype(str) +
    rfm["f_score"].astype(str) +
    rfm["m_score"].astype(str)
)

rfm_final = rfm[[
    "customer_key",
    "Country",
    "recency",
    "frequency",
    "monetary",
    "r_score",
    "f_score",
    "m_score",
    "rfm_score",
    "segment",
    "lastpurchase"   
]]

rfm_final.to_sql(
    "rfm_customer_segments",
    con=engine,
    if_exists="replace",
    index=False,
    dtype={"lastpurchase": DateTime()} 
)


