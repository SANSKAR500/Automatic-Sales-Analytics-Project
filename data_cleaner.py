"""
data_cleaner.py
----------------
This file's job: take ANY messy sales CSV/Excel file and turn it into a
clean, standardized pandas DataFrame that the rest of the project can use.

Beginner note: a "DataFrame" is just pandas' word for a spreadsheet-like
table living in Python's memory.
"""

import pandas as pd
import numpy as np
import re


# ----------------------------------------------------------------------
# 1. LOADING THE FILE
# ----------------------------------------------------------------------
def load_file(file_path_or_buffer, file_name: str = None) -> pd.DataFrame:
    """
    Loads a CSV or Excel file into a pandas DataFrame.

    file_path_or_buffer: a file path (string) OR an uploaded file object
                          (Streamlit gives us a file object, not a path).
    file_name: the original file name, used to decide csv vs excel when
               we only have a file object (Streamlit case).
    """
    name_to_check = file_name if file_name else str(file_path_or_buffer)

    if name_to_check.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path_or_buffer)
    else:
        # Try a couple of common separators/encodings before giving up.
        try:
            df = pd.read_csv(file_path_or_buffer)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path_or_buffer, encoding="latin1")

    return df


# ----------------------------------------------------------------------
# 2. AUTO-DETECTING WHICH COLUMN MEANS WHAT
# ----------------------------------------------------------------------
# Sales files use all sorts of column names: "Sales", "Revenue", "Amount",
# "Order Date", "Date", "Product", "Item", etc. We match against common
# keywords so the tool works on files we've never seen before.

COLUMN_HINTS = {
    "date": ["date", "order date", "invoice date", "purchase date", "day"],
    "revenue": ["revenue", "sales", "amount", "total", "sale amount",
                "total sales", "price", "net sales"],
    "quantity": ["quantity", "qty", "units", "units sold", "unit sold"],
    "product": ["product", "item", "product name", "sku", "product id"],
    "region": ["region", "state", "country", "city", "location", "market"],
    "customer": ["customer", "client", "customer name", "customer id"],
    "category": ["category", "segment", "product category", "type"],
}


def _best_match(column_names, keywords):
    """Returns the column name that best matches a list of keywords, or None."""
    lower_cols = {c: c.lower().strip() for c in column_names}
    # exact match first
    for col, low in lower_cols.items():
        if low in keywords:
            return col
    # partial/contains match second
    for col, low in lower_cols.items():
        for kw in keywords:
            if kw in low:
                return col
    return None


def detect_columns(df: pd.DataFrame) -> dict:
    """
    Scans the DataFrame's column names and returns a dictionary like:
    {"date": "Order Date", "revenue": "Sales", "product": "Item", ...}

    If a role isn't found, its value will be None.
    """
    mapping = {}
    for role, keywords in COLUMN_HINTS.items():
        mapping[role] = _best_match(df.columns, keywords)
    return mapping


# ----------------------------------------------------------------------
# 3. CLEANING THE DATA
# ----------------------------------------------------------------------
def clean_data(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """
    Cleans the DataFrame:
    - drops fully empty rows/columns
    - removes duplicate rows
    - converts the date column to real dates
    - converts revenue/quantity to numbers (strips $, commas, etc.)
    - fills small gaps sensibly
    """
    df = df.copy()

    # Drop rows/columns that are entirely empty
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Remove exact duplicate rows
    before = len(df)
    df.drop_duplicates(inplace=True)
    duplicates_removed = before - len(df)

    # Clean the date column
    date_col = column_map.get("date")
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df.dropna(subset=[date_col], inplace=True)  # drop rows with bad dates

    # Clean numeric columns (revenue, quantity): strip currency symbols/commas
    for role in ["revenue", "quantity"]:
        col = column_map.get(role)
        if col and col in df.columns:
            if df[col].dtype == object:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(r"[^\d.\-]", "", regex=True)  # keep digits, dot, minus
                    .replace("", np.nan)
                )
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].fillna(0)

    # Trim whitespace on text columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    df.attrs["duplicates_removed"] = duplicates_removed
    return df


def clean_pipeline(file_path_or_buffer, file_name: str = None):
    """
    Full pipeline: load -> detect columns -> clean.
    Returns (cleaned_df, column_map) so the analyzer knows which column is which.
    """
    raw_df = load_file(file_path_or_buffer, file_name)
    column_map = detect_columns(raw_df)
    cleaned_df = clean_data(raw_df, column_map)
    return cleaned_df, column_map
