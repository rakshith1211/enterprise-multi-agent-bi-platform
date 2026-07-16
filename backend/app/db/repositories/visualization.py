from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.visualization import VisualizationHistory
from typing import List, Optional
import uuid

class VisualizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: VisualizationHistory) -> VisualizationHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[VisualizationHistory]:
        res = await self.db.execute(
            select(VisualizationHistory)
            .order_by(VisualizationHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
