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
    (and optionally expenses, ebitda, total_assets, total_liabilities,
     current_assets, current_liabilities, cash_flow)
    """
    conn = get_connection()
    cursor = conn.cursor()
    for record in records:
        cursor.execute(
            """INSERT INTO financial_data
               (file_id, year, revenue, profit, expenses, ebitda,
                total_assets, total_liabilities, current_assets,
                current_liabilities, cash_flow)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                file_id,
                record.get("year", ""),
                record.get("revenue", 0),
                record.get("profit", 0),
                record.get("expenses", 0),
                record.get("ebitda", 0),
                record.get("total_assets", 0),
                record.get("total_liabilities", 0),
                record.get("current_assets", 0),
                record.get("current_liabilities", 0),
                record.get("cash_flow", 0),
            )
        )
    conn.commit()
    cursor.close()
    conn.close()


def insert_ratios(file_id, revenue_growth, profit_margin,
                  ebitda_margin=0, debt_equity=0, current_ratio=0,
                  cagr_5yr=0, avg_profit_margin=0):
    """Insert or update ratios for a file."""
    conn = get_connection()
    cursor = conn.cursor()
    # Delete existing ratios for this file
    cursor.execute("DELETE FROM ratios WHERE file_id = %s", (file_id,))
    cursor.execute(
        """INSERT INTO ratios
           (file_id, revenue_growth, profit_margin, ebitda_margin,
            debt_equity, current_ratio, cagr_5yr, avg_profit_margin)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (file_id, revenue_growth, profit_margin, ebitda_margin,
         debt_equity, current_ratio, cagr_5yr, avg_profit_margin)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_financial_data(file_id):
    """Get all financial data for a file."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT year, revenue, profit, expenses, ebitda,
                  total_assets, total_liabilities, current_assets,
                  current_liabilities, cash_flow
           FROM financial_data WHERE file_id = %s ORDER BY year""",
        (file_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # Convert Decimal to float for JSON serialization
    decimal_fields = [
        "revenue", "profit", "expenses", "ebitda",
        "total_assets", "total_liabilities", "current_assets",
        "current_liabilities", "cash_flow",
    ]
    for row in rows:
        for field in decimal_fields:
            row[field] = float(row[field]) if row.get(field) else 0.0
    return rows


def get_ratios(file_id):
    """Get ratios for a file."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT revenue_growth, profit_margin, ebitda_margin,
                  debt_equity, current_ratio, cagr_5yr, avg_profit_margin
           FROM ratios WHERE file_id = %s""",
        (file_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {k: float(v) if v else 0.0 for k, v in row.items()}
    return {
        "revenue_growth": 0, "profit_margin": 0, "ebitda_margin": 0,
        "debt_equity": 0, "current_ratio": 0, "cagr_5yr": 0,
        "avg_profit_margin": 0,
    }


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


# ──────────────────────────────────────────────
# Anomalies CRUD
# ──────────────────────────────────────────────

def insert_anomalies(file_id, anomalies_list):
    """Insert a list of anomaly dicts into the anomalies table.

    anomalies_list: list of dicts with keys:
        year, field, value, expected_value, deviation_pct, severity, description
    Returns number of rows inserted.
    """
    if not anomalies_list:
        return 0

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        count = 0
        for a in anomalies_list:
            cursor.execute(
                """INSERT INTO anomalies
                   (file_id, year, field, value, expected_value,
                    deviation_pct, severity, description)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    file_id,
                    a.get("year"),
                    a.get("field"),
                    a.get("value"),
                    a.get("expected_value"),
                    a.get("deviation_pct"),
                    a.get("severity", "medium"),
                    a.get("description", ""),
                )
            )
            count += 1
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        print(f"[ERROR] insert_anomalies failed: {e}")
        return 0
    finally:
        if conn:
            conn.close()


def get_anomalies(file_id):
    """Fetch all anomalies for a file_id. Return list of dicts."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT year, field, value, expected_value,
                      deviation_pct, severity, description
               FROM anomalies WHERE file_id = %s ORDER BY year""",
            (file_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        # Convert Decimal values to float for JSON serialization
        for row in rows:
            for key in ("value", "expected_value", "deviation_pct"):
                if row.get(key) is not None:
                    row[key] = float(row[key])
        return rows
    except Exception as e:
        print(f"[ERROR] get_anomalies failed: {e}")
        return []
    finally:
        if conn:
            conn.close()


# ──────────────────────────────────────────────
# Chat History CRUD
# ──────────────────────────────────────────────

def insert_chat_message(file_id, role, content):
    """Insert a single chat message. role is 'user' or 'assistant'."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO chat_history (file_id, role, content)
               VALUES (%s, %s, %s)""",
            (file_id, role, content)
        )
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"[ERROR] insert_chat_message failed: {e}")
    finally:
        if conn:
            conn.close()


def get_chat_history(file_id):
    """Fetch full chat history for a file_id ordered by created_at ASC.
    Return list of dicts with role and content.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT role, content, created_at
               FROM chat_history WHERE file_id = %s
               ORDER BY created_at ASC""",
            (file_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        # Convert datetime to string for JSON
        for row in rows:
            if row.get("created_at"):
                row["created_at"] = str(row["created_at"])
        return rows
    except Exception as e:
        print(f"[ERROR] get_chat_history failed: {e}")
        return []
    finally:
        if conn:
            conn.close()
