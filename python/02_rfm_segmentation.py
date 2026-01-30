import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Midhu%4029@localhost/customer_segmentation_db")

fact_sales = pd.read_sql("select * from fact_sales",engine)

fact_sales["InvoiceDate"]=pd.to_datetime(fact_sales["date_key"].astype(str), format="%Y%m%d")
# set reference date for recency
analysis_date = fact_sales["InvoiceDate"].max()+pd.Timedelta(days=1)

# calculate rfm matrics
rfm = fact_sales.groupby("customer_key").agg({
    "InvoiceDate": lambda x: (analysis_date - x.max()).days,  
    "InvoiceNo": "nunique",                                  
    "total_amount": "sum"                                    
}).reset_index()

rfm.columns = ["customer_key", "Recency", "Frequency", "Monetary"]
print(rfm.head())

# RFM scoring 1 to 5
# recency
rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5,4,3,2,1],duplicates="drop")
# Frequency
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
# Monetary
rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5],duplicates="drop")


# assign segments
def assign_segment(row):
    r = int(row["R_Score"])
    f = int(row["F_Score"])
    m = int(row["M_Score"])
    
    # Behavioral patterns 
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
    
# apply segmentation
rfm['Segment']=rfm.apply(assign_segment,axis=1)
print(rfm.head(50))

# validation check
avg_monetary_segment = rfm.groupby("Segment")["Monetary"].mean().sort_values(ascending=False)
print("Average Monetary per Segment:",avg_monetary_segment)

champions = rfm[rfm["Segment"] == "Champions"]
print("\nChampions segment customers:", champions.shape[0])
print("Average spending of Champions:", champions["Monetary"].mean())



