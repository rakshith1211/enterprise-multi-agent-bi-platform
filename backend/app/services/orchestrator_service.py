import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.orchestrator import WorkflowHistory
from app.schemas.orchestrator import WorkflowRequest, WorkflowResponse
from app.db.repositories.orchestrator import WorkflowRepository
from app.services.orchestrator.graph_compiler import compile_agent_workflow
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class OrchestratorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkflowRepository(db)

    async def run_workflow(self, request: WorkflowRequest) -> WorkflowResponse:
        # Check cache
        cache_key = f"workflow:{hash(request.model_dump_json())}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving completed workflow from Redis cache.")
            cached["created_at"] = datetime.fromisoformat(cached["created_at"])
            return WorkflowResponse(**cached)

        # 1. Prepare initial state
        initial_state = {
            "user_query": request.user_query,
            "connection_id": str(request.connection_id),
            "generate_report": request.generate_report,
            "query_plan": {},
            "sql": "",
            "query_results": {},
            "analytics": {},
            "visualization": {},
            "forecast": {},
            "recommendations": {},
            "report": {},
            "errors": [],
            "trace": []
        }

        # 2. Compile and run Graph
        graph = compile_agent_workflow(self.db)
        final_state = await graph.invoke(initial_state)

        # 3. Format Response
        response = WorkflowResponse(
            id=uuid.uuid4(),
            status=final_state.get("status", "success"),
            trace=final_state.get("trace", []),
            sql=final_state.get("sql"),
            query_results=final_state.get("query_results"),
            analytics=final_state.get("analytics"),
            visualization=final_state.get("visualization"),
            forecast=final_state.get("forecast") if final_state.get("forecast") else None,
            recommendations=final_state.get("recommendations") if final_state.get("recommendations") else None,
            report=final_state.get("report") if final_state.get("report") else None,
            errors=final_state.get("errors", []),
            created_at=datetime.now(timezone.utc)
        )

        # 4. Save report history
        history = WorkflowHistory(
            id=response.id,
            user_query=request.user_query,
            status=response.status,
            state_json=response.model_dump(mode="json")
        )
        await self.repo.create(history)

        # 5. Cache response (TTL 1 hour)
        resp_dict = response.model_dump()
        resp_dict["created_at"] = resp_dict["created_at"].isoformat()
        cache.set(cache_key, resp_dict, ttl=3600)

        return response

    async def get_workflow_status(self, workflow_id: uuid.UUID) -> WorkflowResponse:
        history = await self.repo.get(workflow_id)
        if not history:
            raise HTTPException(status_code=404, detail="Workflow execution not found")
        return WorkflowResponse(**history.state_json)

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[WorkflowHistory]:
        return await self.repo.list_history(skip, limit)
