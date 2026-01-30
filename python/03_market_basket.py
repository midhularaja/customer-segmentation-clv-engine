import pandas as pd
from sqlalchemy import create_engine
from mlxtend.frequent_patterns import fpgrowth, association_rules

engine = create_engine("mysql+pymysql://root:Midhu%4029@localhost/customer_segmentation_db")
fact_sales = pd.read_sql("select * from fact_sales", engine)

basket = fact_sales.groupby(["InvoiceNo", "product_key"]).size().unstack(fill_value=0)
basket_bool = basket > 0

top_products = basket_bool.sum().sort_values(ascending=False).head(100).index
basket_filtered = basket_bool[top_products]

frequent_itemsets = fpgrowth(basket_filtered, min_support=0.01, use_colnames=True)

rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1).sort_values("lift", ascending=False)

print(rules.head(10))
