from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.db.session import get_db
from app.schemas.analytics import AnalyticsRequest, AnalyticsResponse, AnalyticsHistoryResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.post("/analyze", response_model=AnalyticsResponse)
async def analyze_dataset_metrics(schema: AnalyticsRequest, db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.analyze_dataset(schema)

@router.get("/history", response_model=List[AnalyticsHistoryResponse])
async def list_analytics_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_history(skip, limit)

@router.get("/statistics")
async def get_quick_statistics(schema: AnalyticsRequest, db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    res = await service.analyze_dataset(schema)
    return res.statistics

@router.get("/kpis")
async def get_quick_kpis(schema: AnalyticsRequest, db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    res = await service.analyze_dataset(schema)
    return res.kpis

@router.get("/insights")
async def get_quick_insights(schema: AnalyticsRequest, db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    res = await service.analyze_dataset(schema)
    return res.insights

@router.get("/health")
def check_analytics_health():
    return {"status": "healthy", "service": "Enterprise Analytics Agent"}
