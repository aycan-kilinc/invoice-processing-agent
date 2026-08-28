"""
generate_sample_invoices.py

Creates a few synthetic PDF invoices in data/sample_invoices/ so the
pipeline has something to run against out of the box. One invoice is
deliberately made to NOT add up, to demonstrate the discrepancy-flagging
behavior in validator.py.

Run once before process_invoices.py:
    python generate_sample_invoices.py
"""

import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUTPUT_DIR = "data/sample_invoices"


def make_invoice(filename, vendor, invoice_number, date, line_items, stated_total):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 72

    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, y, f"INVOICE - {vendor}")
    y -= 24

    c.setFont("Helvetica", 10)
    c.drawString(72, y, f"Invoice Number: {invoice_number}")
    y -= 16
    c.drawString(72, y, f"Date: {date}")
    y -= 28

    c.setFont("Helvetica-Bold", 10)
    c.drawString(72, y, "Description")
    c.drawString(320, y, "Qty")
    c.drawString(380, y, "Unit Price")
    y -= 16
    c.setFont("Helvetica", 10)

    for description, qty, unit_price in line_items:
        c.drawString(72, y, description)
        c.drawString(320, y, str(qty))
        c.drawString(380, y, f"${unit_price:.2f}")
        y -= 16

    y -= 12
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, y, f"Total: ${stated_total:.2f}")

    c.save()
    print(f"Created {path}")


def main():
    make_invoice(
        "invoice_001_clean.pdf",
        vendor="Northwind Office Supplies",
        invoice_number="NW-1042",
        date="2026-08-10",
        line_items=[
            ("Printer paper (box)", 5, 12.50),
            ("USB-C cables", 10, 6.00),
            ("Desk organizers", 3, 15.00),
        ],
        stated_total=167.50,  # matches: 5*12.50 + 10*6.00 + 3*15.00
    )

    make_invoice(
        "invoice_002_discrepancy.pdf",
        vendor="BrightLine Consulting",
        invoice_number="BL-2210",
        date="2026-08-14",
        line_items=[
            ("Consulting hours", 20, 85.00),
            ("Travel expenses", 1, 120.00),
        ],
        stated_total=1750.00,  # actual sum is 20*85 + 120 = 1820.00 -> discrepancy
    )

    make_invoice(
        "invoice_003_clean.pdf",
        vendor="Riga Print & Design",
        invoice_number="RPD-334",
        date="2026-08-20",
        line_items=[
            ("Business cards (500)", 1, 45.00),
            ("Banner printing", 2, 60.00),
        ],
        stated_total=165.00,  # matches: 45 + 2*60
    )


if __name__ == "__main__":
    main()
