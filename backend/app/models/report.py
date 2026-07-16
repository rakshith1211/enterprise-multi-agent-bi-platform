import uuid
from datetime import datetime
from sqlalchemy import DateTime, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class ReportHistory(Base):
    __tablename__ = "report_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    template: Mapped[str] = mapped_column(String(100), nullable=False)
    pdf_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    docx_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    pptx_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    html_content: Mapped[str] = mapped_column(Text, nullable=False)
    md_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
