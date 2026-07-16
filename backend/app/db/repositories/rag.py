from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.rag import RAGDocumentHistory
from typing import List, Optional
import uuid

class RAGRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: RAGDocumentHistory) -> RAGDocumentHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_by_name(self, doc_name: str) -> Optional[RAGDocumentHistory]:
        res = await self.db.execute(
            select(RAGDocumentHistory)
            .where(RAGDocumentHistory.document_name == doc_name)
            .order_by(RAGDocumentHistory.doc_version.desc())
            .limit(1)
        )
        return res.scalar_one_or_none()

    async def delete(self, doc_id: uuid.UUID) -> bool:
        doc = await self.db.execute(
            select(RAGDocumentHistory).where(RAGDocumentHistory.id == doc_id)
        )
        history = doc.scalar_one_or_none()
        if history:
            await self.db.delete(history)
            await self.db.commit()
            return True
        return False

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[RAGDocumentHistory]:
        res = await self.db.execute(
            select(RAGDocumentHistory)
            .order_by(RAGDocumentHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
