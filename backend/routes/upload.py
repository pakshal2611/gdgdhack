"""
Upload route — handles file upload, extraction, cleaning, storage, and RAG indexing.
"""
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

from services.pdf_extractor import extract_data
from services.data_cleaner import standardize
from database.models import insert_file, insert_financial_data_bulk, get_financial_data
from services.rag_pipeline import build_rag_index
from utils.helpers import generate_unique_filename, is_supported_file

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a financial document (PDF, Excel, Image).
    Extracts data, cleans it, stores in MySQL, and builds RAG index.
    """
    # Validate file type
    if not is_supported_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Accepted: PDF, Excel (.xlsx/.xls/.csv), Images (.png/.jpg/.jpeg)"
        )

    try:
        # Save file to disk
        unique_name = generate_unique_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract data from file
        df, raw_text = extract_data(file_path, file.filename)

        # Clean and standardize
        df = standardize(df)

        # Store file record in DB
        file_id = insert_file(file.filename)

        # Store financial data in DB
        if not df.empty:
            records = df.to_dict(orient="records")
            insert_financial_data_bulk(file_id, records)

        # Build RAG index
        financial_data = get_financial_data(file_id)
        build_rag_index(file_id, financial_data, raw_text)

        # Clean up uploaded file (optional — keep for reference)
        # os.remove(file_path)

        return {
            "file_id": file_id,
            "message": "Upload successful",
            "filename": file.filename,
            "rows_extracted": len(df),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
