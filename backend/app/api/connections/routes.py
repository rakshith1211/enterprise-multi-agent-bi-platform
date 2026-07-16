from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.db.session import get_db
from app.schemas.connections import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionResponse,
    ConnectionTestRequest
)
from app.services.connection_service import ConnectionService

router = APIRouter()

@router.post("", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(schema: ConnectionCreate, request: Request, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.create(schema, ip=request.client.host if request.client else "127.0.0.1")

@router.get("", response_model=List[ConnectionResponse])
async def list_connections(db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.list_connections()

@router.get("/search", response_model=List[ConnectionResponse])
async def search_connections(q: str, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.search(q)

@router.get("/{id}", response_model=ConnectionResponse)
async def get_connection_details(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.get(id)

@router.put("/{id}", response_model=ConnectionResponse)
async def update_connection(id: uuid.UUID, schema: ConnectionUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.update(id, schema, ip=request.client.host if request.client else "127.0.0.1")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    await service.delete(id, ip=request.client.host if request.client else "127.0.0.1")

@router.post("/{id}/restore", response_model=ConnectionResponse)
async def restore_connection(id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.restore(id, ip=request.client.host if request.client else "127.0.0.1")

@router.patch("/{id}/enable", response_model=ConnectionResponse)
async def enable_connection(id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.enable(id, ip=request.client.host if request.client else "127.0.0.1")

@router.patch("/{id}/disable", response_model=ConnectionResponse)
async def disable_connection(id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.disable(id, ip=request.client.host if request.client else "127.0.0.1")

@router.post("/test")
async def test_connection(schema: ConnectionTestRequest):
    # Dummy service instantiation without DB for transient testing
    service = ConnectionService(None)
    res = await service.test_connection_by_details(schema)
    if res["status"] == "failed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res["error"])
    return res

@router.get("/{id}/health")
async def connection_health_check(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    res = await service.run_health_check(id)
    if res["status"] in ["unhealthy", "disabled"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=res.get("error", "Connection is unhealthy or disabled"))
    return res

@router.get("/{id}/schemas")
async def get_schemas(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.get_schemas(id)

@router.get("/{id}/schemas/{schema}/tables")
async def get_tables(id: uuid.UUID, schema: str, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.get_tables(id, schema)

@router.get("/{id}/schemas/{schema}/tables/{table}/columns")
async def get_columns(id: uuid.UUID, schema: str, table: str, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.get_columns(id, schema, table)

@router.post("/{id}/refresh-metadata")
async def refresh_metadata(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    return await service.refresh_metadata(id)
