from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.planner import QueryPlanHistory
from typing import List, Optional
import uuid

class PlannerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: QueryPlanHistory) -> QueryPlanHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_by_id(self, id: uuid.UUID) -> Optional[QueryPlanHistory]:
        res = await self.db.execute(select(QueryPlanHistory).where(QueryPlanHistory.id == id))
        return res.scalars().first()

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[QueryPlanHistory]:
        res = await self.db.execute(
            select(QueryPlanHistory)
            .order_by(QueryPlanHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
