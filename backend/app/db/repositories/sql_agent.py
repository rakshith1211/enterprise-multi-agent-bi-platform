from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.sql_agent import SQLAgentHistory
from typing import List, Optional
import uuid

class SQLAgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: SQLAgentHistory) -> SQLAgentHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[SQLAgentHistory]:
        res = await self.db.execute(
            select(SQLAgentHistory)
            .order_by(SQLAgentHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
