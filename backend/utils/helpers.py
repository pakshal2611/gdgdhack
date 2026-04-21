"""
Utility helper functions.
"""
import os
import uuid


def generate_unique_filename(original_filename):
    """Generate a unique filename preserving the extension."""
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4().hex}{ext}"


def get_file_extension(filename):
    """Get lowercase file extension."""
    return os.path.splitext(filename)[1].lower()


def is_supported_file(filename):
    """Check if the file type is supported."""
    supported = {".pdf", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
    return get_file_extension(filename) in supported


def safe_float(value, default=0.0):
    """Safely convert a value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def format_currency(value):
    """Format a number as currency string."""
    try:
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value):
    """Format a number as percentage string."""
    try:
        return f"{value:.2f}%"
    except (ValueError, TypeError):
        return str(value)
