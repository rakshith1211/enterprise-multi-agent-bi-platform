from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ForecastRequest(BaseModel):
    history_dates: List[str] = Field(..., description="List of ISO date strings representing timestamps.")
    history_values: List[float] = Field(..., description="List of corresponding metric values.")
    horizon: int = Field(12, description="Number of periods to forecast into the future.")

class AccuracyMetrics(BaseModel):
    mape: float
    rmse: float
    mae: float

class PredictionPoint(BaseModel):
    date: str
    value: float
    upper_bound: float
    lower_bound: float

class ForecastResponse(BaseModel):
    id: uuid.UUID
    forecast_values: List[PredictionPoint]
    trend: str # Increasing, Decreasing, Flat
    seasonality: str # Monthly, Quarterly, None
    model_used: str
    accuracy_metrics: AccuracyMetrics
    business_explanation: str
    confidence_score: float
    created_at: datetime

    model_config = {"from_attributes": True}

class ForecastHistoryResponse(BaseModel):
    id: uuid.UUID
    input_summary: Dict[str, Any]
    forecast_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
