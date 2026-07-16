from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class AnalyticsRequest(BaseModel):
    columns: List[str] = Field(..., description="List of dataset column headers.")
    rows: List[Dict[str, Any]] = Field(..., description="List of row data dicts.")

class KPIsResult(BaseModel):
    revenue: float = 0.0
    profit: float = 0.0
    growth_rate: float = 0.0
    average_order_value: float = 0.0
    gross_margin: float = 0.0
    net_margin: float = 0.0
    customer_count: int = 0
    churn_rate: float = 0.0
    roi: float = 0.0
    custom_kpis: Dict[str, float] = Field(default_factory=dict)

class DescriptiveStats(BaseModel):
    mean: float = 0.0
    median: float = 0.0
    mode: float = 0.0
    variance: float = 0.0
    std_dev: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0
    coefficient_of_variation: float = 0.0

class TrendResult(BaseModel):
    direction: str = "Flat" # Upward, Downward, Flat
    strength: float = 0.0
    cagr: float = 0.0
    moving_averages: List[float] = Field(default_factory=list)

class AnomalyItem(BaseModel):
    index: int
    column: str
    value: Any
    reason: str
    severity: str # High, Medium, Low
    confidence: float

class CorrelationMatrix(BaseModel):
    matrix: Dict[str, Dict[str, float]]
    ranked_relationships: List[str] = Field(default_factory=list)

class DataQualityResult(BaseModel):
    missing_count: int = 0
    null_percentage: float = 0.0
    duplicate_rows: int = 0
    completeness_score: float = 1.0
    uniqueness_score: float = 1.0

class BusinessInsight(BaseModel):
    title: str
    description: str
    priority: str # High, Medium, Low
    confidence: float
    business_impact: str

class AnalyticsResponse(BaseModel):
    id: uuid.UUID
    summary: Dict[str, Any]
    statistics: Dict[str, DescriptiveStats]
    trends: Dict[str, TrendResult]
    outliers: List[AnomalyItem] = Field(default_factory=list)
    correlations: CorrelationMatrix
    kpis: KPIsResult
    data_quality: DataQualityResult
    insights: List[BusinessInsight] = Field(default_factory=list)
    explainability: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}

class AnalyticsHistoryResponse(BaseModel):
    id: uuid.UUID
    input_summary: Dict[str, Any]
    analytics_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
