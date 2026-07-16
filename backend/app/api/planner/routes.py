from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.planner import QueryPlanRequest, QueryPlanResponse, PlanHistoryResponse
from app.services.query_planner import QueryPlannerService

router = APIRouter()

@router.post("/plan", response_model=QueryPlanResponse)
async def generate_query_plan(schema: QueryPlanRequest, db: AsyncSession = Depends(get_db)):
    service = QueryPlannerService(db)
    return await service.generate_plan(schema)

@router.get("/history", response_model=List[PlanHistoryResponse])
async def list_plan_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = QueryPlannerService(db)
    return await service.get_history(skip, limit)

@router.get("/health")
def check_planner_health():
    return {"status": "healthy", "service": "Query Planning Engine"}
