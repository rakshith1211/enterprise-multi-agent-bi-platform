import uuid
import logging
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.sql_agent import SQLAgentHistory
from app.schemas.sql_agent import SQLAgentRequest, SQLAgentResponse
from app.db.repositories.sql_agent import SQLAgentRepository
from app.db.adapters.sql_dialects.factory import DialectAdapterFactory
from app.services.sql_optimizer import SQLOptimizer
from app.services.sql_validator import SQLValidator
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class SQLAgentService:
    def __init__(self, db: AsyncSession):
        self.repo = SQLAgentRepository(db)

    async def generate_sql(self, request: SQLAgentRequest) -> SQLAgentResponse:
        # Create cache key
        cache_key = f"sql:{hash(request.model_dump_json())}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving SQL from Redis cache.")
            return SQLAgentResponse(**cached)

        # 1. Resolve Dialect Adapter
        adapter = DialectAdapterFactory.get_adapter(request.database_type)

        # 2. Build Fields Projection (Select Columns)
        # Avoid SELECT * - project required columns only
        quoted_cols = []
        for col in request.required_columns:
            # Match columns to their respective tables if multiple tables exist
            table_prefix = None
            if len(request.required_tables) > 1:
                # Basic prefix matching (e.g. total_sales is mapped if table prefix matches, 
                # for mock simplicity we assign col to table[0] or prefix)
                table_prefix = request.required_tables[0]
            quoted_cols.append(adapter.format_column(col, table_prefix))

        # Add metric aggregation
        metric_col = request.metric.lower()
        if len(request.required_tables) > 1:
            metric_col = f"{request.required_tables[0]}.{metric_col}"
        
        proj_fields = quoted_cols.copy()
        proj_fields.append(f"{request.aggregation}({metric_col}) AS {adapter.quote_identifier('aggregated_' + request.metric.lower())}")
        
        select_clause = f"SELECT {', '.join(proj_fields)}"

        # 3. Build FROM clause
        primary_table = adapter.format_table(request.required_tables[0])
        from_clause = f"FROM {primary_table}"

        # 4. Join Planner (pruning unnecessary joins)
        # Star/Snowflake schemas join building
        raw_joins = []
        if len(request.required_tables) > 1:
            for tbl in request.required_tables[1:]:
                raw_joins.append(f"JOIN {tbl} ON {request.required_tables[0]}.user_id = {tbl}.id")
        
        optimized_joins = SQLOptimizer.prune_joins(request.required_tables, raw_joins)
        join_clause = " ".join(optimized_joins)

        # 5. Filter Builder & Parameterizer (Pushdown filters early)
        # Inject business rules directly into filters
        all_filters = request.filters.copy()
        for rule in request.business_rules:
            # Exclude cancelled orders
            if "cancelled" in rule.lower():
                all_filters.append({"column": "status", "operator": "!=", "value": "Cancelled"})
            # Active customers
            elif "active" in rule.lower():
                all_filters.append({"column": "is_active", "operator": "=", "value": True})

        filter_clauses, parameters = SQLOptimizer.parameterize_filters(all_filters)
        where_clause = ""
        if filter_clauses:
            where_clause = f"WHERE {' AND '.join(filter_clauses)}"

        # 6. Group By & Order By Builder
        group_clause = ""
        order_clause = ""
        if request.dimensions:
            quoted_dims = [adapter.format_column(d, request.required_tables[0] if len(request.required_tables) > 1 else None) for d in request.dimensions]
            group_clause = f"GROUP BY {', '.join(quoted_dims)}"
            order_clause = f"ORDER BY {quoted_dims[0]} DESC"

        # 7. Compile Final SQL
        sql_parts = [select_clause, from_clause]
        if join_clause:
            sql_parts.append(join_clause)
        if where_clause:
            sql_parts.append(where_clause)
        if group_clause:
            sql_parts.append(group_clause)
        if order_clause:
            sql_parts.append(order_clause)

        # Apply dialect limit formatting
        sql_parts.append(adapter.format_limit(1000))

        raw_sql = " ".join(sql_parts)

        # 8. SQL Security Validation
        is_safe = SQLValidator.validate_safety(raw_sql)
        if not is_safe:
            logger.error(f"SQL Injection attempt blocked: {raw_sql}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Violation: SQL query failed strict select-only validation rules."
            )

        # 9. Explainability Builder
        explainability = (
            f"Selected tables {request.required_tables} using primary entity mappings. "
            f"Generated {request.aggregation} aggregator on metric '{request.metric}'. "
            f"Applied filters: {[f['column'] for f in request.filters]} with dynamic parameter bindings. "
            f"Injected business rules logic constraints: {request.business_rules}."
        )

        response = SQLAgentResponse(
            sql=raw_sql,
            dialect=request.database_type,
            parameters=parameters,
            estimated_cost={"scanned_rows_approx": 50000, "join_cost": len(optimized_joins), "llm_tokens": 0},
            explainability=explainability,
            validation_status="success"
        )

        # 10. Persist to History Database
        history = SQLAgentHistory(
            query_plan_id=str(request.query_plan_id) if request.query_plan_id else None,
            sql_query=raw_sql,
            dialect=request.database_type,
            parameters_json=parameters
        )
        await self.repo.create(history)

        # Cache in Redis (TTL 1 hour)
        cache.set(cache_key, response.model_dump(), ttl=3600)

        return response

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[SQLAgentHistory]:
        return await self.repo.list_history(skip, limit)
