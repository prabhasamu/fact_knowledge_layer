from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.chunk import Chunk


router = APIRouter(
    prefix="/chunks",
    tags=["Chunks"]
)


@router.get("/{document_id}")
def get_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):

    chunks = (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id)
        .order_by(
            Chunk.page_number,
            Chunk.chunk_index
        )
        .all()
    )

    return {
        "document_id": document_id,
        "chunk_count": len(chunks),
        "chunks": [
            {
                "id": chunk.id,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text
            }
            for chunk in chunks
        ]
    }