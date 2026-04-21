"""
PDF, Excel, and Image data extraction service.
"""
import pdfplumber
import pandas as pd
from PIL import Image
import os


def extract_from_pdf(file_path):
    """
    Extract tables and text from a PDF file.
    Returns: (DataFrame, raw_text)
    """
    all_rows = []
    raw_text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            # Extract raw text for RAG
            text = page.extract_text()
            if text:
                raw_text_parts.append(text)

            # Extract tables
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:
                    # First row as header, rest as data
                    header = [str(cell).strip() if cell else "" for cell in table[0]]
                    for row in table[1:]:
                        row_data = {}
                        for i, cell in enumerate(row):
                            if i < len(header):
                                row_data[header[i]] = str(cell).strip() if cell else ""
                        if row_data:
                            all_rows.append(row_data)

    raw_text = "\n".join(raw_text_parts)

    if all_rows:
        df = pd.DataFrame(all_rows)
    else:
        # If no tables found, try to parse text into structured data
        df = _parse_text_to_dataframe(raw_text)

    return df, raw_text


def extract_from_excel(file_path):
    """
    Extract data from an Excel file.
    Returns: (DataFrame, raw_text)
    """
    df = pd.read_excel(file_path)
    raw_text = df.to_string()
    return df, raw_text


def extract_from_image(file_path):
    """
    Extract text from an image using OCR (pytesseract).
    Returns: (DataFrame, raw_text)
    """
    try:
        import pytesseract
        img = Image.open(file_path)
        raw_text = pytesseract.image_to_string(img)
        df = _parse_text_to_dataframe(raw_text)
        return df, raw_text
    except ImportError:
        # pytesseract not installed — return empty
        return pd.DataFrame(), "OCR not available (pytesseract not installed)"
    except Exception as e:
        return pd.DataFrame(), f"Image extraction error: {str(e)}"


def extract_data(file_path, filename):
    """
    Route to the correct extractor based on file extension.
    Returns: (DataFrame, raw_text)
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext in (".xlsx", ".xls", ".csv"):
        if ext == ".csv":
            df = pd.read_csv(file_path)
            return df, df.to_string()
        return extract_from_excel(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff"):
        return extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _parse_text_to_dataframe(text):
    """
    Attempt to parse unstructured text into a financial DataFrame.
    Looks for patterns like 'Year: 2023, Revenue: 1000, Profit: 200'
    or tabular text data.
    """
    import re

    rows = []
    lines = text.strip().split("\n")

    for line in lines:
        # Try to find year + numbers pattern
        # Match lines that contain a year (4 digits) followed by numbers
        year_match = re.search(r'(20\d{2}|19\d{2})', line)
        if year_match:
            numbers = re.findall(r'[\d,]+\.?\d*', line)
            # Filter out the year from numbers
            year = year_match.group(1)
            nums = [n.replace(",", "") for n in numbers if n != year and len(n) > 1]
            if len(nums) >= 2:
                rows.append({
                    "year": year,
                    "revenue": nums[0],
                    "profit": nums[1]
                })
            elif len(nums) == 1:
                rows.append({
                    "year": year,
                    "revenue": nums[0],
                    "profit": "0"
                })

    if rows:
        return pd.DataFrame(rows)
    return pd.DataFrame(columns=["year", "revenue", "profit"])
