from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.db.session import get_db
from app.schemas.rag import (
    RAGIngestRequest, RAGUploadResponse, RAGRetrieveRequest, RAGRetrieveResponse, RAGHistoryResponse
)
from app.services.rag_service import RAGService

router = APIRouter()

@router.post("/ingest", response_model=RAGUploadResponse, status_code=status.HTTP_201_CREATED)
async def ingest_unstructured_document(schema: RAGIngestRequest, db: AsyncSession = Depends(get_db)):
    service = RAGService(db)
    return await service.ingest_document(schema)

@router.post("/retrieve", response_model=RAGRetrieveResponse)
async def retrieve_semantic_context(schema: RAGRetrieveRequest, db: AsyncSession = Depends(get_db)):
    service = RAGService(db)
    return await service.retrieve_context(schema)

@router.delete("/document/{id}")
async def delete_rag_document(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = RAGService(db)
    return await service.delete_document(id)

@router.get("/history", response_model=List[RAGHistoryResponse])
async def list_rag_documents_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = RAGService(db)
    return await service.get_history(skip, limit)

@router.get("/health")
def check_rag_health():
    return {"status": "healthy", "service": "Enterprise RAG Knowledge Base"}
