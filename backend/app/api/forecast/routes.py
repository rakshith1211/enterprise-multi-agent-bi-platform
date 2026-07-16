from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.forecast import ForecastRequest, ForecastResponse, ForecastHistoryResponse
from app.services.forecast_service import ForecastService

router = APIRouter()

@router.post("/predict", response_model=ForecastResponse)
async def generate_future_predictions(schema: ForecastRequest, db: AsyncSession = Depends(get_db)):
    service = ForecastService(db)
    return await service.predict(schema)

@router.get("/history", response_model=List[ForecastHistoryResponse])
async def list_forecast_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = ForecastService(db)
    return await service.get_history(skip, limit)

@router.get("/models")
def list_registered_forecasting_models():
    return {
        "models": [
            {"name": "ARIMA (1,1,0)", "type": "Statistical", "status": "active"},
            {"name": "Random Forest Regressor", "type": "Machine Learning", "status": "active"},
            {"name": "Prophet", "type": "Facebook Additive", "status": "inactive_fallback"}
        ]
    }

@router.get("/health")
def check_forecast_health():
    return {"status": "healthy", "service": "Enterprise Forecast Agent"}
