"""
Export route — generates Excel reports.
"""
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import openpyxl

from database.models import get_file, get_financial_data, get_ratios

router = APIRouter()


@router.get("/export/{file_id}")
async def export_excel(file_id: int):
    """
    Export financial data and ratios as an Excel file.
    Sheet1: Raw Data
    Sheet2: Ratios
    """
    # Verify file exists
    file_record = get_file(file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        data = get_financial_data(file_id)
        ratios = get_ratios(file_id)

        # Create workbook
        wb = openpyxl.Workbook()

        # Sheet 1: Raw Data
        ws1 = wb.active
        ws1.title = "Raw Data"

        # Header styling
        header_font = openpyxl.styles.Font(bold=True, color="FFFFFF")
        header_fill = openpyxl.styles.PatternFill(start_color="1a1a2e", end_color="1a1a2e", fill_type="solid")

        headers = ["Year", "Revenue", "Profit"]
        for col, header in enumerate(headers, 1):
            cell = ws1.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill

        for i, row in enumerate(data, 2):
            ws1.cell(row=i, column=1, value=row.get("year", ""))
            ws1.cell(row=i, column=2, value=row.get("revenue", 0))
            ws1.cell(row=i, column=3, value=row.get("profit", 0))

        # Auto-width columns
        for col in ws1.columns:
            max_length = max(len(str(cell.value or "")) for cell in col)
            ws1.column_dimensions[col[0].column_letter].width = max_length + 4

        # Sheet 2: Ratios
        ws2 = wb.create_sheet("Ratios")
        ratio_headers = ["Metric", "Value"]
        for col, header in enumerate(ratio_headers, 1):
            cell = ws2.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill

        ws2.cell(row=2, column=1, value="Revenue Growth (%)")
        ws2.cell(row=2, column=2, value=ratios.get("revenue_growth", 0))
        ws2.cell(row=3, column=1, value="Profit Margin (%)")
        ws2.cell(row=3, column=2, value=ratios.get("profit_margin", 0))

        for col in ws2.columns:
            max_length = max(len(str(cell.value or "")) for cell in col)
            ws2.column_dimensions[col[0].column_letter].width = max_length + 4

        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        filename = file_record.get("filename", "report").replace(".", "_")

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}_report.xlsx"'
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
