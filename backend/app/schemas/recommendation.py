from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class RecommendationRequest(BaseModel):
    analytics_summary: Dict[str, Any] = Field(..., description="Metrics summaries, anomalies count, and KPIs")
    forecast_summary: Dict[str, Any] = Field(..., description="Forecasted metrics trends and model accuracy")
    business_rules: List[str] = Field(default=[], description="Active corporate policy rules and thresholds")

class RecommendationItem(BaseModel):
    title: str
    type: str # Revenue Optimization, Customer Retention, Cost Reduction, etc.
    priority: str # High, Medium, Low
    business_impact: str
    confidence: float
    reasoning: str
    affected_kpis: List[str]
    affected_departments: List[str]
    estimated_benefits: str
    estimated_risks: str
    suggested_actions: List[str]

class RecommendationResponse(BaseModel):
    id: uuid.UUID
    recommendations: List[RecommendationItem]
    created_at: datetime

    model_config = {"from_attributes": True}

class RecHistoryResponse(BaseModel):
    id: uuid.UUID
    input_summary: Dict[str, Any]
    recommendation_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
