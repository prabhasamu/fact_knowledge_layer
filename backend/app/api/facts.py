from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.chunk import Chunk
from app.models.fact import Fact
from app.services.fact_extractor import extract_candidate_facts

from app.services.fact_normalizer import normalize_fact


router = APIRouter(prefix="/facts", tags=["Facts"])


@router.post("/extract/{document_id}")
def extract_facts(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Extract facts from all chunks belonging to a document
    and save them into the facts table.
    """

    chunks = (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id)
        .order_by(Chunk.page_number, Chunk.chunk_index)
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail=f"No chunks found for document {document_id}"
        )

    # Remove previously extracted facts for this document.
    db.query(Fact).filter(
        Fact.document_id == document_id
    ).delete()

    db.commit()

    total_facts = 0

    for chunk in chunks:

        chunk_data = {
            "id": chunk.id,
            "page_number": chunk.page_number,
            "text": chunk.text
        }

        extracted_facts = extract_candidate_facts(chunk_data)

        for fact_data in extracted_facts:

            fact = Fact(
                document_id=document_id,
                chunk_id=fact_data["chunk_id"],
                page_number=fact_data["page_number"],
                entity=fact_data.get("entity"),
                attribute=fact_data["attribute"],
                value=fact_data["value"],
                numeric_value=fact_data.get("numeric_value"),
                unit=fact_data.get("unit"),
                period=fact_data.get("period"),
                scope=fact_data.get("scope"),
                fact_type=fact_data.get("fact_type"),
                evidence_text=fact_data["evidence_text"],
                confidence=fact_data.get("confidence")
            )

            db.add(fact)
            total_facts += 1

    db.commit()

    return {
        "document_id": document_id,
        "chunks_processed": len(chunks),
        "facts_extracted": total_facts,
        "status": "success"
    }


@router.get("/{document_id}")
def get_facts(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Return all extracted facts for a document.
    """

    facts = (
        db.query(Fact)
        .filter(Fact.document_id == document_id)
        .order_by(Fact.page_number, Fact.id)
        .all()
    )

    return {
        "document_id": document_id,
        "fact_count": len(facts),
        "facts": [
            {
                "id": fact.id,
                "document_id": fact.document_id,
                "chunk_id": fact.chunk_id,
                "page_number": fact.page_number,
                "entity": fact.entity,
                "attribute": fact.attribute,
                "value": fact.value,
                "numeric_value": fact.numeric_value,
                "unit": fact.unit,

                # Normalized values will be populated
                # by the normalization stage.
                "normalized_value": fact.normalized_value,
                "normalized_unit": fact.normalized_unit,

                "period": fact.period,
                "scope": fact.scope,
                "fact_type": fact.fact_type,
                "evidence_text": fact.evidence_text,
                "confidence": fact.confidence
            }
            for fact in facts
        ]
    }

@router.post("/normalize/{document_id}")
def normalize_facts(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Normalize all extracted numerical facts for a document.
    """

    facts = (
        db.query(Fact)
        .filter(Fact.document_id == document_id)
        .all()
    )

    if not facts:
        raise HTTPException(
            status_code=404,
            detail=f"No facts found for document {document_id}"
        )

    normalized_count = 0

    for fact in facts:

        normalized_value, normalized_unit = normalize_fact(
            fact.numeric_value,
            fact.unit,
            fact.attribute
        )

        fact.normalized_value = normalized_value
        fact.normalized_unit = normalized_unit

        normalized_count += 1

    db.commit()

    return {
        "document_id": document_id,
        "facts_processed": len(facts),
        "facts_normalized": normalized_count,
        "status": "success"
    }

@router.get("/search/{document_id}")
def search_facts(
    document_id: int,
    attribute: str = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(Fact)
        .filter(Fact.document_id == document_id)
    )

    if attribute:
        query = query.filter(
            Fact.attribute.ilike(f"%{attribute}%")
        )

    facts = (
        query
        .order_by(Fact.page_number, Fact.id)
        .all()
    )

    return {
        "document_id": document_id,
        "attribute": attribute,
        "fact_count": len(facts),
        "facts": [
            {
                "id": fact.id,
                "attribute": fact.attribute,
                "value": fact.value,
                "numeric_value": fact.numeric_value,
                "unit": fact.unit,
                "normalized_value": fact.normalized_value,
                "normalized_unit": fact.normalized_unit,
                "period": fact.period,
                "page_number": fact.page_number,
                "fact_type": fact.fact_type,
                "evidence_text": fact.evidence_text,
                "confidence": fact.confidence
            }
            for fact in facts
        ]
    }
