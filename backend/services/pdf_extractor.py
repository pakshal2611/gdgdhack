"""
PDF, Excel, and Image data extraction service.
Uses Tesseract OCR for scanned PDFs and images.
"""
import pdfplumber
import pandas as pd
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import os
import re
import platform

# ── Configure Tesseract path ──────────────────────────────────────────────────
# On Windows the installer does NOT always add tesseract to PATH.
# We set the path explicitly so pytesseract can always find it.
if platform.system() == "Windows":
    _TESSERACT_PATHS = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR", "tesseract.exe"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for _path in _TESSERACT_PATHS:
        if os.path.isfile(_path):
            pytesseract.pytesseract.tesseract_cmd = _path
            print(f"[OCR] Tesseract found at: {_path}")
            break
    else:
        print("[OCR] WARNING: Tesseract not found in common locations. OCR may fail.")


def _preprocess_image_for_ocr(img):
    """
    Preprocess an image to improve OCR accuracy.
    - Convert to grayscale
    - Scale up aggressively for small images
    - Increase contrast
    - Apply sharpening
    """
    # Convert to grayscale
    img = img.convert("L")

    # Scale up small images — OCR needs ~300 DPI equivalent.
    # Financial statements in screenshots are usually 72-96 DPI,
    # so we scale 3-4x to reach ~300 DPI.
    width, height = img.size
    if width < 2000:
        scale = max(3, 2500 // width)  # Target at least 2500px wide
        img = img.resize((width * scale, height * scale), Image.LANCZOS)
        print(f"[OCR] Scaled image from {width}x{height} to {img.width}x{img.height} ({scale}x)")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)

    return img


def _ocr_image(img):
    """
    Run Tesseract OCR on a PIL Image with optimized config.
    Returns extracted text string.
    """
    # Preprocess
    processed = _preprocess_image_for_ocr(img)

    # Try multiple PSM modes and pick the one with most text
    configs = [
        r"--oem 3 --psm 6",   # Assume uniform block of text
        r"--oem 3 --psm 4",   # Assume single column of variable sizes
        r"--oem 3 --psm 3",   # Fully automatic
    ]

    best_text = ""
    for config in configs:
        try:
            text = pytesseract.image_to_string(processed, config=config)
            if len(text.strip()) > len(best_text.strip()):
                best_text = text
        except Exception:
            continue

    return best_text


def extract_from_pdf(file_path):
    """
    Extract tables and text from a PDF file.
    Falls back to OCR for scanned PDFs (image-based pages).
    Returns: (DataFrame, raw_text)
    """
    all_rows = []
    raw_text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # ── Step 1: Try native text extraction ──
            text = page.extract_text()
            if text and text.strip():
                raw_text_parts.append(text)

            # ── Step 2: Try native table extraction ──
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:
                    header = [str(cell).strip() if cell else "" for cell in table[0]]
                    for row in table[1:]:
                        row_data = {}
                        for i, cell in enumerate(row):
                            if i < len(header):
                                row_data[header[i]] = str(cell).strip() if cell else ""
                        if row_data:
                            all_rows.append(row_data)

            # ── Step 3: If no text found, the page is likely a scanned image → OCR ──
            if not text or not text.strip():
                print(f"[OCR] Page {page_num + 1}: No embedded text found, running OCR...")
                try:
                    page_image = page.to_image(resolution=300)
                    pil_img = page_image.original
                    ocr_text = _ocr_image(pil_img)
                    if ocr_text and ocr_text.strip():
                        raw_text_parts.append(ocr_text)
                        print(f"[OCR] Page {page_num + 1}: Extracted {len(ocr_text)} characters via OCR")
                    else:
                        print(f"[OCR] Page {page_num + 1}: OCR returned no text")
                except Exception as e:
                    print(f"[OCR] Page {page_num + 1}: OCR failed — {str(e)}")

    raw_text = "\n".join(raw_text_parts)

    if all_rows:
        df = pd.DataFrame(all_rows)
    else:
        # If no tables found, try to parse the extracted text into structured data
        df = _parse_financial_statement(raw_text)

    print(f"[Extractor] PDF result: {len(df)} rows, {len(raw_text)} chars of text")
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
    Extract text from an image using Tesseract OCR.
    Returns: (DataFrame, raw_text)
    """
    try:
        img = Image.open(file_path)
        raw_text = _ocr_image(img)

        if not raw_text or not raw_text.strip():
            print(f"[OCR] Image '{file_path}': No text detected")
            return pd.DataFrame(), "No text could be extracted from image."

        print(f"[OCR] Image: Extracted {len(raw_text)} characters")
        print(f"[OCR] Preview:\n{raw_text[:300]}")

        df = _parse_financial_statement(raw_text)
        return df, raw_text

    except Exception as e:
        print(f"[OCR] Image extraction error: {str(e)}")
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


# ──────────────────────────────────────────────────────────────────────────────
# Intelligent Financial Statement Parser
# ──────────────────────────────────────────────────────────────────────────────

def _clean_number(s):
    """
    Convert a string like '(157,219)', '$97,603', '890,884' to a float.
    Parentheses denote negative values. Removes $, ₹, €, £, commas.
    Returns None if not a number.
    """
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    if not s or s in ("*", "^", "-", "—", "–", ","):
        return None

    negative = False
    # Handle parenthesized negatives: (123) → -123
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1]
    # Handle partial parens from OCR: (123 or 123)
    elif s.startswith("("):
        negative = True
        s = s[1:]
    elif s.endswith(")"):
        negative = True
        s = s[:-1]

    # Remove currency symbols, commas, spaces
    s = re.sub(r'[₹$€£,\s]', '', s)

    # Handle periods used as thousands separator (European) vs decimal
    # If pattern is like 157.219 (3 digits after dot), it's likely thousands sep
    if re.match(r'^\d+\.\d{3}$', s):
        s = s.replace('.', '')

    try:
        val = float(s)
        return -val if negative else val
    except ValueError:
        return None


def _detect_year_columns(header_lines):
    """
    Detect which columns correspond to which years from header lines.
    Returns a list of year labels found (e.g., ['2024', '2025', '2025', '2024', '2025', '2025'])
    """
    years = []
    for line in header_lines:
        found = re.findall(r'\b(19\d{2}|20\d{2})\b', line)
        if found:
            years.extend(found)
    return years


def _parse_financial_statement(text):
    """
    Intelligent parser for financial statements (income statements,
    balance sheets, etc.) extracted via OCR.

    Handles multi-column layouts like:
        Revenues  222,083  225,042  2,634  897,603  890,884  10,428

    Returns a DataFrame with columns: year, revenue, profit
    (extracted from the yearly/quarterly data)
    """
    if not text or not text.strip():
        return pd.DataFrame(columns=["year", "revenue", "profit"])

    lines = text.strip().split("\n")
    lines = [l.strip() for l in lines if l.strip()]

    # ── Step 1: Detect what kind of document this is ──
    full_text_lower = text.lower()
    is_income_statement = any(kw in full_text_lower for kw in [
        "statement of income", "income statement", "profit and loss",
        "p&l", "revenue", "profit for the period", "profit before tax",
        "cost of revenue", "gross profit", "operating"
    ])

    # ── Step 2: Find year headers ──
    # Look for lines that contain multiple years (e.g., "2024  2025  2025  2024  2025  2025")
    header_zone = lines[:15]  # Years are usually in the first 15 lines
    years = _detect_year_columns(header_zone)
    print(f"[Parser] Detected years in headers: {years}")

    # ── Step 3: If this is an income statement, parse line items ──
    if is_income_statement and years:
        return _parse_income_statement(lines, years)

    # ── Step 4: Fallback — try simple year+numbers per line ──
    return _parse_simple_rows(lines)


def _parse_income_statement(lines, header_years):
    """
    Parse a multi-column income statement.
    Extracts key financial metrics (Revenue, Profit, etc.) across year columns.
    """
    # Determine unique years and their column positions
    # Usually the columns repeat: Q3-2024, Q3-2025, Q3-2025(USD), FY-2024, FY-2025, FY-2025(USD)
    # We want the main currency columns (not USD convenience translations)

    # Key line items to look for
    key_items = {
        "revenue": [r"^revenues?\b", r"^total revenue", r"^net sales", r"^total sales", r"^turnover", r"^total income"],
        "cost_of_revenue": [r"^cost of revenue"],
        "gross_profit": [r"^gross profit"],
        "operating_profit": [r"^results from operating", r"^operating (profit|income)"],
        "profit_before_tax": [r"^profit before tax", r"^income before tax"],
        "tax": [r"^income tax", r"^tax expense", r"^provision for"],
        "net_profit": [r"^profit for the (period|year)", r"^net (profit|income)$", r"^net (profit|income) for"],
    }

    extracted = {}  # item_name -> list of numbers from the line

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        # Check if this line matches any key item
        for item_name, patterns in key_items.items():
            for pattern in patterns:
                # Match the label at the start, then extract numbers after it
                if re.search(pattern, line_clean, re.IGNORECASE):
                    # Extract all number-like tokens from the line
                    # Numbers can be: 222,083  (157,219)  $97,603  3.197  -1,820
                    tokens = re.findall(
                        r'\([\d,.\s]+\)|[\-]?[\$₹€£]?[\d,]+\.?\d*',
                        line_clean
                    )
                    nums = []
                    for t in tokens:
                        val = _clean_number(t)
                        if val is not None:
                            nums.append(val)

                    if nums and item_name not in extracted:
                        extracted[item_name] = nums
                        print(f"[Parser] {item_name}: {nums}")
                    break  # Don't match multiple patterns for same line

    if not extracted:
        print("[Parser] No key financial items matched — falling back to simple parser")
        return _parse_simple_rows(lines)

    # ── Build the DataFrame ──
    # Determine the unique year periods
    # header_years example: ['2024', '2025', '2025', '2024', '2025', '2025']
    # Usually: [Q-2024, Q-2025, Q-2025-USD, FY-2024, FY-2025, FY-2025-USD]
    unique_years = sorted(set(header_years))
    num_year_cols = len(header_years)
    print(f"[Parser] {num_year_cols} year columns detected, unique years: {unique_years}")

    # Determine which columns to use based on number of columns
    # For a 6-column layout: cols 0,3 = 2024, cols 1,4 = 2025, cols 2,5 = USD
    # We prefer yearly data (cols 3,4) over quarterly (cols 0,1)
    # But we adapt to whatever we find

    rows = []

    if num_year_cols == 6 and len(unique_years) == 2:
        # Typical: Q-Y1, Q-Y2, Q-Y2-USD, FY-Y1, FY-Y2, FY-Y2-USD
        # Use columns index 3 (FY-Y1) and 4 (FY-Y2) for yearly data
        year_labels = [f"FY {unique_years[0]}", f"FY {unique_years[1]}"]
        col_indices = [3, 4]  # FY columns

        # Also include quarterly as separate rows
        q_year_labels = [f"Q4 {unique_years[0]}", f"Q4 {unique_years[1]}"]
        q_col_indices = [0, 1]

        # Build yearly rows
        for idx, (label, col_idx) in enumerate(zip(year_labels, col_indices)):
            revenue = _safe_get(extracted.get("revenue", []), col_idx, 0)
            profit = _safe_get(extracted.get("net_profit", []), col_idx,
                        _safe_get(extracted.get("profit_before_tax", []), col_idx, 0))
            rows.append({
                "year": label,
                "revenue": abs(revenue),  # Revenue should be positive
                "profit": profit,
            })

        # Build quarterly rows
        for idx, (label, col_idx) in enumerate(zip(q_year_labels, q_col_indices)):
            revenue = _safe_get(extracted.get("revenue", []), col_idx, 0)
            profit = _safe_get(extracted.get("net_profit", []), col_idx,
                        _safe_get(extracted.get("profit_before_tax", []), col_idx, 0))
            rows.append({
                "year": label,
                "revenue": abs(revenue),
                "profit": profit,
            })

    elif num_year_cols >= 2:
        # General case: use first occurrence of each unique year
        for i, year in enumerate(unique_years):
            # Find the first column index for this year
            col_idx = header_years.index(year)
            revenue = _safe_get(extracted.get("revenue", []), col_idx, 0)
            profit = _safe_get(extracted.get("net_profit", []), col_idx,
                        _safe_get(extracted.get("profit_before_tax", []), col_idx, 0))
            rows.append({
                "year": year,
                "revenue": abs(revenue),
                "profit": profit,
            })
    else:
        # Single year — just use the first numbers found
        revenue = _safe_get(extracted.get("revenue", []), 0, 0)
        profit = _safe_get(extracted.get("net_profit", []), 0,
                    _safe_get(extracted.get("profit_before_tax", []), 0, 0))
        year = unique_years[0] if unique_years else "N/A"
        rows.append({
            "year": year,
            "revenue": abs(revenue),
            "profit": profit,
        })

    if rows:
        df = pd.DataFrame(rows)
        print(f"[Parser] Extracted financial data:\n{df}")
        return df

    return pd.DataFrame(columns=["year", "revenue", "profit"])


def _parse_simple_rows(lines):
    """
    Fallback parser for simple formats where each line has a year + numbers.
    Handles formats like:
        2021  45000  8000
        Year 2022: Revenue 52000, Profit 11000
    """
    rows = []

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        year_match = re.search(r'(20\d{2}|19\d{2})', line_clean)
        if year_match:
            year = year_match.group(1)
            # Don't treat header lines as data rows
            # If the line has multiple years, skip it (it's likely a header)
            all_years = re.findall(r'\b(20\d{2}|19\d{2})\b', line_clean)
            if len(all_years) > 1:
                continue

            # Extract numbers
            numbers = re.findall(r'[\d,]+\.?\d*', line_clean)
            nums = [n.replace(",", "") for n in numbers if n != year and len(n) > 1]

            if len(nums) >= 2:
                rows.append({
                    "year": year,
                    "revenue": nums[0],
                    "profit": nums[1],
                })
            elif len(nums) == 1:
                rows.append({
                    "year": year,
                    "revenue": nums[0],
                    "profit": "0",
                })

    if rows:
        return pd.DataFrame(rows)

    return pd.DataFrame(columns=["year", "revenue", "profit"])


def _safe_get(lst, index, default=0):
    """Safely get an item from a list by index."""
    if lst and 0 <= index < len(lst):
        return lst[index]
    return default
