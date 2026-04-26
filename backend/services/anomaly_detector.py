"""
Anomaly Detection — detects financial anomalies in data.
Covers: revenue spikes, margin compression, cash-flow mismatches.
"""
import statistics

from database.models import insert_anomalies


def detect_revenue_spikes(data):
    """
    Detect years where revenue changed by more than 30% vs previous year.
    For each such year, create an anomaly dict:
      { year, field: 'revenue', value: actual_value, expected_value: prev_year_value,
        deviation_pct: pct_change, severity: 'high' if >50% else 'medium',
        description: human-readable string explaining the spike or drop }
    Returns list of anomaly dicts.
    """
    anomalies = []
    for i in range(1, len(data)):
        prev_rev = data[i - 1].get("revenue", 0)
        curr_rev = data[i].get("revenue", 0)

        if prev_rev == 0:
            continue

        pct_change = ((curr_rev - prev_rev) / abs(prev_rev)) * 100

        if abs(pct_change) > 30:
            direction = "spike" if pct_change > 0 else "drop"
            severity = "high" if abs(pct_change) > 50 else "medium"
            anomalies.append({
                "year": data[i].get("year"),
                "field": "revenue",
                "value": curr_rev,
                "expected_value": prev_rev,
                "deviation_pct": round(pct_change, 2),
                "severity": severity,
                "description": (
                    f"Revenue {direction} of {abs(pct_change):.1f}% detected in year "
                    f"{data[i].get('year')} (from {prev_rev:,.2f} to {curr_rev:,.2f})."
                ),
            })

    return anomalies


def detect_margin_compression(data):
    """
    Detect years where profit margin dropped by more than 5 percentage points vs previous year.
    Create anomaly dicts with field: 'profit_margin', severity based on size of drop.
    Returns list of anomaly dicts.
    """
    anomalies = []
    for i in range(1, len(data)):
        prev_rev = data[i - 1].get("revenue", 0)
        curr_rev = data[i].get("revenue", 0)
        prev_profit = data[i - 1].get("profit", 0)
        curr_profit = data[i].get("profit", 0)

        if prev_rev == 0 or curr_rev == 0:
            continue

        prev_margin = (prev_profit / prev_rev) * 100
        curr_margin = (curr_profit / curr_rev) * 100
        margin_change = curr_margin - prev_margin

        if margin_change < -5:
            severity = "high" if margin_change < -15 else "medium"
            anomalies.append({
                "year": data[i].get("year"),
                "field": "profit_margin",
                "value": round(curr_margin, 2),
                "expected_value": round(prev_margin, 2),
                "deviation_pct": round(margin_change, 2),
                "severity": severity,
                "description": (
                    f"Profit margin compressed by {abs(margin_change):.1f} percentage points "
                    f"in year {data[i].get('year')} (from {prev_margin:.1f}% to {curr_margin:.1f}%)."
                ),
            })

    return anomalies


def detect_cashflow_mismatch(data):
    """
    Detect years where profit is positive but cash_flow is negative.
    This is a potential red flag.
    Create anomaly dicts with field: 'cash_flow', severity: 'high'.
    Returns list of anomaly dicts.
    """
    anomalies = []
    for row in data:
        profit = row.get("profit", 0)
        cash_flow = row.get("cash_flow", 0)

        if profit > 0 and cash_flow < 0:
            anomalies.append({
                "year": row.get("year"),
                "field": "cash_flow",
                "value": cash_flow,
                "expected_value": profit,
                "deviation_pct": round(((cash_flow - profit) / abs(profit)) * 100, 2) if profit != 0 else 0,
                "severity": "high",
                "description": (
                    f"Cash-flow mismatch in year {row.get('year')}: profit is positive "
                    f"({profit:,.2f}) but cash flow is negative ({cash_flow:,.2f}). "
                    f"This may indicate aggressive accrual accounting or working-capital issues."
                ),
            })

    return anomalies


def run_anomaly_detection(file_id, data):
    """
    Run all anomaly detectors on the financial data.
    Combine results from all three detectors.
    Call insert_anomalies(file_id, combined_list) from database.models.
    Return the combined anomalies list.
    """
    combined = []
    combined.extend(detect_revenue_spikes(data))
    combined.extend(detect_margin_compression(data))
    combined.extend(detect_cashflow_mismatch(data))

    if combined:
        insert_anomalies(file_id, combined)

    return combined
