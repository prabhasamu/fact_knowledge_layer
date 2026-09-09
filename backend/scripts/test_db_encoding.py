import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.database import SessionLocal
from app.models.fact import Fact


def main():
    db = SessionLocal()

    try:
        fact = Fact(
            document_id=1,
            chunk_id=1,
            page_number=100,
            entity="Test Entity",
            attribute="Test Amount",
            value="₹42.27 million",
            numeric_value=42.27,
            unit="INR million",
            period=None,
            scope=None,
            fact_type="financial",
            evidence_text="Test evidence ₹42.27 million",
            confidence=1.0
        )

        db.add(fact)
        db.commit()
        db.refresh(fact)

        print("=" * 80)
        print("DATABASE ENCODING TEST")
        print("=" * 80)

        print("ID:", fact.id)
        print("Value:", fact.value)
        print("Value repr:", repr(fact.value))
        print("Evidence:", fact.evidence_text)
        print("Evidence repr:", repr(fact.evidence_text))

        db.delete(fact)
        db.commit()

        print()
        print("Database encoding test completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()