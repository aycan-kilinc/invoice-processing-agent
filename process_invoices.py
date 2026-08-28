"""
process_invoices.py

End-to-end pipeline:

    PDF invoices  --pdf_utils-->  raw text
                  --extractor -->  structured JSON (vendor, line items, total)
                  --validator -->  validated record (computed_total, status)
                  --this file-->  invoice_results.csv

Run:
    python process_invoices.py --input data/sample_invoices --output invoice_results.csv
"""

import argparse
import csv
import glob
import os

from dotenv import load_dotenv

from pdf_utils import extract_text
from extractor import extract_invoice_data
from validator import validate_invoice

load_dotenv()

CSV_FIELDS = [
    "file",
    "vendor",
    "invoice_number",
    "invoice_date",
    "computed_total",
    "stated_total",
    "status",
]


def process_folder(input_dir: str, output_csv: str) -> None:
    pdf_paths = sorted(glob.glob(os.path.join(input_dir, "*.pdf")))
    if not pdf_paths:
        print(f"No PDF files found in {input_dir}")
        return

    results = []
    for path in pdf_paths:
        filename = os.path.basename(path)
        print(f"Processing {filename}...")

        text = extract_text(path)
        data = extract_invoice_data(text)
        validated = validate_invoice(data)
        validated["file"] = filename
        results.append(validated)

        if validated["status"] == "DISCREPANCY":
            print(
                f"  DISCREPANCY: stated_total={validated.get('stated_total')} "
                f"vs computed_total={validated['computed_total']}"
            )

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. {len(results)} invoice(s) written to {output_csv}")


def main():
    parser = argparse.ArgumentParser(description="Extract and validate PDF invoices.")
    parser.add_argument("--input", default="data/sample_invoices", help="Folder of PDF invoices")
    parser.add_argument("--output", default="invoice_results.csv", help="Output CSV path")
    args = parser.parse_args()

    process_folder(args.input, args.output)


if __name__ == "__main__":
    main()
