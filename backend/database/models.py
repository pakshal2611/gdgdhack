"""
Database models — CRUD operations for MySQL tables.
"""
from database.db import get_connection


def insert_file(filename):
    """Insert a new file record and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO files (filename) VALUES (%s)",
        (filename,)
    )
    conn.commit()
    file_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return file_id


def insert_financial_data(file_id, year, revenue, profit):
    """Insert a financial data row."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO financial_data (file_id, year, revenue, profit) VALUES (%s, %s, %s, %s)",
        (file_id, year, revenue, profit)
    )
    conn.commit()
    cursor.close()
    conn.close()


def insert_financial_data_bulk(file_id, records):
    """Insert multiple financial data rows at once.
    records: list of dicts with keys: year, revenue, profit
    """
    conn = get_connection()
    cursor = conn.cursor()
    for record in records:
        cursor.execute(
            "INSERT INTO financial_data (file_id, year, revenue, profit) VALUES (%s, %s, %s, %s)",
            (file_id, record.get("year", ""), record.get("revenue", 0), record.get("profit", 0))
        )
    conn.commit()
    cursor.close()
    conn.close()


def insert_ratios(file_id, revenue_growth, profit_margin):
    """Insert or update ratios for a file."""
    conn = get_connection()
    cursor = conn.cursor()
    # Delete existing ratios for this file
    cursor.execute("DELETE FROM ratios WHERE file_id = %s", (file_id,))
    cursor.execute(
        "INSERT INTO ratios (file_id, revenue_growth, profit_margin) VALUES (%s, %s, %s)",
        (file_id, revenue_growth, profit_margin)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_financial_data(file_id):
    """Get all financial data for a file."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT year, revenue, profit FROM financial_data WHERE file_id = %s ORDER BY year",
        (file_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # Convert Decimal to float for JSON serialization
    for row in rows:
        row["revenue"] = float(row["revenue"]) if row["revenue"] else 0
        row["profit"] = float(row["profit"]) if row["profit"] else 0
    return rows


def get_ratios(file_id):
    """Get ratios for a file."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT revenue_growth, profit_margin FROM ratios WHERE file_id = %s",
        (file_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {
            "revenue_growth": float(row["revenue_growth"]) if row["revenue_growth"] else 0,
            "profit_margin": float(row["profit_margin"]) if row["profit_margin"] else 0,
        }
    return {"revenue_growth": 0, "profit_margin": 0}


def get_file(file_id):
    """Get file record by ID."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM files WHERE id = %s", (file_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_files():
    """Get all uploaded files."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM files ORDER BY upload_time DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
