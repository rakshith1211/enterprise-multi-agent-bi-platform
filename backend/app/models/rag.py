import uuid
from datetime import datetime
from sqlalchemy import DateTime, JSON, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class RAGDocumentHistory(Base):
    __tablename__ = "rag_document_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_name: Mapped[str] = mapped_column(String(250), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    doc_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    chunks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
