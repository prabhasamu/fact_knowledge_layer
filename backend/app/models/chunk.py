from sqlalchemy import Column, Integer, Text, ForeignKey

from app.models.database import Base


class Chunk(Base):

    __tablename__ = "chunks"

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

    page_number = Column(
        Integer,
        nullable=False
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    text = Column(
        Text,
        nullable=False
    )