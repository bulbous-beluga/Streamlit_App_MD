import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Data App Assignment, on July 14th")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='ME')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

# (1) Select a category
categories = sorted(df["Category"].dropna().unique())

selected_category = st.selectbox(
    "Select a category",
    options=categories,
)

# Only keep rows belonging to the selected category
category_df = df.loc[df["Category"] == selected_category]

# (2) Select subcategories within that category
subcategories = sorted(category_df["Sub_Category"].dropna().unique())

selected_subcategories = st.multiselect(
    "Select subcategories",
    options=subcategories,
    default=subcategories,
    key=f"subcategories_{selected_category}",
)

# Only keep rows belonging to the selected subcategories
filtered_df = category_df.loc[
    category_df["Sub_Category"].isin(selected_subcategories)
]

# Calculate the baseline using the entire dataset, not the filtered data
all_sales = df["Sales"].sum()
all_profit = df["Profit"].sum()

overall_margin = (
    all_profit / all_sales * 100
    if all_sales != 0
    else None
)

if filtered_df.empty:
    st.info("Select at least one subcategory to display the chart and metrics.")

else:
    # (3) Aggregate selected sales by month and display a line chart
    selected_monthly_sales = (
        filtered_df[["Sales"]]
        .groupby(pd.Grouper(freq="ME"))
        .sum()
        .sort_index()
    )

    st.subheader("Monthly sales for selected subcategories")
    st.line_chart(selected_monthly_sales, y="Sales")

    # (4) Calculate metrics for the filtered data
    total_sales = filtered_df["Sales"].sum()
    total_profit = filtered_df["Profit"].sum()

    selected_margin = (
        total_profit / total_sales * 100
        if total_sales != 0
        else None
    )

    # (5) Compare selected profit margin with the overall profit margin
    margin_delta = (
        selected_margin - overall_margin
        if selected_margin is not None and overall_margin is not None
        else None
    )

    sales_col, profit_col, margin_col = st.columns(3)

    sales_col.metric(
        label="Total sales",
        value=f"${total_sales:,.2f}",
    )

    profit_col.metric(
        label="Total profit",
        value=f"${total_profit:,.2f}",
    )

    margin_col.metric(
        label="Overall profit margin",
        value=(
            f"{selected_margin:.2f}%"
            if selected_margin is not None
            else "N/A"
        ),
        delta=(
            f"{margin_delta:.2f} percentage points"
            if margin_delta is not None
            else None
        ),
        help=(
            "Selected profit margin = selected total profit / "
            "selected total sales × 100. "
            "Delta = selected margin minus the full-dataset margin."
        ),
    )

    if overall_margin is not None:
        st.caption(
            f"All-products profit margin: {overall_margin:.2f}%. "
            "The delta compares the selected items with this baseline."
        )