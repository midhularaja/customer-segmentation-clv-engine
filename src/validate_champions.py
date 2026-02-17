import pandas as pd
from src.db_connection import get_engine
import matplotlib.pyplot as plt

engine = get_engine()

def validate_champions():
    print("Validating 'Champions' segment...")

    # Load RFM table
    rfm_final = pd.read_sql("SELECT * FROM rfm_customer_segments", engine)

    if rfm_final.empty:
        print("No data found in rfm_customer_segments. Run RFM pipeline first.")
        return

    # Filter Champions
    champions = rfm_final[rfm_final['segment'] == 'Champions']

    # Top 10 spenders overall
    top_spenders = rfm_final.sort_values(by='monetary', ascending=False).head(10)
    print("Top 10 spenders overall:\n", top_spenders[['customer_key','monetary','frequency','recency','segment']])

    # Median comparison
    champions_median = champions['monetary'].median()
    overall_median = rfm_final['monetary'].median()
    print(f"\nChampions median spend: {champions_median}")
    print(f"Overall median spend: {overall_median}")

    # Boxplot for visual check
    rfm_final.boxplot(column='monetary', by='segment', figsize=(10,6))
    plt.title("Monetary distribution by segment")
    plt.ylabel("Monetary Value")
    plt.show()

if __name__ == "__main__":
    validate_champions()
