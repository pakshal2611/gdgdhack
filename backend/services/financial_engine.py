"""
Financial analysis engine — calculates ratios and detects trends.
"""
from database.models import get_financial_data, insert_ratios


def calculate_revenue_growth(data):
    """
    Calculate year-over-year revenue growth.
    Returns the latest growth percentage.
    """
    if len(data) < 2:
        return 0.0

    revenues = [row["revenue"] for row in data if row["revenue"] > 0]
    if len(revenues) < 2:
        return 0.0

    prev = revenues[-2]
    curr = revenues[-1]

    if prev == 0:
        return 0.0

    growth = ((curr - prev) / prev) * 100
    return round(growth, 2)


def calculate_profit_margin(data):
    """
    Calculate the latest profit margin (profit / revenue * 100).
    """
    if not data:
        return 0.0

    latest = data[-1]
    revenue = latest.get("revenue", 0)
    profit = latest.get("profit", 0)

    if revenue == 0:
        return 0.0

    margin = (profit / revenue) * 100
    return round(margin, 2)


def detect_trend(data):
    """
    Detect the overall trend of revenue.
    Returns: 'Growing', 'Declining', or 'Stable'
    """
    if len(data) < 2:
        return "Insufficient Data"

    revenues = [row["revenue"] for row in data]

    # Calculate consecutive growth/decline
    increases = 0
    decreases = 0

    for i in range(1, len(revenues)):
        if revenues[i] > revenues[i - 1]:
            increases += 1
        elif revenues[i] < revenues[i - 1]:
            decreases += 1

    total = increases + decreases
    if total == 0:
        return "Stable"
    elif increases / total >= 0.6:
        return "Growing"
    elif decreases / total >= 0.6:
        return "Declining"
    else:
        return "Stable"


# ──────────────────────────────────────────────
# New ratio functions
# ──────────────────────────────────────────────

def calculate_ebitda_margin(data):
    """
    Calculate latest EBITDA margin: (ebitda / revenue) * 100.
    If ebitda is 0 for all rows, estimate as profit * 1.3 (rough proxy).
    Returns float rounded to 2 decimal places.
    """
    if not data:
        return 0.0

    latest = data[-1]
    revenue = latest.get("revenue", 0)
    ebitda = latest.get("ebitda", 0)

    # If ebitda is 0 for all rows, estimate from profit
    if all(row.get("ebitda", 0) == 0 for row in data):
        ebitda = latest.get("profit", 0) * 1.3

    if revenue == 0:
        return 0.0

    return round((ebitda / revenue) * 100, 2)


def calculate_debt_equity(data):
    """
    Calculate Debt-to-Equity ratio: total_liabilities / (total_assets - total_liabilities).
    Use the latest year's data.
    Return 0.0 if data is missing or denominator is zero.
    Returns float rounded to 2 decimal places.
    """
    if not data:
        return 0.0

    latest = data[-1]
    total_assets = latest.get("total_assets", 0)
    total_liabilities = latest.get("total_liabilities", 0)

    equity = total_assets - total_liabilities
    if equity == 0:
        return 0.0

    return round(total_liabilities / equity, 2)


def calculate_current_ratio(data):
    """
    Calculate Current Ratio: current_assets / current_liabilities.
    Use the latest year's data.
    Return 0.0 if data is missing or current_liabilities is zero.
    Returns float rounded to 2 decimal places.
    """
    if not data:
        return 0.0

    latest = data[-1]
    current_assets = latest.get("current_assets", 0)
    current_liabilities = latest.get("current_liabilities", 0)

    if current_liabilities == 0:
        return 0.0

    return round(current_assets / current_liabilities, 2)


def calculate_5yr_cagr(data):
    """
    Calculate 5-year CAGR of revenue: (last_revenue / first_revenue)^(1/n) - 1 * 100.
    n = number of years - 1.
    Use only rows where revenue > 0.
    Return 0.0 if fewer than 2 data points.
    Returns float percentage rounded to 2 decimal places.
    """
    positive = [row for row in data if row.get("revenue", 0) > 0]
    if len(positive) < 2:
        return 0.0

    first_revenue = positive[0]["revenue"]
    last_revenue = positive[-1]["revenue"]
    n = len(positive) - 1

    if first_revenue <= 0 or n == 0:
        return 0.0

    cagr = ((last_revenue / first_revenue) ** (1 / n) - 1) * 100
    return round(cagr, 2)


def calculate_avg_profit_margin(data):
    """
    Calculate average profit margin across all years.
    Returns float rounded to 2 decimal places.
    """
    margins = []
    for row in data:
        revenue = row.get("revenue", 0)
        profit = row.get("profit", 0)
        if revenue > 0:
            margins.append((profit / revenue) * 100)

    if not margins:
        return 0.0

    return round(sum(margins) / len(margins), 2)


def build_yoy_table(data):
    """
    Build year-over-year growth table.
    Returns list of dicts, each with:
      year, revenue, profit, revenue_growth_pct, profit_growth_pct, profit_margin_pct
    First year will have None for growth fields.
    """
    table = []
    for i, row in enumerate(data):
        entry = {
            "year": row.get("year"),
            "revenue": row.get("revenue", 0),
            "profit": row.get("profit", 0),
            "revenue_growth_pct": None,
            "profit_growth_pct": None,
            "profit_margin_pct": None,
        }

        revenue = row.get("revenue", 0)
        profit = row.get("profit", 0)

        # Profit margin for this year
        if revenue > 0:
            entry["profit_margin_pct"] = round((profit / revenue) * 100, 2)

        # YoY growth (skip first year)
        if i > 0:
            prev_rev = data[i - 1].get("revenue", 0)
            prev_profit = data[i - 1].get("profit", 0)

            if prev_rev > 0:
                entry["revenue_growth_pct"] = round(
                    ((revenue - prev_rev) / prev_rev) * 100, 2
                )
            if prev_profit > 0:
                entry["profit_growth_pct"] = round(
                    ((profit - prev_profit) / prev_profit) * 100, 2
                )

        table.append(entry)

    return table


def run_full_analysis(file_id):
    """
    Run complete financial analysis for a file.
    Calculates ratios, detects trend, stores in DB.
    Returns analysis results.
    """
    data = get_financial_data(file_id)

    if not data:
        return {
            "data": [],
            "ratios": {
                "revenue_growth": 0, "profit_margin": 0,
                "ebitda_margin": 0, "debt_equity": 0,
                "current_ratio": 0, "cagr_5yr": 0,
                "avg_profit_margin": 0,
            },
            "trend": "No Data",
            "yoy_growth": [],
        }

    revenue_growth = calculate_revenue_growth(data)
    profit_margin = calculate_profit_margin(data)
    ebitda_margin = calculate_ebitda_margin(data)
    debt_equity = calculate_debt_equity(data)
    current_ratio = calculate_current_ratio(data)
    cagr_5yr = calculate_5yr_cagr(data)
    avg_profit_margin = calculate_avg_profit_margin(data)
    trend = detect_trend(data)
    yoy_growth = build_yoy_table(data)

    # Store ratios in DB
    insert_ratios(
        file_id, revenue_growth, profit_margin,
        ebitda_margin=ebitda_margin,
        debt_equity=debt_equity,
        current_ratio=current_ratio,
        cagr_5yr=cagr_5yr,
        avg_profit_margin=avg_profit_margin,
    )

    return {
        "data": data,
        "ratios": {
            "revenue_growth": revenue_growth,
            "profit_margin": profit_margin,
            "ebitda_margin": ebitda_margin,
            "debt_equity": debt_equity,
            "current_ratio": current_ratio,
            "cagr_5yr": cagr_5yr,
            "avg_profit_margin": avg_profit_margin,
        },
        "trend": trend,
        "yoy_growth": yoy_growth,
    }
