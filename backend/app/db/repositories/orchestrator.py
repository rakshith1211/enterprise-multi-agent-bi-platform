from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orchestrator import WorkflowHistory
from typing import List, Optional
import uuid

class WorkflowRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: WorkflowHistory) -> WorkflowHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get(self, workflow_id: uuid.UUID) -> Optional[WorkflowHistory]:
        res = await self.db.execute(
            select(WorkflowHistory).where(WorkflowHistory.id == workflow_id)
        )
        return res.scalar_one_or_none()

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[WorkflowHistory]:
        res = await self.db.execute(
            select(WorkflowHistory)
            .order_by(WorkflowHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
