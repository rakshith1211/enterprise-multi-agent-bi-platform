import uuid
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.models.query_execution import QueryExecutionHistory
from app.schemas.query_execution import QueryExecutionRequest, NormalizedQueryResponse
from app.db.repositories.query_execution import QueryExecutionRepository
from app.services.connection_service import ConnectionService, cache
from app.services.sql_validator import SQLValidator

logger = logging.getLogger(__name__)

class QueryExecutionService:
    def __init__(self, db: AsyncSession):
        self.repo = QueryExecutionRepository(db)
        self.conn_service = ConnectionService(db)

    def _infer_type(self, val: Any) -> str:
        if isinstance(val, int):
            return "Integer"
        elif isinstance(val, float):
            return "Float"
        elif isinstance(val, bool):
            return "Boolean"
        elif isinstance(val, datetime):
            return "DateTime"
        elif val is None:
            return "Null"
        else:
            return "String"

    def _determine_data_types(self, columns: List[str], rows: List[dict]) -> Dict[str, str]:
        types = {}
        if not rows:
            return {c: "String" for c in columns}
        
        # Scan first row to infer column types
        first_row = rows[0]
        for col in columns:
            types[col] = self._infer_type(first_row.get(col))
        return types

    async def execute_query(self, request: QueryExecutionRequest) -> NormalizedQueryResponse:
        sql = request.sql
        connection_id = request.connection_id
        params = request.parameters

        # 1. Enforce strict SELECT security guardrails
        is_safe = SQLValidator.validate_safety(sql)
        if not is_safe:
            logger.error(f"Unsafe query blocked: {sql}")
            # Log failed execution audit
            await self._log_execution(
                sql_query=sql,
                connection_id=connection_id,
                execution_time_ms=0.0,
                row_count=0,
                status="failed",
                error="Security Violation: SQL query failed strict SELECT-only validation rules."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Violation: Query failed SELECT-only validation rules."
            )

        # 2. Redis Caching Check
        cache_key = f"query_result:{connection_id}:{hash(sql)}:{hash(frozenset(params.items()))}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving query result from Redis cache.")
            return NormalizedQueryResponse(**cached)

        conn = await self.conn_service.get(connection_id)
        adapter = self.conn_service._get_adapter(conn)

        # 4. Asynchronous Threaded Execution
        start_time = time.perf_counter()
        status_flag = "success"
        error_msg = None
        
        try:
            # Run in executor thread pool to avoid blocking async event loop during connection execution
            res = await run_in_threadpool(
                adapter.execute_query,
                sql=sql,
                params=params,
                timeout=request.timeout_seconds
            )
            columns = res["columns"]
            rows = res["rows"]
        except Exception as e:
            status_flag = "failed"
            error_msg = str(e)
            logger.error(f"Database execution error: {error_msg}")
            
            # Log failure
            await self._log_execution(
                sql_query=sql,
                connection_id=connection_id,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
                row_count=0,
                status="failed",
                error=error_msg
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database execution error: {error_msg}"
            )

        latency_ms = (time.perf_counter() - start_time) * 1000

        # 5. Result Normalization & Type Inference
        data_types = self._determine_data_types(columns, rows)

        response = NormalizedQueryResponse(
            columns=columns,
            data_types=data_types,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=latency_ms,
            warnings=["Query results limited to 1000 rows"] if len(rows) >= 1000 else [],
            metadata={
                "dialect": adapter.get_dialect_name(),
                "connection_id": str(connection_id)
            }
        )

        # 6. Audit logging in PostgreSQL
        await self._log_execution(
            sql_query=sql,
            connection_id=connection_id,
            execution_time_ms=latency_ms,
            row_count=len(rows),
            status=status_flag,
            error=error_msg
        )

        # 7. Cache query result (TTL 5 minutes for performance)
        cache.set(cache_key, response.model_dump(), ttl=300)

        return response

    async def _log_execution(
        self,
        sql_query: str,
        connection_id: uuid.UUID,
        execution_time_ms: float,
        row_count: int,
        status: str,
        error: str = None
    ):
        try:
            history = QueryExecutionHistory(
                sql_query=sql_query,
                connection_id=str(connection_id),
                execution_time_ms=execution_time_ms,
                row_count=row_count,
                status=status,
                error=error
            )
            await self.repo.create(history)
        except Exception as ex:
            logger.error(f"Failed to save execution audit: {str(ex)}")

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[QueryExecutionHistory]:
        return await self.repo.list_history(skip, limit)

    async def get_observability_metrics(self) -> Dict[str, Any]:
        return await self.repo.get_metrics()
