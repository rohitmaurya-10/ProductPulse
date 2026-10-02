import streamlit as st
import pandas as pd
from src.database import get_connection


st.set_page_config(
    page_title="ProductPulse",
    page_icon="📊",
    layout="wide"
)


def load_product_data():

    connection = get_connection()

    query = """
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        p.sales,
        p.returns,
        f.rating,
        f.issue_category,
        f.feedback_text
    FROM products p
    LEFT JOIN feedback f
        ON p.product_id = f.product_id;
    """

    df = pd.read_sql(query, connection)

    connection.close()

    return df


st.title("📊 ProductPulse")
st.subheader("Product Performance & Customer Feedback Dashboard")

df = load_product_data()

# Product summary
summary = df.groupby(
    ["product_id", "product_name", "category", "price", "sales", "returns"]
).agg(
    average_rating=("rating", "mean"),
    complaints=("feedback_text", "count")
).reset_index()

summary["return_rate"] = (
    summary["returns"] / summary["sales"] * 100
)

# -------------------------
# KPI SECTION
# -------------------------

total_products = summary["product_id"].nunique()
total_sales = summary["sales"].sum()
total_returns = summary["returns"].sum()
average_rating = summary["average_rating"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Products", total_products)
col2.metric("Total Sales", f"{total_sales:,}")
col3.metric("Total Returns", f"{total_returns:,}")
col4.metric("Average Rating", f"{average_rating:.2f} ⭐")

# -------------------------
# PRODUCT FILTER
# -------------------------

st.sidebar.header("Product Filter")

product_options = ["All Products"] + sorted(
    summary["product_name"].unique().tolist()
)

selected_product = st.sidebar.selectbox(
    "Select a product",
    product_options
)

if selected_product != "All Products":
    filtered_summary = summary[
        summary["product_name"] == selected_product
    ]

    filtered_feedback = df[
        df["product_name"] == selected_product
    ]
else:
    filtered_summary = summary
    filtered_feedback = df

# -------------------------
# PRODUCT TABLE
# -------------------------

st.header("Product Performance")

display_df = filtered_summary[
    [
        "product_name",
        "category",
        "price",
        "sales",
        "returns",
        "return_rate",
        "average_rating",
        "complaints"
    ]
].copy()

display_df["return_rate"] = display_df["return_rate"].round(2)
display_df["average_rating"] = display_df["average_rating"].round(2)

st.dataframe(
    display_df,
    use_container_width=True
)


# -------------------------
# SALES CHART
# -------------------------

st.header("Sales by Product")

sales_chart = filtered_summary.set_index("product_name")["sales"]

st.bar_chart(sales_chart)


# -------------------------
# RETURN RATE
# -------------------------

st.header("Return Rate by Product")

return_chart = filtered_summary.set_index("product_name")["return_rate"]

st.bar_chart(return_chart)

# -------------------------
# PRODUCT HEALTH
# -------------------------

st.header("🩺 Product Health")

for _, row in filtered_summary.iterrows():

    if row["average_rating"] < 3:
        health = "🔴 Needs Attention"

    elif row["return_rate"] > 10:
        health = "🟠 Monitor"

    else:
        health = "🟢 Healthy"

    st.write(
        f"**{row['product_name']}** — {health}"
    )
# -------------------------
# TOP CUSTOMER ISSUES
# -------------------------

st.header("🔎 Top Customer Issues")

issue_counts = filtered_feedback["issue_category"].value_counts()

st.bar_chart(issue_counts)
# -------------------------
# TOP CUSTOMER ISSUES
# -------------------------

st.header("🔎 Top Customer Issues")

issue_counts = filtered_feedback["issue_category"].value_counts()

st.bar_chart(issue_counts)
# -------------------------
# PRODUCT INSIGHTS
# -------------------------

st.header("💡 Product Insights")

for _, row in filtered_summary.iterrows():

    if row["average_rating"] < 3:

        st.warning(
            f"⚠️ {row['product_name']}: "
            f"Average rating is {row['average_rating']:.2f}. "
            "Investigate customer complaints and product quality."
        )

    elif row["return_rate"] > 10:

        st.warning(
            f"⚠️ {row['product_name']}: "
            f"Return rate is {row['return_rate']:.2f}%. "
            "Investigate the main reasons for product returns."
        )

    else:

        st.success(
            f"✅ {row['product_name']}: "
            "Current performance is relatively stable."
        )


# -------------------------
# CUSTOMER FEEDBACK
# -------------------------

st.header("Customer Feedback")

feedback_display = filtered_feedback[
    [
        "product_name",
        "rating",
        "issue_category",
        "feedback_text"
    ]
].copy()

st.dataframe(
    feedback_display,
    use_container_width=True
)