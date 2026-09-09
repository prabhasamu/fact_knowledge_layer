from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey

from app.models.database import Base


class Fact(Base):

    __tablename__ = "facts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False
    )

    chunk_id = Column(
        Integer,
        ForeignKey("chunks.id"),
        nullable=False
    )

    page_number = Column(
        Integer,
        nullable=False
    )

    entity = Column(
        String,
        nullable=True
    )

    attribute = Column(
        String,
        nullable=False
    )

    value = Column(
        Text,
        nullable=False
    )

    numeric_value = Column(
        Float,
        nullable=True
    )

    unit = Column(
        String,
        nullable=True
    )

    normalized_value = Column(
        Float,
        nullable=True
    )

    normalized_unit = Column(
        String,
        nullable=True
    )

    period = Column(
        String,
        nullable=True
    )

    scope = Column(
        String,
        nullable=True
    )

    fact_type = Column(
        String,
        nullable=True
    )

    evidence_text = Column(
        Text,
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=True
    )