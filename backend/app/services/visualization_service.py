import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.visualization import VisualizationHistory
from app.schemas.visualization import VisualizationRequest, VisualizationResponse, AccessibilityMetadata
from app.db.repositories.visualization import VisualizationRepository
from app.services.visualization.recommendation_engine import ChartRecommendationEngine
from app.services.visualization.spec_compilers import SpecCompilers
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class VisualizationService:
    def __init__(self, db: AsyncSession):
        self.repo = VisualizationRepository(db)

    async def generate_spec(self, request: VisualizationRequest) -> VisualizationResponse:
        # Check cache
        cache_key = f"vis:{hash(request.model_dump_json())}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving visualization spec from Redis cache.")
            cached["created_at"] = datetime.fromisoformat(cached["created_at"])
            return VisualizationResponse(**cached)

        if not request.rows:
            raise HTTPException(status_code=400, detail="Cannot render spec for empty rows dataset")

        # 1. Run Auto Chart Recommendation Engine
        primary, alt = ChartRecommendationEngine.recommend(
            request.columns,
            request.rows,
            request.preferred_chart_type
        )

        # 2. Compile specs for all 4 engines
        plotly_spec = SpecCompilers.compile_plotly(primary.chart_type, request.columns, request.rows)
        recharts_spec = SpecCompilers.compile_recharts(primary.chart_type, request.columns, request.rows)
        vega_spec = SpecCompilers.compile_vega_lite(primary.chart_type, request.columns, request.rows)
        echarts_spec = SpecCompilers.compile_echarts(primary.chart_type, request.columns, request.rows)

        # 3. Accessibility metadata
        accessibility = AccessibilityMetadata(
            title=f"Chart showing {primary.chart_type} distribution over {request.columns[0]}",
            description=f"This chart displays metric variables {request.columns[1:] if len(request.columns) > 1 else request.columns[0]} grouped by categorical dimension {request.columns[0]}.",
            aria_label=f"Visual representation of dataset metrics. Primary recommended visualization style is {primary.chart_type}.",
            color_palette_hints=SpecCompilers.COLOR_PALETTE
        )

        response = VisualizationResponse(
            id=uuid.uuid4(),
            summary={"row_count": len(request.rows), "columns_count": len(request.columns)},
            primary_recommendation=primary,
            alternative_recommendations=alt,
            plotly_spec=plotly_spec,
            recharts_spec=recharts_spec,
            vega_lite_spec=vega_spec,
            echarts_spec=echarts_spec,
            accessibility=accessibility,
            created_at=datetime.now(timezone.utc)
        )

        # 4. Save to history
        history = VisualizationHistory(
            input_summary=response.summary,
            chart_spec=response.model_dump(mode="json")
        )
        await self.repo.create(history)

        # 5. Cache spec (TTL 1 hour)
        resp_dict = response.model_dump()
        resp_dict["created_at"] = resp_dict["created_at"].isoformat()
        cache.set(cache_key, resp_dict, ttl=3600)

        return response

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[VisualizationHistory]:
        return await self.repo.list_history(skip, limit)
