import re


def validate_fact(fact: dict) -> tuple[bool, list[str]]:
    """
    Validate a candidate fact before it is stored as a trusted fact.

    Returns:
        (is_valid, reasons)
    """

    reasons = []

    # ---------------------------------------------------------
    # 1. Required fields
    # ---------------------------------------------------------
    if not fact.get("attribute"):
        reasons.append("missing_attribute")

    if not fact.get("value"):
        reasons.append("missing_value")

    if not fact.get("evidence_text"):
        reasons.append("missing_evidence")

    if reasons:
        return False, reasons

    value = str(fact["value"]).strip()
    evidence = str(fact["evidence_text"]).strip()

    # ---------------------------------------------------------
    # 2. Evidence should contain the extracted value
    # ---------------------------------------------------------
    normalized_value = value.replace(",", "")

    if value not in evidence and normalized_value not in evidence.replace(",", ""):
        reasons.append("value_not_found_in_evidence")

    # ---------------------------------------------------------
    # 3. Numeric facts should contain a numeric value
    # ---------------------------------------------------------
    fact_type = str(fact.get("fact_type") or "").lower()

    numeric_types = {
        "numerical",
        "percentage",
        "financial",
        "growth",
        "operational"
    }

    if fact_type in numeric_types:
        if fact.get("numeric_value") is None:
            reasons.append("missing_numeric_value")

    # ---------------------------------------------------------
    # 4. Reject obviously malformed numeric values
    # ---------------------------------------------------------
    if fact.get("numeric_value") is not None:
        try:
            number = float(fact["numeric_value"])

            if number != number:  # NaN check
                reasons.append("numeric_value_is_nan")

        except (TypeError, ValueError):
            reasons.append("invalid_numeric_value")

    # ---------------------------------------------------------
    # 5. Reject suspicious standalone percentage values
    # ---------------------------------------------------------
    if fact_type == "percentage":
        percentage_match = re.fullmatch(
            r"\s*\d{1,2}%\s*",
            value
        )

        if percentage_match:
            number = float(value.replace("%", "").strip())

            # Values such as 02% are usually OCR/table noise
            if value.strip().startswith("0") and number < 10:
                reasons.append("suspicious_percentage_format")

    # ---------------------------------------------------------
    # 6. Reject extremely short evidence
    # ---------------------------------------------------------
    if len(evidence) < 10:
        reasons.append("evidence_too_short")

    # ---------------------------------------------------------
    # 7. Reject obviously empty/junk attributes
    # ---------------------------------------------------------
    attribute = str(fact.get("attribute") or "").strip().lower()

    junk_attributes = {
        "",
        "unknown",
        "none",
        "null"
    }

    if attribute in junk_attributes:
        reasons.append("junk_attribute")

    # ---------------------------------------------------------
    # Final decision
    # ---------------------------------------------------------
    return len(reasons) == 0, reasons


def validate_facts(facts: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Validate a list of candidate facts.

    Returns:
        valid_facts, rejected_facts
    """

    valid_facts = []
    rejected_facts = []

    for fact in facts:
        is_valid, reasons = validate_fact(fact)

        if is_valid:
            valid_facts.append(fact)
        else:
            rejected = fact.copy()
            rejected["validation_reasons"] = reasons
            rejected_facts.append(rejected)

    return valid_facts, rejected_facts