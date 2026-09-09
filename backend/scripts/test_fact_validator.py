import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.fact_validator import validate_fact


def test(name, fact):
    valid, reasons = validate_fact(fact)

    print("=" * 70)
    print(name)
    print("VALID:", valid)
    print("REASONS:", reasons)


def main():

    # ---------------------------------------------------------
    # Valid financial fact
    # ---------------------------------------------------------
    test(
        "Valid financial fact",
        {
            "attribute": "Fresh Issue Size",
            "value": "₹40,000 million",
            "numeric_value": 40000,
            "fact_type": "financial",
            "evidence_text": "The Fresh Issue Size is ₹40,000 million."
        }
    )

    # ---------------------------------------------------------
    # Valid percentage
    # ---------------------------------------------------------
    test(
        "Valid percentage",
        {
            "attribute": "Market Share",
            "value": "12.5%",
            "numeric_value": 12.5,
            "fact_type": "percentage",
            "evidence_text": "The company had a market share of 12.5%."
        }
    )

    # ---------------------------------------------------------
    # Missing numeric value
    # ---------------------------------------------------------
    test(
        "Missing numeric value",
        {
            "attribute": "Revenue",
            "value": "₹500 million",
            "numeric_value": None,
            "fact_type": "financial",
            "evidence_text": "Revenue was ₹500 million."
        }
    )

    # ---------------------------------------------------------
    # Value not present in evidence
    # ---------------------------------------------------------
    test(
        "Value missing from evidence",
        {
            "attribute": "Revenue",
            "value": "₹500 million",
            "numeric_value": 500,
            "fact_type": "financial",
            "evidence_text": "Revenue increased significantly."
        }
    )

    # ---------------------------------------------------------
    # Suspicious percentage
    # ---------------------------------------------------------
    test(
        "Suspicious percentage",
        {
            "attribute": "Numerical Metric",
            "value": "02%",
            "numeric_value": 2,
            "fact_type": "percentage",
            "evidence_text": "The value reported was 02%."
        }
    )

    # ---------------------------------------------------------
    # Entity can be None
    # ---------------------------------------------------------
    test(
        "Valid fact without entity",
        {
            "entity": None,
            "attribute": "Total Offer Size",
            "value": "₹52,350 million",
            "numeric_value": 52350,
            "fact_type": "financial",
            "evidence_text": "The Total Offer Size is ₹52,350 million."
        }
    )


if __name__ == "__main__":
    main()