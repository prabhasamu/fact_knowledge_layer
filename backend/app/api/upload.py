from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from pathlib import Path
import shutil
import uuid

from app.services.pdf_extractor import extract_text_from_pdf
from app.services.chunker import create_chunks

from app.models.database import get_db
from app.models.document import Document
from app.models.chunk import Chunk


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# ============================================================
# DIRECTORIES
# ============================================================

UPLOAD_DIR = Path("data/uploads")
EXTRACTED_DIR = Path("data/extracted")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

EXTRACTED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# UPLOAD PDF
# ============================================================

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # ========================================================
    # 1. VALIDATE FILE
    # ========================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    original_filename = Path(file.filename).name

    if not original_filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )


    # ========================================================
    # 2. GENERATE SAFE UNIQUE FILENAME
    # ========================================================

    unique_id = uuid.uuid4().hex[:12]

    safe_filename = (
        f"{unique_id}_{original_filename}"
    )

    pdf_path = UPLOAD_DIR / safe_filename


    # ========================================================
    # 3. SAVE UPLOADED PDF
    # ========================================================

    try:

        with open(pdf_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save PDF: {str(e)}"
        )

    finally:

        await file.close()


    # ========================================================
    # 4. EXTRACT TEXT FROM PDF
    # ========================================================

    try:

        pages = extract_text_from_pdf(
            str(pdf_path)
        )

    except Exception as e:

        # Remove uploaded file if extraction fails

        if pdf_path.exists():
            pdf_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"PDF extraction failed: {str(e)}"
        )


    # ========================================================
    # 5. VALIDATE EXTRACTED CONTENT
    # ========================================================

    if not pages:

        if pdf_path.exists():
            pdf_path.unlink()

        raise HTTPException(
            status_code=400,
            detail="No pages could be extracted from the PDF."
        )


    # Count pages containing actual text

    pages_with_text = sum(
        1
        for page in pages
        if page.get("text", "").strip()
    )


    # ========================================================
    # 6. CREATE CHUNKS
    # ========================================================

    try:

        chunks = create_chunks(
            pages,
            chunk_size=1500,
            chunk_overlap=200
        )

    except Exception as e:

        if pdf_path.exists():
            pdf_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Chunk creation failed: {str(e)}"
        )


    # ========================================================
    # 7. VALIDATE CHUNKS
    # ========================================================

    if not chunks:

        if pdf_path.exists():
            pdf_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=(
                "No text chunks could be created. "
                "The PDF may contain scanned images "
                "or unsupported content."
            )
        )


    # ========================================================
    # 8. SAVE EXTRACTED TEXT
    # ========================================================

    extracted_filename = (
        f"{pdf_path.stem}.txt"
    )

    extracted_file = (
        EXTRACTED_DIR / extracted_filename
    )


    try:

        with open(
            extracted_file,
            "w",
            encoding="utf-8"
        ) as f:

            for page in pages:

                page_number = page["page_number"]

                text = page.get(
                    "text",
                    ""
                )

                f.write(
                    f"\n========== PAGE "
                    f"{page_number} "
                    f"==========\n"
                )

                f.write(text)

                f.write("\n")

    except Exception as e:

        if pdf_path.exists():
            pdf_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save extracted text: {str(e)}"
            )
        )


    # ========================================================
    # 9. CREATE DOCUMENT DATABASE RECORD
    # ========================================================

    document = Document(

        filename=original_filename,

        file_path=str(pdf_path),

        extracted_text_path=str(
            extracted_file
        ),

        page_count=len(pages),

        status="processing"
    )


    try:

        db.add(document)

        db.flush()

        # At this point document.id is available.

        # ====================================================
        # 10. SAVE CHUNKS
        # ====================================================

        for chunk_data in chunks:

            chunk = Chunk(

                document_id=document.id,

                page_number=chunk_data[
                    "page_number"
                ],

                chunk_index=chunk_data[
                    "chunk_index"
                ],

                text=chunk_data[
                    "text"
                ]
            )

            db.add(chunk)


        # ====================================================
        # 11. UPDATE DOCUMENT STATUS
        # ====================================================

        document.status = "processed"

        db.commit()

        db.refresh(document)


    except Exception as e:

        db.rollback()

        # Clean up generated files

        if pdf_path.exists():
            pdf_path.unlink()

        if extracted_file.exists():
            extracted_file.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save document and chunks: {str(e)}"
            )
        )


    # ========================================================
    # 12. RETURN PROCESSING RESULT
    # ========================================================

    return {

        "message":
            "PDF uploaded and processed successfully",

        "document_id":
            document.id,

        "filename":
            document.filename,

        "pages":
            document.page_count,

        "pages_with_text":
            pages_with_text,

        "chunks":
            len(chunks),

        "chunk_size":
            1500,

        "chunk_overlap":
            200,

        "status":
            document.status,

        "pdf_file":
            document.file_path,

        "extracted_text_file":
            document.extracted_text_path
    }


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@router.get("/")
def get_documents(
    db: Session = Depends(get_db)
):

    documents = (
        db.query(Document)
        .order_by(Document.id)
        .all()
    )

    return [

        {
            "id": document.id,

            "filename":
                document.filename,

            "page_count":
                document.page_count,

            "status":
                document.status,

            "file_path":
                document.file_path,

            "extracted_text_path":
                document.extracted_text_path,

            "upload_date":
                document.upload_date
        }

        for document in documents
    ]