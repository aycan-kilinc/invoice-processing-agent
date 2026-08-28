# Invoice Processing Agent (Intelligent Document Processing)

A small agent that reads PDF invoices, pulls out the structured data a
finance team actually cares about (vendor, date, line items, total), and
checks the math — flagging any invoice where the line items don't add up
to the stated total.

## Why

Manually re-adding invoice line items to catch billing errors is slow and
easy to skip under deadline pressure. This project automates that check:
point it at a folder of PDF invoices and get back a clean CSV with every
invoice's totals verified and any discrepancies flagged for review.

## How it works

```
PDF invoices
     │
     ▼
pdf_utils.py  ───────►  extractor.py  ───────►  validator.py  ───────►  CSV
(extract raw text)      (LLM turns text          (sums line items,       (one row per
                          into structured           compares to           invoice, with
                          JSON: vendor, line         stated total)         a status column)
                          items, total)
```

1. `pdf_utils.py` extracts the raw text from each PDF using `pdfplumber`.
2. `extractor.py` sends that text to an LLM with a prompt asking for a
   strict JSON shape: vendor, invoice number, date, line items, and the
   stated total.
3. `validator.py` computes `sum(quantity * unit_price)` across the line
   items in plain Python — not trusting the model to do arithmetic — and
   compares it to the stated total.
4. `process_invoices.py` ties it together: process every PDF in a folder,
   print any discrepancies as they're found, and write everything to a
   CSV with a `status` column (`OK`, `DISCREPANCY`, or `MISSING_TOTAL`).

Grounding the math in code instead of the model is the same pattern used
in my [AI Reporting Assistant](https://github.com/aycan-kilinc/ai-reporting-assistant)
project — LLMs are good at reading messy text, less reliable at exact sums.

## Tech stack

- **Python** — core language
- **pdfplumber** — PDF text extraction
- **OpenAI API** — Generative AI / structured data extraction
- **reportlab** — generates the sample invoice PDFs used for testing
- **python-dotenv** — local secrets management

## Setup

```bash
git clone https://github.com/aycan-kilinc/invoice-processing-agent.git
cd invoice-processing-agent
pip install -r requirements.txt

cp .env.example .env
# then edit .env with your OpenAI API key

# generate a few sample invoices to test against
python generate_sample_invoices.py

# run the pipeline
python process_invoices.py --input data/sample_invoices --output invoice_results.csv
```

## Usage

```bash
python process_invoices.py --input <folder-of-pdfs> --output <results.csv>
```

Sample output (`invoice_results.csv`):

| file | vendor | invoice_number | invoice_date | computed_total | stated_total | status |
|---|---|---|---|---|---|---|
| invoice_001_clean.pdf | Northwind Office Supplies | NW-1042 | 2026-08-10 | 167.50 | 167.50 | OK |
| invoice_002_discrepancy.pdf | BrightLine Consulting | BL-2210 | 2026-08-14 | 1820.00 | 1750.00 | DISCREPANCY |
| invoice_003_clean.pdf | Riga Print & Design | RPD-334 | 2026-08-20 | 165.00 | 165.00 | OK |

## Project structure

```
invoice-processing-agent/
├── process_invoices.py         # Orchestrator: PDF folder -> validated CSV
├── extractor.py                 # LLM prompt + structured JSON extraction
├── validator.py                 # Line-item sum vs. stated total, in plain Python
├── pdf_utils.py                  # Raw text extraction from PDFs
├── generate_sample_invoices.py   # Creates demo invoice PDFs for testing
├── requirements.txt
├── .env.example
└── README.md
```

## Possible extensions

- Swap the CSV output for a direct write into an accounting/ERP system
- Add OCR (e.g. Tesseract) to handle scanned, non-text PDFs
- Extend validation to check tax calculations or currency mismatches
- Wrap this as a Power Automate or Copilot Studio action for a no-code front end

## Background

Built as a hands-on exercise in Intelligent Document Processing (IDP)
while preparing for Accenture's Agentic & Intelligent Automation Bootcamp
— applying the same "ground the numbers in code, let the LLM handle the
messy text" pattern from my Telegram reporting agent to a document-based
workflow.
