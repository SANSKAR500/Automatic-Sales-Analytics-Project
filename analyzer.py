"""
analyzer.py
-----------
Takes the CLEANED DataFrame (from data_cleaner.py) and computes the
numbers and tables a sales report needs: totals, growth, top products,
trends over time, etc.

Every function returns simple Python/pandas objects (numbers, DataFrames)
so both the Jupyter notebook and the Streamlit app can reuse them.
"""

import pandas as pd


def summary_kpis(df: pd.DataFrame, column_map: dict) -> dict:
    """Returns the headline numbers: total revenue, total orders, avg order value, etc."""
    revenue_col = column_map.get("revenue")
    qty_col = column_map.get("quantity")

    total_revenue = df[revenue_col].sum() if revenue_col else None
    total_orders = len(df)
    avg_order_value = (total_revenue / total_orders) if (total_revenue and total_orders) else None
    total_units = df[qty_col].sum() if qty_col else None

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "total_units_sold": total_units,
    }


def revenue_over_time(df: pd.DataFrame, column_map: dict, freq: str = "ME") -> pd.DataFrame:
    """
    Groups revenue by time period.
    freq: 'D' = daily, 'W' = weekly, 'ME' = monthly, 'QE' = quarterly
    Returns a DataFrame with columns: period, revenue
    """
    date_col = column_map.get("date")
    revenue_col = column_map.get("revenue")
    if not date_col or not revenue_col:
        return pd.DataFrame()

    temp = df[[date_col, revenue_col]].dropna()
    temp = temp.set_index(date_col).resample(freq)[revenue_col].sum().reset_index()
    temp.columns = ["period", "revenue"]
    return temp


def top_items(df: pd.DataFrame, column_map: dict, role: str = "product", n: int = 10) -> pd.DataFrame:
    """
    Ranks top N items (products, regions, or customers) by revenue.
    role: 'product', 'region', or 'customer'
    """
    item_col = column_map.get(role)
    revenue_col = column_map.get("revenue")
    if not item_col or not revenue_col:
        return pd.DataFrame()

    result = (
        df.groupby(item_col)[revenue_col]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    result.columns = [role.capitalize(), "Revenue"]
    return result


def growth_rate(time_series_df: pd.DataFrame) -> float:
    """
    Given a revenue_over_time DataFrame, returns % growth from the
    first period to the last period. Useful as a single headline stat.
    """
    if time_series_df.empty or len(time_series_df) < 2:
        return None
    first = time_series_df["revenue"].iloc[0]
    last = time_series_df["revenue"].iloc[-1]
    if first == 0:
        return None
    return round(((last - first) / first) * 100, 2)


def category_breakdown(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """Revenue share by category, if a category column exists."""
    cat_col = column_map.get("category")
    revenue_col = column_map.get("revenue")
    if not cat_col or not revenue_col:
        return pd.DataFrame()

    result = df.groupby(cat_col)[revenue_col].sum().sort_values(ascending=False).reset_index()
    result.columns = ["Category", "Revenue"]
    return result


def generate_text_report(df: pd.DataFrame, column_map: dict) -> str:
    """Builds a plain-English written summary of the dataset's key findings."""
    kpis = summary_kpis(df, column_map)
    ts = revenue_over_time(df, column_map, freq="ME")
    growth = growth_rate(ts)
    top_products = top_items(df, column_map, "product", n=5)

    lines = ["SALES ANALYTICS REPORT", "=" * 40, ""]

    if kpis["total_revenue"] is not None:
        lines.append(f"Total Revenue: {kpis['total_revenue']:,.2f}")
    lines.append(f"Total Orders: {kpis['total_orders']:,}")
    if kpis["avg_order_value"] is not None:
        lines.append(f"Average Order Value: {kpis['avg_order_value']:,.2f}")
    if kpis["total_units_sold"] is not None:
        lines.append(f"Total Units Sold: {kpis['total_units_sold']:,.0f}")

    if growth is not None:
        trend_word = "grew" if growth >= 0 else "declined"
        lines.append(f"\nRevenue {trend_word} by {abs(growth)}% from the first to the last period in the data.")

    if not top_products.empty:
        lines.append("\nTop 5 Products by Revenue:")
        for _, row in top_products.iterrows():
            lines.append(f"  - {row.iloc[0]}: {row.iloc[1]:,.2f}")

    return "\n".join(lines)
