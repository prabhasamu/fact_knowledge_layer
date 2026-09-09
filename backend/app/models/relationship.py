from sqlalchemy import Column, Integer, Text, Float, ForeignKey

from app.models.database import Base


class FactRelationship(Base):

    __tablename__ = "fact_relationships"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    fact_id_1 = Column(
        Integer,
        ForeignKey("facts.id"),
        nullable=False
    )

    fact_id_2 = Column(
        Integer,
        ForeignKey("facts.id"),
        nullable=False
    )

    relationship_type = Column(
        Text,
        nullable=False
    )

    explanation = Column(
        Text,
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=True
    )