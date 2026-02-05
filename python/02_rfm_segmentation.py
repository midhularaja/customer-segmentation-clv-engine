import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import DateTime
import pycountry
import pycountry_convert as pc

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

    elif r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"

    elif r >= 4 and f <= 3 and m >= 3:
        return "Potential Loyalist"

    elif r >= 4 and f <= 2 and m <= 2:
        return "Recent Users"

    elif r == 4 and f == 1 and m <= 2:
        return "Promising"

    elif r <= 2 and f >= 4 and m >= 4:
        return "Can't Lose Them"

    elif r <= 2 and f >= 3:
        return "Needs Attention"

    elif r == 3 and f <= 2:
        return "About to Sleep"

    elif r >= 3 and m <= 2:
        return "Price Sensitive"

    elif r <= 2 and f <= 2 and m <= 2:
        return "Hibernating"

    else:
        return "Lost"



rfm["segment"] = rfm.apply(assign_segment, axis=1)

dim_customer = pd.read_sql(
    "SELECT customer_key, Country FROM dim_customer",
    engine
)

rfm["customer_key"] = rfm["customer_key"].astype(int)
dim_customer["customer_key"] = dim_customer["customer_key"].astype(int)
dim_customer["Country"] = dim_customer["Country"].str.strip()

rfm = rfm.merge(dim_customer, on="customer_key", how="left")

def country_to_region(country):
    try:
        alpha2 = pycountry.countries.lookup(country).alpha_2
        continent = pc.country_alpha2_to_continent_code(alpha2)

        region_map = {
            "AS": "Asia",
            "EU": "Europe",
            "AF": "Africa",
            "NA": "North America",
            "SA": "South America",
            "OC": "Australia"
        }
        return region_map.get(continent, "Others")
    except:
        return "Others"

rfm["Region"] = rfm["Country"].apply(country_to_region)

rfm["rfm_score"] = (
    rfm["r_score"].astype(str) +
    rfm["f_score"].astype(str) +
    rfm["m_score"].astype(str)
)

rfm_final = rfm[[
    "customer_key",
    "Country",
    "Region",
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
rfm_final = rfm_final.rename(columns={"lastpurchase": "last_purchase_date"})

rfm_final.to_sql(
    "rfm_customer_segments",
    con=engine,
    if_exists="replace",
    index=False,
    dtype={"last_purchase_date": DateTime()} 
)


