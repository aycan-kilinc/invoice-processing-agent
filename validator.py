"""
validator.py

Business-rule validation: does the invoice add up? Kept as plain Python
math rather than trusting the LLM to do arithmetic, since language models
are unreliable at exact sums. This is the same "ground the numbers in
code, not in the model" pattern used across this project.
"""

TOLERANCE = 0.01  # allow a cent of rounding error


def validate_invoice(data: dict) -> dict:
    """
    Compare the sum of line items to the invoice's stated total.

    Returns the original data plus two extra fields:
      - computed_total: float, sum of quantity * unit_price across line items
      - status: "OK" or "DISCREPANCY"
    """
    line_items = data.get("line_items") or []
    computed_total = sum(
        (item.get("quantity") or 0) * (item.get("unit_price") or 0)
        for item in line_items
    )

    stated_total = data.get("stated_total")
    if stated_total is None:
        status = "MISSING_TOTAL"
    elif abs(computed_total - stated_total) <= TOLERANCE:
        status = "OK"
    else:
        status = "DISCREPANCY"

    return {
        **data,
        "computed_total": round(computed_total, 2),
        "status": status,
    }
