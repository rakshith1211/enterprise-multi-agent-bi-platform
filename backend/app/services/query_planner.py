import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.planner import QueryPlanHistory
from app.schemas.planner import QueryPlanRequest, QueryPlanResponse, DAGStep, CostEstimate
from app.db.repositories.planner import PlannerRepository
from app.services.intent_classifier import IntentClassifier
from app.services.time_intelligence import TimeIntelligence
from app.services.entity_extractor import EntityExtractor
from app.services.catalog_service import CatalogService
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class QueryPlannerService:
    def __init__(self, db: AsyncSession):
        self.repo = PlannerRepository(db)
        self.catalog = CatalogService(db)

    def _normalize_query(self, query: str) -> str:
        # Standardize basic spelling and spacing
        q = query.strip().replace("  ", " ")
        if not q.endswith("?"):
            q += "?"
        return q

    def _analyze_complexity(self, steps: List[DAGStep], filters: List[dict], joins: List[str]) -> str:
        score = len(steps) + len(filters) + len(joins)
        if score <= 2:
            return "Simple"
        elif score <= 4:
            return "Medium"
        elif score <= 6:
            return "Complex"
        else:
            return "Very Complex"

    def _estimate_cost(self, complexity: str, steps: List[DAGStep]) -> CostEstimate:
        # Generate cost estimates
        if complexity == "Simple":
            return CostEstimate(
                sql_execution_ms=80,
                runtime_ms=150,
                llm_tokens=1200,
                estimated_cost_usd=0.002
            )
        elif complexity == "Medium":
            return CostEstimate(
                sql_execution_ms=250,
                runtime_ms=450,
                llm_tokens=2200,
                estimated_cost_usd=0.005
            )
        else:
            return CostEstimate(
                sql_execution_ms=1200,
                runtime_ms=2500,
                llm_tokens=5000,
                estimated_cost_usd=0.015
            )

    async def generate_plan(self, request: QueryPlanRequest) -> QueryPlanResponse:
        user_query = request.user_query
        
        # 1. Check Planner Memory (Redis Cache) for identical query plan
        cached_plan = cache.get(f"plan:{user_query}")
        if cached_plan:
            logger.info(f"Reusing cached plan for query: {user_query}")
            # De-serialize datetime
            cached_plan["created_at"] = datetime.fromisoformat(cached_plan["created_at"])
            return QueryPlanResponse(**cached_plan)

        normalized_query = self._normalize_query(user_query)

        # 2. Intent Classification
        intent = IntentClassifier.classify(normalized_query)

        # 3. Entity Extraction & Time Intelligence
        entities = EntityExtractor.extract_entities(normalized_query)
        time_intel = TimeIntelligence.parse_time_range(normalized_query)
        
        # Merge time filter into filters
        filters = entities["filters"]
        if time_intel["sql_filter"]:
            filters.append({
                "column": "sale_date",
                "operator": "SQL_EXPR",
                "value": time_intel["sql_filter"]
            })

        # 4. Semantic Catalog lookup
        catalog_ctx = await self.catalog.build_ai_context(normalized_query)
        
        kpis = [k["name"] for k in catalog_ctx["kpis"]]
        business_rules = [r["definition"] for r in catalog_ctx["business_rules"]]
        
        tables = [t["table"] for t in catalog_ctx["mappings"]["tables"]]
        columns = [c["column"] for c in catalog_ctx["mappings"]["columns"]]
        
        # 5. Joins & Relationship extraction
        joins = []
        relationships = []
        if len(tables) > 1:
            joins.append(f"JOIN {tables[0]} ON {tables[0]}.user_id = {tables[1]}.id")
            relationships.append(f"{tables[0]} related to {tables[1]} (Foreign Key)")

        # 6. Ambiguity Detection & Validation
        clarifications = []
        if not entities["metrics"] and not kpis:
            clarifications.append("Could you clarify which metric or value you'd like to aggregate (e.g. Sales, Gross Margin)?")
        if not tables:
            clarifications.append("No database tables mapped to query context. Please define table mappings in semantic catalog.")

        # 7. Recommended agent and step-by-step DAG building
        rec_agent = "SQL Agent"
        if intent == "forecast":
            rec_agent = "Forecast Agent"
        elif intent == "visualization":
            rec_agent = "Visualization Agent"

        steps = []
        # Step 1: SQL Extraction
        steps.append(DAGStep(
            step_id="step_1",
            name="SQL Fetching",
            agent="SQL Agent",
            parameters={"tables": tables, "columns": columns, "filters": filters}
        ))
        
        # Step 2: Analytics calculations (if rules or aggregates exist)
        if intent in ["analytics", "forecast", "visualization"]:
            steps.append(DAGStep(
                step_id="step_2",
                name="Data Calculations",
                agent="Analytics Agent",
                depends_on=["step_1"],
                parameters={"kpi_formulas": [k["formula"] for k in catalog_ctx["kpis"]]}
            ))

        # Step 3: Specific Intent target
        if intent == "forecast":
            steps.append(DAGStep(
                step_id="step_3",
                name="Time Series Forecasting",
                agent="Forecast Agent",
                depends_on=["step_2"]
            ))
        elif intent == "visualization":
            steps.append(DAGStep(
                step_id="step_3",
                name="Chart Compilation",
                agent="Visualization Agent",
                depends_on=["step_2"],
                parameters={"hints": ["LineChart", "BarChart"]}
            ))

        # 8. Complexity and Cost Analysis
        complexity = self._analyze_complexity(steps, filters, joins)
        cost_est = self._estimate_cost(complexity, steps)

        # 9. Explainability
        explainability = (
            f"Classified intent as '{intent}' based on query syntax. "
            f"Mapped tables: {tables} and columns: {columns} using semantic glossary. "
            f"Resolved time interval '{time_intel['raw_time_expression']}' and applied business rules: {business_rules}."
        )

        confidence = 0.95 if not clarifications else 0.40

        business_terms_list = catalog_ctx.get("business_terms", [])
        domain_name = business_terms_list[0].get("business_domain", "Sales") if business_terms_list else "Sales"

        plan = QueryPlanResponse(
            id=uuid.uuid4(),
            user_query=user_query,
            normalized_query=normalized_query,
            business_domain=domain_name,
            intent=intent,
            complexity=complexity,
            recommended_agent=rec_agent,
            execution_steps=steps,
            metrics=entities["metrics"],
            kpis=kpis,
            dimensions=entities["dimensions"],
            filters=filters,
            joins=joins,
            relationships=relationships,
            visualization_hints=["LineChart"] if intent == "visualization" else [],
            cost_estimate=cost_est,
            clarification_requirements=clarifications,
            explainability=explainability,
            confidence=confidence,
            created_at=datetime.now(timezone.utc)
        )

        # 10. Persist to History Database
        history = QueryPlanHistory(
            user_query=user_query,
            normalized_query=normalized_query,
            plan_json=plan.model_dump(mode="json")
        )
        await self.repo.create(history)

        # 11. Cache the plan in Redis (TTL 1 hour)
        # Convert datetime to string for json serialization
        plan_dict = plan.model_dump()
        plan_dict["created_at"] = plan_dict["created_at"].isoformat()
        cache.set(f"plan:{user_query}", plan_dict, ttl=3600)

        return plan
        
    async def get_history(self, skip: int = 0, limit: int = 100) -> List[QueryPlanHistory]:
        return await self.repo.list_history(skip, limit)
