from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class VisualizationRequest(BaseModel):
    columns: List[str] = Field(..., description="Columns in the dataset")
    rows: List[Dict[str, Any]] = Field(..., description="Row data objects")
    preferred_chart_type: Optional[str] = Field(None, description="Line, Bar, Pie, Scatter, etc.")

class ChartRecommendation(BaseModel):
    chart_type: str
    confidence: float
    explanation: str

class AccessibilityMetadata(BaseModel):
    title: str
    description: str
    aria_label: str
    color_palette_hints: List[str]

class VisualizationResponse(BaseModel):
    id: uuid.UUID
    summary: Dict[str, Any]
    primary_recommendation: ChartRecommendation
    alternative_recommendations: List[ChartRecommendation]
    plotly_spec: Dict[str, Any]
    recharts_spec: Dict[str, Any]
    vega_lite_spec: Dict[str, Any]
    echarts_spec: Dict[str, Any]
    accessibility: AccessibilityMetadata
    created_at: datetime

    model_config = {"from_attributes": True}

class VisHistoryResponse(BaseModel):
    id: uuid.UUID
    input_summary: Dict[str, Any]
    chart_spec: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
