"""
extractor.py

Turns raw invoice text into structured data using a Generative AI model.
The model is asked to return strict JSON so the rest of the pipeline can
work with a predictable schema instead of parsing free text with regex.
"""

import json
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EXTRACTION_PROMPT = """You are an invoice data extraction agent.

Read the invoice text below and return ONLY a JSON object with this exact
shape (no markdown, no commentary):

{{
  "vendor": string,
  "invoice_date": string,
  "invoice_number": string,
  "line_items": [
    {{"description": string, "quantity": number, "unit_price": number}}
  ],
  "stated_total": number
}}

Rules:
- "stated_total" is the total amount printed on the invoice.
- If a field is missing from the text, use null.
- Numbers must be plain numbers, not strings, and not currency symbols.

Invoice text:
---
{invoice_text}
---
"""


def extract_invoice_data(invoice_text: str, model: str = "gpt-4o-mini") -> dict:
    """Call the LLM and parse its JSON response into a Python dict."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": EXTRACTION_PROMPT.format(invoice_text=invoice_text)},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return json.loads(raw)
