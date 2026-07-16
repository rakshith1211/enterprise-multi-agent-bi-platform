from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.analytics import AnalyticsHistory
from typing import List, Optional
import uuid

class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: AnalyticsHistory) -> AnalyticsHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[AnalyticsHistory]:
        res = await self.db.execute(
            select(AnalyticsHistory)
            .order_by(AnalyticsHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
