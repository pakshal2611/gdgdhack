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
            "ratios": {"revenue_growth": 0, "profit_margin": 0},
            "trend": "No Data",
        }

    revenue_growth = calculate_revenue_growth(data)
    profit_margin = calculate_profit_margin(data)
    trend = detect_trend(data)

    # Store ratios in DB
    insert_ratios(file_id, revenue_growth, profit_margin)

    return {
        "data": data,
        "ratios": {
            "revenue_growth": revenue_growth,
            "profit_margin": profit_margin,
        },
        "trend": trend,
    }
