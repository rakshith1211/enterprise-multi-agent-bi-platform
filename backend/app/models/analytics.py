import uuid
from datetime import datetime
from sqlalchemy import DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class AnalyticsHistory(Base):
    __tablename__ = "analytics_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    input_summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    analytics_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
