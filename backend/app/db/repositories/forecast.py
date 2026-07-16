from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.forecast import ForecastHistory
from typing import List, Optional
import uuid

class ForecastRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: ForecastHistory) -> ForecastHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[ForecastHistory]:
        res = await self.db.execute(
            select(ForecastHistory)
            .order_by(ForecastHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
