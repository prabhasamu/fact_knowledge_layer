def normalize_fact(numeric_value, unit, attribute=None):
    """
    Convert extracted numerical values into standardized values.
    """

    if numeric_value is None:
        return None, None

    try:
        value = float(numeric_value)
    except (ValueError, TypeError):
        return None, None

    if unit is None:
        return value, None

    unit_clean = unit.lower().strip()

    # ----------------------------------------
    # PERCENTAGE
    # ----------------------------------------

    if unit_clean == "%":
        return value, "percent"

    # ----------------------------------------
    # MILLION
    # ----------------------------------------

    if unit_clean == "million":
        return value * 1_000_000, "INR"

    # ----------------------------------------
    # BILLION
    # ----------------------------------------

    if unit_clean == "billion":
        return value * 1_000_000_000, "INR"

    # ----------------------------------------
    # CRORE
    # ----------------------------------------

    if unit_clean == "crore":
        return value * 10_000_000, "INR"

    # ----------------------------------------
    # LAKH
    # ----------------------------------------

    if unit_clean == "lakh":
        return value * 100_000, "INR"

    # ----------------------------------------
    # UNKNOWN UNIT
    # ----------------------------------------

    return value, unit