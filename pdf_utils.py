"""
pdf_utils.py

Small helper for pulling raw text out of a PDF invoice. Kept separate
from extractor.py so the "read the file" concern is isolated from the
"understand the file" concern.
"""

import pdfplumber


def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF file, page by page."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)
