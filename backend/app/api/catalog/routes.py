from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import uuid

from app.db.session import get_db
from app.schemas.catalog import (
    DomainCreate,
    DomainResponse,
    GlossaryCreate,
    GlossaryResponse,
    TermCreate,
    TermResponse,
    TermUpdate,
    LineageCreate,
    LineageResponse,
    SemanticSearchResult
)
from app.services.catalog_service import CatalogService

router = APIRouter()

# Domain routes
@router.post("/domains", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def create_domain(schema: DomainCreate, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.create_domain(schema)

@router.get("/domains", response_model=List[DomainResponse])
async def list_domains(db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.list_domains()

# Glossary routes
@router.post("/glossaries", response_model=GlossaryResponse, status_code=status.HTTP_201_CREATED)
async def create_glossary(schema: GlossaryCreate, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.create_glossary(schema)

# Term routes
@router.post("/terms", response_model=TermResponse, status_code=status.HTTP_201_CREATED)
async def create_term(schema: TermCreate, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.create_term(schema)

@router.get("/terms", response_model=List[TermResponse])
async def list_terms(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.list_terms(skip, limit)

@router.get("/terms/{id}", response_model=TermResponse)
async def get_term_details(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.get_term(id)

@router.put("/terms/{id}", response_model=TermResponse)
async def update_term(id: uuid.UUID, schema: TermUpdate, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.update_term(id, schema)

@router.delete("/terms/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_term(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    await service.delete_term(id)

# Search & similar
@router.get("/search", response_model=List[SemanticSearchResult])
async def search_catalog(q: str, limit: int = 10, confidence_threshold: float = 0.0, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.search(q, limit, confidence_threshold)

@router.get("/similar/{id}")
async def get_similar_terms(id: uuid.UUID, limit: int = 5, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.get_similar_terms(id, limit)

@router.post("/reindex")
async def force_reindex(db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.reindex_all()

# Lineage routes
@router.post("/lineage", response_model=LineageResponse, status_code=status.HTTP_201_CREATED)
async def create_lineage(schema: LineageCreate, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.create_lineage(schema)

@router.get("/lineage", response_model=List[LineageResponse])
async def list_lineage(db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.list_lineage()

# AI Context Builder Endpoint
@router.get("/context")
async def build_ai_context(q: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.build_ai_context(q)
