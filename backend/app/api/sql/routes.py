from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import uuid

from app.db.session import get_db
from app.schemas.sql_agent import SQLAgentRequest, SQLAgentResponse, SQLHistoryResponse
from app.services.sql_agent_service import SQLAgentService
from app.services.sql_validator import SQLValidator

router = APIRouter()

@router.post("/generate", response_model=SQLAgentResponse)
async def generate_sql_query(schema: SQLAgentRequest, db: AsyncSession = Depends(get_db)):
    service = SQLAgentService(db)
    return await service.generate_sql(schema)

@router.post("/validate")
def validate_sql_query(payload: Dict[str, str]):
    sql = payload.get("sql", "")
    if not sql:
        raise HTTPException(status_code=400, detail="Missing 'sql' string in payload")
    
    is_safe = SQLValidator.validate_safety(sql)
    if not is_safe:
        return {"status": "failed", "error": "Query failed SELECT-only security guardrails"}
    return {"status": "success", "message": "Query passed security checks"}

@router.get("/history", response_model=List[SQLHistoryResponse])
async def list_sql_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = SQLAgentService(db)
    return await service.get_history(skip, limit)

@router.get("/explain")
def explain_sql_compilation(dialect: str, sql: str):
    # Mock explanation endpoint
    return {
        "sql": sql,
        "dialect": dialect,
        "explanation": f"Formatted identifiers using {dialect} quoting. Validated syntax against standard SQL SELECT AST rules."
    }

@router.get("/health")
def check_sql_agent_health():
    return {"status": "healthy", "service": "SQL Agent Engine"}
