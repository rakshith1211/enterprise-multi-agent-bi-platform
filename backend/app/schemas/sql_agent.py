from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class SQLAgentRequest(BaseModel):
    query_plan_id: Optional[uuid.UUID] = None
    database_type: str = Field("postgresql", description="postgresql, mysql, mssql, oracle, sqlite, duckdb")
    metric: str
    aggregation: str = "SUM" # SUM, AVG, COUNT, MIN, MAX
    dimensions: List[str] = Field(default_factory=list)
    filters: List[Dict[str, Any]] = Field(default_factory=list)
    required_tables: List[str] = Field(..., min_length=1)
    required_columns: List[str] = Field(..., min_length=1)
    business_rules: List[str] = Field(default_factory=list)

class SQLAgentResponse(BaseModel):
    sql: str
    dialect: str
    parameters: Dict[str, Any]
    estimated_cost: Dict[str, Any]
    explainability: str
    validation_status: str

class SQLHistoryResponse(BaseModel):
    id: uuid.UUID
    query_plan_id: Optional[str]
    sql_query: str
    dialect: str
    parameters_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
