from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ReportRequest(BaseModel):
    title: str = Field("Executive Business Intelligence Report", description="Title of the report")
    template: str = Field("Executive Report", description="Executive Report, Financial Report, etc.")
    analytics_data: Dict[str, Any] = Field(..., description="Analytics inputs")
    forecast_data: Dict[str, Any] = Field(..., description="Forecast inputs")
    visualization_metadata: Dict[str, Any] = Field(..., description="Visualization metadata")
    recommendations_data: Dict[str, Any] = Field(..., description="Recommendations list")

class ReportResponse(BaseModel):
    id: uuid.UUID
    title: str
    template_used: str
    formats_available: List[str]
    download_urls: Dict[str, str]
    created_at: datetime

    model_config = {"from_attributes": True}

class ReportHistoryResponse(BaseModel):
    id: uuid.UUID
    title: str
    template: str
    created_at: datetime

    model_config = {"from_attributes": True}
