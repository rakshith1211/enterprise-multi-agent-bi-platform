from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.query_execution import QueryExecutionHistory
from typing import List, Optional, Dict, Any
import uuid

class QueryExecutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: QueryExecutionHistory) -> QueryExecutionHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def list_history(self, skip: int = 0, limit: int = 100) -> List[QueryExecutionHistory]:
        res = await self.db.execute(
            select(QueryExecutionHistory)
            .order_by(QueryExecutionHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())

    async def get_metrics(self) -> Dict[str, Any]:
        # Aggregate performance metrics
        res = await self.db.execute(
            select(
                func.count(QueryExecutionHistory.id).label("total_queries"),
                func.avg(QueryExecutionHistory.execution_time_ms).label("avg_latency_ms"),
                func.sum(QueryExecutionHistory.row_count).label("total_rows_scanned"),
                func.sum(select(func.count(QueryExecutionHistory.id)).where(QueryExecutionHistory.status == "failed").scalar_subquery()).label("failed_queries")
            )
        )
        row = res.first()
        if not row or row[0] == 0:
            return {
                "total_queries": 0,
                "avg_latency_ms": 0.0,
                "total_rows_scanned": 0,
                "failed_queries": 0
            }
        return {
            "total_queries": row[0],
            "avg_latency_ms": float(row[1] or 0.0),
            "total_rows_scanned": int(row[2] or 0),
            "failed_queries": int(row[3] or 0)
        }
