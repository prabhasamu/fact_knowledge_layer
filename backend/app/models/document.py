from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.models.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    extracted_text_path = Column(String, nullable=True)

    page_count = Column(Integer, default=0)

    status = Column(String, default="uploaded")

    upload_date = Column(
        DateTime,
        default=datetime.utcnow
    )