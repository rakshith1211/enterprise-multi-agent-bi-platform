from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.visualization import VisualizationRequest, VisualizationResponse, VisHistoryResponse
from app.services.visualization_service import VisualizationService

router = APIRouter()

@router.post("/spec", response_model=VisualizationResponse)
async def generate_chart_specification(schema: VisualizationRequest, db: AsyncSession = Depends(get_db)):
    service = VisualizationService(db)
    return await service.generate_spec(schema)

@router.get("/history", response_model=List[VisHistoryResponse])
async def list_visualization_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = VisualizationService(db)
    return await service.get_history(skip, limit)

@router.get("/health")
def check_visualization_health():
    return {"status": "healthy", "service": "Enterprise Visualization Agent"}
