import uuid
import time
import json
import logging
import redis
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.connections import DatabaseConnection
from app.models.audit import AuditLog
from app.schemas.connections import ConnectionCreate, ConnectionUpdate, ConnectionTestRequest
from app.db.repositories.connections import ConnectionRepository
from app.core.crypto import encryptor
from app.db.adapters.factory import DatabaseAdapterFactory
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis Caching Wrapper
class CacheManager:
    def __init__(self):
        try:
            self.client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, socket_connect_timeout=1)
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}. Caching disabled.")
            self.client = None

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None
        try:
            val = self.client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        if not self.client:
            return
        try:
            self.client.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def delete(self, key: str) -> None:
        if not self.client:
            return
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    def clear_pattern(self, pattern: str) -> None:
        if not self.client:
            return
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis clear_pattern error: {e}")

cache = CacheManager()

class ConnectionService:
    def __init__(self, db: AsyncSession):
        self.repo = ConnectionRepository(db)

    async def _audit(self, action: str, connection_id: Optional[str], status_str: str, user: str = "system", ip: str = "127.0.0.1", details: dict = None):
        log = AuditLog(
            user=user,
            action=action,
            connection_id=connection_id,
            ip_address=ip,
            status=status_str,
            details=details or {}
        )
        await self.repo.create_audit_log(log)

    async def create(self, schema: ConnectionCreate, creator: str = "system", ip: str = "127.0.0.1") -> DatabaseConnection:
        existing = await self.repo.get_by_name(schema.name)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Connection with this name already exists")

        details = schema.model_dump()
        pwd = details.pop("password", None)
        conn_str = details.pop("connection_string", None)

        enc_pwd = encryptor.encrypt(pwd) if pwd else None
        enc_conn_str = encryptor.encrypt(conn_str) if conn_str else None

        db_conn = DatabaseConnection(
            name=schema.name,
            description=schema.description,
            database_type=schema.database_type,
            host=schema.host,
            port=schema.port,
            username=schema.username,
            encrypted_password=enc_pwd,
            encrypted_connection_string=enc_conn_str,
            database_name=schema.database_name,
            ssl_enabled=schema.ssl_enabled,
            extra_parameters=schema.extra_parameters,
            environment=schema.environment,
            tags=schema.tags,
            created_by=creator,
            updated_by=creator
        )

        try:
            saved = await self.repo.create(db_conn)
            await self._audit("CONNECTION_CREATED", str(saved.id), "success", user=creator, ip=ip)
            return saved
        except Exception as exc:
            await self._audit("CONNECTION_CREATED", None, "failed", user=creator, ip=ip, details={"error": str(exc)})
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {exc}")

    async def get(self, id: uuid.UUID) -> DatabaseConnection:
        conn = await self.repo.get_by_id(id)
        if not conn:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
        return conn

    async def list_connections(self, skip: int = 0, limit: int = 100) -> List[DatabaseConnection]:
        return await self.repo.list_all(skip, limit)

    async def search(self, query: str) -> List[DatabaseConnection]:
        return await self.repo.search(query)

    async def update(self, id: uuid.UUID, schema: ConnectionUpdate, updater: str = "system", ip: str = "127.0.0.1") -> DatabaseConnection:
        conn = await self.get(id)
        updates = schema.model_dump(exclude_unset=True)

        pwd = updates.pop("password", None)
        conn_str = updates.pop("connection_string", None)

        if pwd is not None:
            conn.encrypted_password = encryptor.encrypt(pwd)
        if conn_str is not None:
            conn.encrypted_connection_string = encryptor.encrypt(conn_str)

        for k, v in updates.items():
            setattr(conn, k, v)
        
        conn.updated_by = updater
        conn.updated_at = datetime.now(timezone.utc)

        try:
            updated = await self.repo.update(conn)
            # Evict metadata cache
            cache.delete(f"metadata:{id}")
            await self._audit("CONNECTION_UPDATED", str(id), "success", user=updater, ip=ip)
            return updated
        except Exception as exc:
            await self._audit("CONNECTION_UPDATED", str(id), "failed", user=updater, ip=ip, details={"error": str(exc)})
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    async def delete(self, id: uuid.UUID, user: str = "system", ip: str = "127.0.0.1") -> bool:
        success = await self.repo.soft_delete(id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
        cache.delete(f"metadata:{id}")
        await self._audit("CONNECTION_DELETED", str(id), "success", user=user, ip=ip)
        return True

    async def restore(self, id: uuid.UUID, user: str = "system", ip: str = "127.0.0.1") -> DatabaseConnection:
        restored = await self.repo.restore(id)
        if not restored:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deleted connection not found")
        await self._audit("CONNECTION_RESTORED", str(id), "success", user=user, ip=ip)
        return restored

    async def enable(self, id: uuid.UUID, user: str = "system", ip: str = "127.0.0.1") -> DatabaseConnection:
        conn = await self.get(id)
        conn.status = "active"
        updated = await self.repo.update(conn)
        await self._audit("CONNECTION_ENABLED", str(id), "success", user=user, ip=ip)
        return updated

    async def disable(self, id: uuid.UUID, user: str = "system", ip: str = "127.0.0.1") -> DatabaseConnection:
        conn = await self.get(id)
        conn.status = "disabled"
        updated = await self.repo.update(conn)
        await self._audit("CONNECTION_DISABLED", str(id), "success", user=user, ip=ip)
        return updated

    def _get_adapter(self, conn: DatabaseConnection):
        details = {
            "host": conn.host,
            "port": conn.port,
            "username": conn.username,
            "database_name": conn.database_name,
        }
        if conn.encrypted_password:
            details["password"] = encryptor.decrypt(conn.encrypted_password)
        if conn.encrypted_connection_string:
            details["connection_string"] = encryptor.decrypt(conn.encrypted_connection_string)

        pool_params = {
            "pool_size": conn.extra_parameters.get("pool_size", 5),
            "pool_timeout": conn.extra_parameters.get("pool_timeout", 30),
            "pool_recycle": conn.extra_parameters.get("pool_recycle", 1800),
            "max_overflow": conn.extra_parameters.get("max_overflow", 10),
        }
        return DatabaseAdapterFactory.get_adapter(conn.database_type, details, pool_params)

    async def test_connection_by_details(self, schema: ConnectionTestRequest) -> Dict[str, Any]:
        details = schema.model_dump()
        pwd = details.pop("password", None)
        conn_str = details.pop("connection_string", None)
        
        # Test connection details
        conn_details = {
            "host": schema.host,
            "port": schema.port,
            "username": schema.username,
            "database_name": schema.database_name,
            "password": pwd,
            "connection_string": conn_str
        }
        try:
            adapter = DatabaseAdapterFactory.get_adapter(schema.database_type, conn_details)
            latency = adapter.test_connection()
            return {"status": "success", "response_time_ms": round(latency, 2)}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def run_health_check(self, id: uuid.UUID) -> Dict[str, Any]:
        conn = await self.get(id)
        if conn.status == "disabled":
            return {"status": "disabled", "error": "Connection is disabled"}
        try:
            adapter = self._get_adapter(conn)
            latency = adapter.test_connection()
            conn.last_successful_connection = datetime.now(timezone.utc)
            conn.average_response_time_ms = int((conn.average_response_time_ms + latency) / 2) if conn.average_response_time_ms else int(latency)
            await self.repo.update(conn)
            return {"status": "healthy", "latency_ms": round(latency, 2)}
        except Exception as e:
            conn.last_failed_connection = datetime.now(timezone.utc)
            conn.failure_reason = str(e)
            await self.repo.update(conn)
            return {"status": "unhealthy", "error": str(e)}

    async def get_schemas(self, id: uuid.UUID) -> List[str]:
        conn = await self.get(id)
        adapter = self._get_adapter(conn)
        try:
            return adapter.get_schemas()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch schemas: {e}")

    async def get_tables(self, id: uuid.UUID, schema: str) -> List[str]:
        conn = await self.get(id)
        adapter = self._get_adapter(conn)
        try:
            return adapter.get_tables(schema=schema)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch tables: {e}")

    async def get_columns(self, id: uuid.UUID, schema: str, table: str) -> List[Dict[str, Any]]:
        conn = await self.get(id)
        adapter = self._get_adapter(conn)
        try:
            return adapter.get_columns(table, schema=schema)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch columns: {e}")

    async def refresh_metadata(self, id: uuid.UUID) -> Dict[str, Any]:
        # Crawl all schemas, tables, and columns to build a schema map
        conn = await self.get(id)
        adapter = self._get_adapter(conn)
        
        try:
            schemas = adapter.get_schemas()
            schema_map = {}
            for schema in schemas:
                # Exclude internal schemas for cleaner AI agent context
                if schema.lower() in ["information_schema", "pg_catalog", "sys"]:
                    continue
                tables = adapter.get_tables(schema=schema)
                views = adapter.get_views(schema=schema)
                schema_map[schema] = {
                    "tables": {},
                    "views": views
                }
                for table in tables:
                    columns = adapter.get_columns(table, schema=schema)
                    fkeys = adapter.get_foreign_keys(table, schema=schema)
                    indexes = adapter.get_indexes(table, schema=schema)
                    constraints = adapter.get_unique_constraints(table, schema=schema)
                    
                    schema_map[schema]["tables"][table] = {
                        "columns": columns,
                        "foreign_keys": fkeys,
                        "indexes": indexes,
                        "unique_constraints": constraints
                    }

            # Cache the reflected schema in Redis
            cache.set(f"metadata:{id}", schema_map, ttl=settings.extra_parameters.get("metadata_ttl", 86400) if hasattr(settings, "extra_parameters") else 86400)
            await self._audit("SCHEMA_REFRESHED", str(id), "success")
            return {"status": "success", "schema_map": schema_map}
        except Exception as e:
            await self._audit("SCHEMA_REFRESHED", str(id), "failed", details={"error": str(e)})
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Reflection failed: {e}")
