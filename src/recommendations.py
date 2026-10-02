import pandas as pd
from database import get_connection


def load_data():
    connection = get_connection()

    query = """
    SELECT
        p.product_name,
        p.category,
        p.sales,
        p.returns,
        f.rating,
        f.issue_category,
        f.feedback_text
    FROM products p
    JOIN feedback f
        ON p.product_id = f.product_id;
    """

    df = pd.read_sql(query, connection)

    connection.close()

    return df


def generate_insights(df):

    summary = df.groupby("product_name").agg(
        average_rating=("rating", "mean"),
        sales=("sales", "first"),
        returns=("returns", "first"),
        complaints=("feedback_text", "count")
    ).reset_index()

    summary["return_rate"] = (
        summary["returns"] / summary["sales"] * 100
    )

    print("\n--- PRODUCT INSIGHTS ---")

    for _, row in summary.iterrows():

        print(f"\nProduct: {row['product_name']}")
        print(f"Average Rating: {row['average_rating']:.2f}")
        print(f"Return Rate: {row['return_rate']:.2f}%")
        print(f"Customer Complaints: {row['complaints']}")

        if row["average_rating"] < 3:
            print("Recommendation: Investigate product quality and customer complaints.")

        elif row["return_rate"] > 10:
            print("Recommendation: Investigate the main reasons for product returns.")

        else:
            print("Recommendation: Product performance is currently stable.")


if __name__ == "__main__":

    df = load_data()

    generate_insights(df)