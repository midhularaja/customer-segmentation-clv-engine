import pandas as pd
from src.db_connection import get_engine
from mlxtend.frequent_patterns import fpgrowth, association_rules


def main():
    engine = get_engine()

    fact_sales = pd.read_sql(
        "SELECT InvoiceNo, product_key FROM fact_sales",
        engine
    )

    basket = (
        fact_sales
        .groupby(["InvoiceNo", "product_key"])
        .size()
        .unstack(fill_value=0)
    )

    basket_bool = basket > 0

    top_products = (
        basket_bool.sum()
        .sort_values(ascending=False)
        .head(100)
        .index
    )

    basket_filtered = basket_bool[top_products]

    frequent_itemsets = fpgrowth(
        basket_filtered,
        min_support=0.01,
        use_colnames=True
    )

    rules = association_rules(
        frequent_itemsets,
        metric="lift",
        min_threshold=1
    ).sort_values("lift", ascending=False)

    
    rules["antecedents"] = rules["antecedents"].apply(
        lambda x: ",".join(map(str, list(x)))
    )

    rules["consequents"] = rules["consequents"].apply(
        lambda x: ",".join(map(str, list(x)))
    )

    rules.to_sql(
        "market_basket_rules",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("Market basket rules saved to database successfully")


if __name__ == "__main__":
    main()
