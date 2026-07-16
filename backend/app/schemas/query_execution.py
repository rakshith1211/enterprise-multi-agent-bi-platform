from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class QueryExecutionRequest(BaseModel):
    sql: str = Field(..., description="The SELECT query to execute.")
    connection_id: uuid.UUID = Field(..., description="Target database connection profile ID.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameter variables.")
    timeout_seconds: int = Field(30, description="Execution timeout limit in seconds.")

class QueryValidationRequest(BaseModel):
    sql: str = Field(..., description="SQL query string to validate.")

class NormalizedQueryResponse(BaseModel):
    columns: List[str]
    data_types: Dict[str, str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float
    warnings: List[str] = []
    metadata: Dict[str, Any]

class ExecutionHistoryResponse(BaseModel):
    id: uuid.UUID
    sql_query: str
    connection_id: str
    execution_time_ms: float
    row_count: int
    status: str
    error: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
