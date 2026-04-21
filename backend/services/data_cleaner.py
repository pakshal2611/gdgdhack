"""
Data cleaning and standardization service.
"""
import pandas as pd
import re


# Column name normalization mapping
LABEL_MAP = {
    "sales": "revenue",
    "total sales": "revenue",
    "net sales": "revenue",
    "total revenue": "revenue",
    "turnover": "revenue",
    "income": "revenue",
    "total income": "revenue",
    "net profit": "profit",
    "net income": "profit",
    "pat": "profit",
    "profit after tax": "profit",
    "net earnings": "profit",
    "earnings": "profit",
    "bottom line": "profit",
    "fiscal year": "year",
    "fy": "year",
    "period": "year",
    "date": "year",
}


def clean_dataframe(df):
    """
    Clean a DataFrame:
    - Remove currency symbols (₹, $, €, £, commas)
    - Convert string numbers to numeric
    - Drop completely empty rows
    """
    if df.empty:
        return df

    df = df.copy()

    for col in df.columns:
        if df[col].dtype == object:
            # Remove currency symbols and commas
            df[col] = df[col].apply(lambda x: _clean_value(x) if isinstance(x, str) else x)

    # Drop rows where all values are NaN or empty
    df = df.dropna(how="all")
    df = df.reset_index(drop=True)

    return df


def _clean_value(value):
    """Clean a single string value — remove symbols, try to convert to number."""
    if not value or not isinstance(value, str):
        return value

    cleaned = value.strip()
    # Remove currency symbols and common prefixes
    cleaned = re.sub(r'[₹$€£,]', '', cleaned)
    # Remove parentheses used for negative numbers: (100) → -100
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = "-" + cleaned[1:-1]
    # Remove spaces in numbers
    cleaned = cleaned.replace(" ", "")

    # Try to convert to float
    try:
        return float(cleaned)
    except ValueError:
        return value


def normalize_labels(df):
    """
    Normalize column names to standard labels.
    Maps various names to: year, revenue, profit
    """
    if df.empty:
        return df

    df = df.copy()

    # Normalize column names
    new_columns = {}
    for col in df.columns:
        col_lower = str(col).strip().lower()
        if col_lower in LABEL_MAP:
            new_columns[col] = LABEL_MAP[col_lower]
        else:
            new_columns[col] = col_lower

    df = df.rename(columns=new_columns)

    # Ensure required columns exist
    if "year" not in df.columns:
        # Try to find a column that looks like years
        for col in df.columns:
            if df[col].dtype == object:
                sample = df[col].dropna().head()
                if any(re.match(r'^\d{4}$', str(v).strip()) for v in sample):
                    df = df.rename(columns={col: "year"})
                    break

    if "revenue" not in df.columns:
        # Try first numeric column after year
        numeric_cols = [c for c in df.columns if c != "year"]
        if numeric_cols:
            df = df.rename(columns={numeric_cols[0]: "revenue"})

    if "profit" not in df.columns:
        numeric_cols = [c for c in df.columns if c not in ("year", "revenue")]
        if numeric_cols:
            df = df.rename(columns={numeric_cols[0]: "profit"})

    return df


def standardize(df):
    """
    Full cleaning pipeline:
    1. Clean values
    2. Normalize labels
    3. Ensure correct types
    """
    df = clean_dataframe(df)
    df = normalize_labels(df)

    # Keep only standard columns if they exist
    standard_cols = ["year", "revenue", "profit"]
    existing = [c for c in standard_cols if c in df.columns]
    if existing:
        df = df[existing]

    # Convert revenue and profit to numeric
    for col in ["revenue", "profit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Convert year to string
    if "year" in df.columns:
        df["year"] = df["year"].astype(str).str.strip()

    return df
