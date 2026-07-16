from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class WorkflowRequest(BaseModel):
    user_query: str = Field(..., description="Natural language question to analyze")
    connection_id: uuid.UUID = Field(..., description="Target database connection ID")
    generate_report: bool = Field(False, description="Generate downloadable PDF/DOCX report")

class WorkflowResponse(BaseModel):
    id: uuid.UUID
    status: str
    trace: List[str]
    sql: Optional[str] = None
    query_results: Optional[Dict[str, Any]] = None
    analytics: Optional[Dict[str, Any]] = None
    visualization: Optional[Dict[str, Any]] = None
    forecast: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}

class WorkflowHistoryResponse(BaseModel):
    id: uuid.UUID
    user_query: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
