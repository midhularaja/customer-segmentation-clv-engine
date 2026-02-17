import pandas as pd
from sqlalchemy.types import DateTime
import pycountry
import pycountry_convert as pc
from src.db_connection import get_engine

engine = get_engine()
def safe_qcut(series, bins=5, labels=None):
    """qcut fallback if duplicates exist"""
    try:
        return pd.qcut(series, bins, labels=labels)
    except ValueError:
        ranked = series.rank(method="first")
        return pd.cut(ranked, bins, labels=labels)

def country_to_region(country):
    manual_map = {
        "USA": "United States",
        "U.S.": "United States",
        "UK": "United Kingdom",
        "U.K.": "United Kingdom",
        "Korea, South": "South Korea",
        "South Korea": "South Korea"
    }
    if country in manual_map:
        country = manual_map[country]
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
        return region_map.get(continent)
    except:
        return None

def assign_segment(row):
    r, f, m = int(row["r_score"]), int(row["f_score"]), int(row["m_score"])
    if r >= 4 and f >= 4 and m >= 4: return "Champions"
    if r >= 3 and f >= 3 and m >= 3: return "Loyal Customers"
    if r >= 4 and f <= 3 and m >= 3: return "Potential Loyalist"
    if r >= 4 and f <= 2 and m <= 2: return "Recent Users"
    if r == 4 and f == 1 and m <= 2: return "Promising"
    if r <= 2 and f >= 4 and m >= 4: return "Can't Lose Them"
    if r <= 2 and f >= 3: return "Needs Attention"
    if r == 3 and f <= 2: return "About to Sleep"
    if r >= 3 and m <= 2: return "Price Sensitive"
    if r <= 2 and f <= 2 and m <= 2: return "Hibernating"
    return "Lost"


def main():
    # Load fact_sales
    fact_sales = pd.read_sql(
        "SELECT customer_key, InvoiceNo, total_amount, date_key FROM fact_sales",
        engine
    )
    fact_sales["invoice_date"] = pd.to_datetime(
        fact_sales["date_key"].astype(str), format="%Y%m%d", errors="coerce"
    )
    analysis_date = fact_sales["invoice_date"].max() + pd.Timedelta(days=1)

    # Compute RFM
    rfm = fact_sales.groupby("customer_key").agg({
        "invoice_date": [
            lambda x: (analysis_date - x.max()).days,  # Recency
            "max"                                     # Last purchase
        ],
        "InvoiceNo": "nunique",  # Frequency
        "total_amount": "sum"    # Monetary
    }).reset_index()
    rfm.columns = ["customer_key", "recency", "last_purchase_date", "frequency", "monetary"]

    # RFM scoring
    rfm["r_score"] = safe_qcut(rfm["recency"], 5, labels=[5,4,3,2,1])
    rfm["f_score"] = safe_qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
    rfm["m_score"] = safe_qcut(rfm["monetary"], 5, labels=[1,2,3,4,5])
    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)

    # Segment assignment
    rfm["segment"] = rfm.apply(assign_segment, axis=1)

    # Load customer dimension
    dim_customer = pd.read_sql("SELECT customer_key, Country FROM dim_customer", engine)
    dim_customer["customer_key"] = dim_customer["customer_key"].astype(int)
    dim_customer["Country"] = dim_customer["Country"].str.strip()

    rfm["customer_key"] = rfm["customer_key"].astype(int)
    rfm = rfm.merge(dim_customer, on="customer_key", how="left")

    # Country → Region
    rfm["Region"] = rfm["Country"].apply(country_to_region)

    # Valid RFM
    rfm_final = rfm[rfm["Region"].notna()].copy()
    rfm_final = rfm_final[[
        "customer_key","Country","Region","recency","frequency","monetary",
        "r_score","f_score","m_score","rfm_score","segment","last_purchase_date"
    ]]

    # Push to DB
    rfm_final.to_sql(
        "rfm_customer_segments",
        con=engine,
        if_exists="replace",
        index=False,
        dtype={"last_purchase_date": DateTime()}
    )

    # Invalid countries
    rfm_invalid = rfm[rfm["Region"].isna()].copy()
    rfm_invalid.to_sql(
        "rfm_invalid_countries",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("RFM segmentation completed successfully")

if __name__ == "__main__":
    main()
