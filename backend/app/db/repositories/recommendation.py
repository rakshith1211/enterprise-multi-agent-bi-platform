from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.recommendation import RecommendationHistory
from typing import List, Optional
import uuid

class RecommendationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: RecommendationHistory) -> RecommendationHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[RecommendationHistory]:
        res = await self.db.execute(
            select(RecommendationHistory)
            .order_by(RecommendationHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
