"""
Analysis route — returns financial data, ratios, and AI insights.
"""
from fastapi import APIRouter, HTTPException

from services.financial_engine import run_full_analysis
from services.ai_insights import generate_insights
from database.models import get_file, get_all_files, get_anomalies

router = APIRouter()


@router.get("/analysis/{file_id}")
async def get_analysis(file_id: int):
    """
    Get financial analysis for a specific file.
    Includes: data, ratios, trend, AI insights, anomalies, and YoY growth.
    """
    # Verify file exists
    file_record = get_file(file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Run financial analysis
        analysis = run_full_analysis(file_id)

        # Generate AI insights
        insights = generate_insights(file_id)

        # Fetch anomalies
        anomalies = get_anomalies(file_id)

        return {
            "file_id": file_id,
            "filename": file_record.get("filename", ""),
            "data": analysis["data"],
            "ratios": analysis["ratios"],
            "trend": analysis["trend"],
            "insights": insights,
            "anomalies": anomalies,
            "yoy_growth": analysis.get("yoy_growth", []),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/files")
async def list_files():
    """List all uploaded files."""
    try:
        files = get_all_files()
        # Convert datetime objects to strings for JSON
        for f in files:
            if f.get("upload_time"):
                f["upload_time"] = str(f["upload_time"])
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
