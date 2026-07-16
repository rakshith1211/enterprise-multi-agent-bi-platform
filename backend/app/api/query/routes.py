from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.db.session import get_db
from app.schemas.query_execution import (
    QueryExecutionRequest,
    QueryValidationRequest,
    NormalizedQueryResponse,
    ExecutionHistoryResponse
)
from app.services.query_execution_service import QueryExecutionService
from app.services.sql_validator import SQLValidator

router = APIRouter()

@router.post("/execute", response_model=NormalizedQueryResponse)
async def execute_sql_query(schema: QueryExecutionRequest, db: AsyncSession = Depends(get_db)):
    service = QueryExecutionService(db)
    return await service.execute_query(schema)

@router.post("/validate")
def validate_sql_syntax(schema: QueryValidationRequest):
    is_safe = SQLValidator.validate_safety(schema.sql)
    if not is_safe:
        return {"status": "failed", "error": "Query failed security syntax checks"}
    return {"status": "success", "message": "Query passed syntax safety validation"}

@router.get("/history", response_model=List[ExecutionHistoryResponse])
async def list_execution_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = QueryExecutionService(db)
    return await service.get_history(skip, limit)

@router.get("/metrics")
async def get_telemetry_metrics(db: AsyncSession = Depends(get_db)):
    service = QueryExecutionService(db)
    return await service.get_observability_metrics()

@router.get("/health")
def check_execution_health():
    return {"status": "healthy", "service": "SQL Validation & Query Execution Engine"}
