from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class QueryPlanRequest(BaseModel):
    user_query: str = Field(..., description="The natural language question to plan.")
    connection_id: Optional[uuid.UUID] = Field(None, description="Optional target database connection ID.")

class DAGStep(BaseModel):
    step_id: str
    name: str
    agent: str # SQL, Analytics, Forecast, Visualization, Recommendation, Report
    depends_on: List[str] = []
    status: str = "pending"
    parameters: Dict[str, Any] = {}

class CostEstimate(BaseModel):
    sql_execution_ms: int = 0
    runtime_ms: int = 0
    llm_tokens: int = 0
    estimated_cost_usd: float = 0.0

class QueryPlanResponse(BaseModel):
    id: uuid.UUID
    user_query: str
    normalized_query: str
    business_domain: str
    intent: str # analytics, forecast, recommendation, visualization, report_generation, metadata_search
    complexity: str # Simple, Medium, Complex, Very Complex
    recommended_agent: str
    execution_steps: List[DAGStep]
    metrics: List[str]
    kpis: List[str]
    dimensions: List[str]
    filters: List[Dict[str, Any]]
    joins: List[str]
    relationships: List[str]
    visualization_hints: List[str]
    cost_estimate: CostEstimate
    clarification_requirements: List[str]
    explainability: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}

class PlanHistoryResponse(BaseModel):
    id: uuid.UUID
    user_query: str
    normalized_query: Optional[str]
    plan_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
