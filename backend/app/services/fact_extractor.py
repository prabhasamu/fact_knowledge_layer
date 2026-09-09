import re
import spacy


# ============================================================
# LOAD SPACY MODEL ONCE
# ============================================================

nlp = spacy.load("en_core_web_sm")


# ============================================================
# ATTRIBUTE KEYWORDS
# ============================================================

ATTRIBUTE_PATTERNS = {
    "revenue": [
        "revenue from operations",
        "total revenue",
        "income from operations",
        "revenue"
    ],

    "profit": [
        "profit after tax",
        "net profit",
        "profit"
    ],

    "loss": [
        "net loss",
        "loss"
    ],

    "ebitda": [
        "adjusted ebitda",
        "ebitda"
    ],

    "employees": [
        "number of employees",
        "employee count",
        "employees"
    ],

    "customers": [
        "customer base",
        "customers"
    ],

    "orders": [
        "shipments processed",
        "shipments",
        "orders"
    ],

    "market_share": [
        "market share"
    ],

    "fresh_issue": [
        "fresh issue"
    ],

    "offer_for_sale": [
        "offer for sale"
    ],

    "total_offer": [
        "total offer",
        "offer size"
    ]
}


# ============================================================
# PRE-COMPILE REGEX
# ============================================================

MONEY_PATTERN = re.compile(
    r"(₹\s?[\d,]+(?:\.\d+)?)\s*"
    r"(million|billion|crore|lakh)?",
    re.IGNORECASE
)

NUMBER_UNIT_PATTERN = re.compile(
    r"([\d,]+(?:\.\d+)?)\s*"
    r"(million|billion|crore|lakh)",
    re.IGNORECASE
)

PERCENT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*%",
    re.IGNORECASE
)

NUMBER_PATTERN = re.compile(
    r"(?<![\w])[\d,]+(?:\.\d+)?(?![\w])"
)

YEAR_PATTERN = re.compile(
    r"(?:FY\s?\d{2,4}(?:-\d{2,4})?"
    r"|20\d{2}(?:[-/]\d{2})?)",
    re.IGNORECASE
)


# ============================================================
# FIND ATTRIBUTE
# ============================================================

def find_attribute(sentence: str):

    text = sentence.lower()

    best_attribute = None
    best_position = len(text) + 1
    best_length = 0

    for attribute, keywords in ATTRIBUTE_PATTERNS.items():

        for keyword in keywords:

            position = text.find(keyword)

            if position != -1:

                # Prefer the earliest attribute.
                # If same position, prefer longer phrase.
                if (
                    position < best_position
                    or (
                        position == best_position
                        and len(keyword) > best_length
                    )
                ):
                    best_attribute = attribute
                    best_position = position
                    best_length = len(keyword)

    return best_attribute


# ============================================================
# FIND ATTRIBUTE POSITION
# ============================================================

def find_attribute_position(sentence: str, attribute: str):

    text = sentence.lower()

    positions = []

    for keyword in ATTRIBUTE_PATTERNS.get(attribute, []):

        position = text.find(keyword)

        if position != -1:
            positions.append(
                (position, len(keyword))
            )

    if not positions:
        return None

    return min(positions)


# ============================================================
# EXTRACT VALUE NEAR ATTRIBUTE
# ============================================================

def extract_value(sentence: str, attribute=None):

    # --------------------------------------------------------
    # Find attribute location
    # --------------------------------------------------------

    attribute_info = None

    if attribute:
        attribute_info = find_attribute_position(
            sentence,
            attribute
        )

    # --------------------------------------------------------
    # Find all numerical candidates
    # --------------------------------------------------------

    candidates = []

    # Currency values
    for match in MONEY_PATTERN.finditer(sentence):

        value = match.group(1)
        unit = match.group(2)

        # Ignore matches that contain no actual digits
        if not re.search(r"\d", value):
            continue

        numeric_value = value.replace(",", "")
        numeric_value = numeric_value.replace("₹", "").strip()

        try:
            numeric_value = float(numeric_value)
        except ValueError:
            continue

        candidates.append({
            "start": match.start(),
            "end": match.end(),
            "value": value,
            "numeric_value": numeric_value,
            "unit": unit
        })

    # Percentage values
    for match in PERCENT_PATTERN.finditer(sentence):

        value = match.group(1)

        try:
            numeric_value = float(value)
        except ValueError:
            continue

        candidates.append({
            "start": match.start(),
            "end": match.end(),
            "value": value,
            "numeric_value": numeric_value,
            "unit": "%"
        })

    # Numbers with units
    for match in NUMBER_UNIT_PATTERN.finditer(sentence):

        value = match.group(1)
        unit = match.group(2)

        try:
            numeric_value = float(
                value.replace(",", "")
            )
        except ValueError:
            continue

        candidates.append({
            "start": match.start(),
            "end": match.end(),
            "value": value,
            "numeric_value": numeric_value,
            "unit": unit
        })

    # Plain numbers
    for match in NUMBER_PATTERN.finditer(sentence):

        value = match.group(0)

        try:
            numeric_value = float(
                value.replace(",", "")
            )
        except ValueError:
            continue

        candidates.append({
            "start": match.start(),
            "end": match.end(),
            "value": value,
            "numeric_value": numeric_value,
            "unit": None
        })

    if not candidates:
        return None, None, None

    # --------------------------------------------------------
    # Remove duplicate numerical matches
    # --------------------------------------------------------

    unique = {}

    for candidate in candidates:

        key = (
            candidate["start"],
            candidate["end"]
        )

        unique[key] = candidate

    candidates = list(unique.values())

    # --------------------------------------------------------
    # Choose value closest to attribute
    # --------------------------------------------------------

    if attribute_info:

        attribute_start, attribute_length = attribute_info

        attribute_end = (
            attribute_start + attribute_length
        )

        def distance(candidate):

            if candidate["start"] >= attribute_end:
                return candidate["start"] - attribute_end

            if candidate["end"] <= attribute_start:
                return attribute_start - candidate["end"]

            return 0

        candidates.sort(
            key=distance
        )

        # Prefer a value occurring after the attribute
        after_attribute = [
            c for c in candidates
            if c["start"] >= attribute_end
        ]

        if after_attribute:

            candidates = after_attribute

    # --------------------------------------------------------
    # Select closest valid value
    # --------------------------------------------------------

    selected = candidates[0]

    return (
        selected["value"],
        selected["numeric_value"],
        selected["unit"]
    )


# ============================================================
# FIND PERIOD
# ============================================================

def extract_period(sentence: str):

    match = YEAR_PATTERN.search(sentence)

    if match:
        return match.group(0)

    return None


# ============================================================
# EXTRACT ENTITY FROM EXISTING SPACY DOC
# ============================================================

def extract_entity_from_doc(doc):

    for ent in doc.ents:

        if ent.label_ == "ORG":
            return ent.text

    return None


# ============================================================
# DETERMINE FACT TYPE
# ============================================================

def determine_fact_type(attribute):

    if attribute in {
        "revenue",
        "profit",
        "loss",
        "ebitda"
    }:
        return "financial"

    if attribute in {
        "fresh_issue",
        "offer_for_sale",
        "total_offer"
    }:
        return "offer"

    return "operational"


# ============================================================
# EXTRACT FACTS FROM CHUNK
# ============================================================

def extract_facts_from_chunk(
    chunk_text: str,
    page_number: int,
    chunk_id: int
):

    # Parse chunk only ONCE
    doc = nlp(chunk_text)

    facts = []

    for sentence in doc.sents:

        sentence_text = sentence.text.strip()

        if not sentence_text:
            continue

        # ----------------------------------------------------
        # ATTRIBUTE
        # ----------------------------------------------------

        attribute = find_attribute(
            sentence_text
        )

        if not attribute:
            continue

        # ----------------------------------------------------
        # VALUE
        # ----------------------------------------------------

        value, numeric_value, unit = extract_value(
            sentence_text,
            attribute
        )

        if value is None:
            continue

        # ----------------------------------------------------
        # PERIOD
        # ----------------------------------------------------

        period = extract_period(
            sentence_text
        )

        # ----------------------------------------------------
        # ENTITY
        # ----------------------------------------------------

        entity = extract_entity_from_doc(
            sentence
        )

        # ----------------------------------------------------
        # FACT TYPE
        # ----------------------------------------------------

        fact_type = determine_fact_type(
            attribute
        )

        # ----------------------------------------------------
        # CONFIDENCE
        # ----------------------------------------------------

        confidence = 0.85

        # Increase confidence when attribute and
        # numerical value occur close together.
        attribute_info = find_attribute_position(
            sentence_text,
            attribute
        )

        if attribute_info:

            attribute_start, attribute_length = attribute_info

            value_position = sentence_text.find(
                str(value)
            )

            if value_position != -1:

                distance = abs(
                    value_position -
                    (
                        attribute_start +
                        attribute_length
                    )
                )

                if distance <= 50:
                    confidence = 0.95

                elif distance <= 100:
                    confidence = 0.90

        # ----------------------------------------------------
        # SAVE FACT
        # ----------------------------------------------------

        facts.append({

            "document_id": None,

            "chunk_id": chunk_id,

            "page_number": page_number,

            "entity": entity,

            "attribute": attribute,

            "value": value,

            "numeric_value": numeric_value,

            "unit": unit,

            "period": period,

            "scope": None,

            "fact_type": fact_type,

            "evidence_text": sentence_text,

            "confidence": confidence
        })

    return facts


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def extract_candidate_facts(chunk_data):

    return extract_facts_from_chunk(
        chunk_text=chunk_data["text"],
        page_number=chunk_data["page_number"],
        chunk_id=chunk_data["id"]
    )