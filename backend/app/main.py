from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.chunks import router as chunks_router
from app.api.facts import router as facts_router

from app.models.database import Base, engine
from app.models import Document, Chunk, Fact

from app.api.qa import router as qa_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Superjoin Fact Knowledge Layer",
    description="Fact extraction and cross-document reasoning system",
    version="1.0.0"
)


app.include_router(upload_router)
app.include_router(chunks_router)
app.include_router(facts_router)
app.include_router(qa_router)


@app.get("/")
def root():
    return {
        "message": "Superjoin Fact Knowledge Layer API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }