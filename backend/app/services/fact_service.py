from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.fact import Fact

from app.services.fact_extractor import (
    extract_facts_from_chunk
)


def extract_document_facts(
    document_id: int,
    db: Session
):

    chunks = (
        db.query(Chunk)
        .filter(
            Chunk.document_id == document_id
        )
        .order_by(
            Chunk.page_number,
            Chunk.chunk_index
        )
        .all()
    )

    total_facts = 0

    for chunk in chunks:

        facts = extract_facts_from_chunk(
            chunk.text,
            chunk.page_number,
            chunk.id
        )

        for fact_data in facts:

            fact = Fact(

                document_id=document_id,

                chunk_id=chunk.id,

                entity=fact_data["entity"],

                attribute=fact_data["attribute"],

                value=fact_data["value"],

                unit=fact_data["unit"],

                period=fact_data["period"],

                scope=fact_data["scope"],

                fact_type=fact_data["fact_type"],

                evidence_text=fact_data[
                    "evidence_text"
                ],

                page_number=fact_data[
                    "page_number"
                ],

                confidence=fact_data[
                    "confidence"
                ]
            )

            db.add(fact)

            total_facts += 1

    db.commit()

    return total_facts