from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.db.session import get_db
from app.schemas.orchestrator import WorkflowRequest, WorkflowResponse, WorkflowHistoryResponse
from app.services.orchestrator_service import OrchestratorService

router = APIRouter()

@router.post("/run", response_model=WorkflowResponse)
async def run_langgraph_workflow(schema: WorkflowRequest, db: AsyncSession = Depends(get_db)):
    service = OrchestratorService(db)
    return await service.run_workflow(schema)

@router.post("/chat", response_model=WorkflowResponse)
async def conversation_chat_interface(schema: WorkflowRequest, db: AsyncSession = Depends(get_db)):
    # Chat redirects to workflow run pipeline in standard format
    service = OrchestratorService(db)
    return await service.run_workflow(schema)

@router.get("/status/{id}", response_model=WorkflowResponse)
async def get_workflow_execution_status(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = OrchestratorService(db)
    return await service.get_workflow_status(id)

@router.get("/history", response_model=List[WorkflowHistoryResponse])
async def list_workflows_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = OrchestratorService(db)
    return await service.get_history(skip, limit)

@router.get("/health")
def check_orchestrator_health():
    return {"status": "healthy", "service": "LangGraph Multi-Agent Orchestrator"}
