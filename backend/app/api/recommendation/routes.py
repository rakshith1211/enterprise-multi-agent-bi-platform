from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, RecHistoryResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()

@router.post("/generate", response_model=RecommendationResponse)
async def generate_prescriptive_recommendations(schema: RecommendationRequest, db: AsyncSession = Depends(get_db)):
    service = RecommendationService(db)
    return await service.generate(schema)

@router.get("/history", response_model=List[RecHistoryResponse])
async def list_recommendation_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = RecommendationService(db)
    return await service.get_history(skip, limit)

@router.get("/health")
def check_recommendation_health():
    return {"status": "healthy", "service": "Enterprise Recommendation Agent"}
