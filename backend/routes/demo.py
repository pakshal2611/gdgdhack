"""
Demo route — seeds synthetic financial data for instant demo without uploading a file.
"""
from fastapi import APIRouter, HTTPException
from database.models import get_all_files, insert_file, insert_financial_data_bulk
from services.financial_engine import run_full_analysis
from services.anomaly_detector import run_anomaly_detection
from services.rag_pipeline import build_rag_index

router = APIRouter()

DEMO_FILENAME = "demo_company.pdf"

DEMO_DATA = [
    {
        "year": "2019",
        "revenue": 45000000, "profit": 5400000, "expenses": 35000000,
        "ebitda": 9000000, "total_assets": 60000000, "total_liabilities": 25000000,
        "current_assets": 18000000, "current_liabilities": 10000000, "cash_flow": 4500000,
    },
    {
        "year": "2020",
        "revenue": 41000000, "profit": 3280000, "expenses": 33000000,
        "ebitda": 7380000, "total_assets": 58000000, "total_liabilities": 27000000,
        "current_assets": 16000000, "current_liabilities": 11000000, "cash_flow": 2800000,
    },
    {
        "year": "2021",
        "revenue": 52000000, "profit": 7280000, "expenses": 40000000,
        "ebitda": 10400000, "total_assets": 70000000, "total_liabilities": 28000000,
        "current_assets": 22000000, "current_liabilities": 12000000, "cash_flow": 6500000,
    },
    {
        "year": "2022",
        "revenue": 63000000, "profit": 10080000, "expenses": 47000000,
        "ebitda": 12600000, "total_assets": 85000000, "total_liabilities": 30000000,
        "current_assets": 28000000, "current_liabilities": 13000000, "cash_flow": 9200000,
    },
    {
        "year": "2023",
        "revenue": 71000000, "profit": 12780000, "expenses": 52000000,
        "ebitda": 14200000, "total_assets": 98000000, "total_liabilities": 32000000,
        "current_assets": 34000000, "current_liabilities": 14000000, "cash_flow": 11500000,
    },
]


@router.post("/demo")
async def load_demo():
    """
    Load synthetic demo data for TechCorp India Ltd (2019-2023).
    Idempotent: returns existing file_id if demo already seeded.
    """
    try:
        # Check if demo already exists
        all_files = get_all_files()
        for f in all_files:
            if f.get("filename") == DEMO_FILENAME:
                return {"file_id": f["id"], "message": "Demo data loaded"}

        # Create file record
        file_id = insert_file(DEMO_FILENAME)

        # Insert financial data
        insert_financial_data_bulk(file_id, DEMO_DATA)

        # Run full financial analysis (computes ratios, stores in DB)
        result = run_full_analysis(file_id)

        # Run anomaly detection
        run_anomaly_detection(file_id, result.get("data", DEMO_DATA))

        # Build RAG index for chat
        build_rag_index(file_id, result.get("data", DEMO_DATA), "")

        return {"file_id": file_id, "message": "Demo data loaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo setup failed: {str(e)}")
