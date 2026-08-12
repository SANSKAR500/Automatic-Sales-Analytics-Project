"""
app.py
------
This is the Streamlit dashboard. Run it with:
    streamlit run app.py

It lets you upload ANY sales CSV/Excel file, then automatically cleans
it and shows KPIs, charts, and a downloadable report.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from data_cleaner import clean_pipeline
from analyzer import (
    summary_kpis,
    revenue_over_time,
    top_items,
    growth_rate,
    category_breakdown,
    generate_text_report,
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Automatic Sales Analytics", layout="wide")
st.title("📊 Automatic Sales Analytics Dashboard")
st.caption("Upload any sales CSV or Excel file — it'll be cleaned and analyzed automatically.")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload a sales file", type=["csv", "xlsx", "xls"])

if uploaded_file is None:
    st.info("👆 Upload a file to get started. No file? Try the included sample_sales_data.csv.")
    st.stop()

# ---------------- CLEAN THE DATA ----------------
with st.spinner("Cleaning your data..."):
    df, column_map = clean_pipeline(uploaded_file, uploaded_file.name)

if df.empty:
    st.error("The file loaded but had no usable rows after cleaning. Please check the file.")
    st.stop()

# Let the user confirm/fix the auto-detected columns, in case the guess was wrong
with st.expander("🔍 Detected columns (click to review or fix)"):
    cols = list(df.columns)
    for role in ["date", "revenue", "quantity", "product", "region", "customer", "category"]:
        current = column_map.get(role)
        options = ["(none)"] + cols
        idx = options.index(current) if current in options else 0
        choice = st.selectbox(f"{role.capitalize()} column", options, index=idx, key=role)
        column_map[role] = None if choice == "(none)" else choice

# ---------------- KPIs ----------------
kpis = summary_kpis(df, column_map)
ts = revenue_over_time(df, column_map, freq="ME")
growth = growth_rate(ts)

st.subheader("Key Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"{kpis['total_revenue']:,.0f}" if kpis["total_revenue"] is not None else "N/A")
c2.metric("Total Orders", f"{kpis['total_orders']:,}")
c3.metric("Avg Order Value", f"{kpis['avg_order_value']:,.2f}" if kpis["avg_order_value"] is not None else "N/A")
c4.metric("Revenue Growth", f"{growth}%" if growth is not None else "N/A")

st.divider()

# ---------------- CHARTS ----------------
left, right = st.columns(2)

with left:
    st.subheader("Revenue Over Time")
    if not ts.empty:
        fig = px.line(ts, x="period", y="revenue", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Couldn't find date/revenue columns for a trend chart.")

with right:
    st.subheader("Top Products")
    top_p = top_items(df, column_map, "product", n=10)
    if not top_p.empty:
        fig = px.bar(top_p, x="Revenue", y=top_p.columns[0], orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No product column detected.")

left2, right2 = st.columns(2)

with left2:
    st.subheader("Top Regions")
    top_r = top_items(df, column_map, "region", n=10)
    if not top_r.empty:
        fig = px.bar(top_r, x="Revenue", y=top_r.columns[0], orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No region column detected.")

with right2:
    st.subheader("Category Breakdown")
    cat = category_breakdown(df, column_map)
    if not cat.empty:
        fig = px.pie(cat, names="Category", values="Revenue")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category column detected.")

st.divider()

# ---------------- TEXT REPORT + DOWNLOAD ----------------
st.subheader("📝 Auto-Generated Report")
report_text = generate_text_report(df, column_map)
st.text(report_text)

col_a, col_b = st.columns(2)
with col_a:
    st.download_button(
        "⬇️ Download Text Report",
        data=report_text,
        file_name="sales_report.txt",
        mime="text/plain",
    )
with col_b:
    st.download_button(
        "⬇️ Download Cleaned Data (CSV)",
        data=df.to_csv(index=False),
        file_name="cleaned_sales_data.csv",
        mime="text/csv",
    )

with st.expander("View cleaned data table"):
    st.dataframe(df, use_container_width=True)
