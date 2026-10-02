import pandas as pd
from database import get_connection


def load_feedback_data():
    connection = get_connection()

    query = """
    SELECT
        f.feedback_id,
        c.customer_name,
        p.product_name,
        p.category,
        p.price,
        p.sales,
        p.returns,
        f.rating,
        f.feedback_text,
        f.issue_category
    FROM feedback f
    JOIN customers c
        ON f.customer_id = c.customer_id
    JOIN products p
        ON f.product_id = p.product_id;
    """

    df = pd.read_sql(query, connection)

    connection.close()

    return df


def product_analysis(df):

    product_summary = df.groupby("product_name").agg(
        average_rating=("rating", "mean"),
        sales=("sales", "first"),
        returns=("returns", "first"),
        complaints=("feedback_id", "count")
    ).reset_index()

    product_summary["return_rate"] = (
        product_summary["returns"] /
        product_summary["sales"] * 100
    )

    return product_summary


if __name__ == "__main__":

    df = load_feedback_data()

    print("\n--- PRODUCTPULSE ANALYSIS ---")

    summary = product_analysis(df)

    print(summary.to_string(index=False))