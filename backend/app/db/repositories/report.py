from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.report import ReportHistory
from typing import List, Optional
import uuid

class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: ReportHistory) -> ReportHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get(self, report_id: uuid.UUID) -> Optional[ReportHistory]:
        res = await self.db.execute(
            select(ReportHistory).where(ReportHistory.id == report_id)
        )
        return res.scalar_one_or_none()

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[ReportHistory]:
        res = await self.db.execute(
            select(ReportHistory)
            .order_by(ReportHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
