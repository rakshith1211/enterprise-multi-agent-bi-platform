import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.recommendation import RecommendationHistory
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, RecommendationItem
from app.db.repositories.recommendation import RecommendationRepository
from app.services.recommendation.opportunity_engine import OpportunityEngine
from app.services.recommendation.risk_engine import RiskEngine
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.repo = RecommendationRepository(db)

    async def generate(self, request: RecommendationRequest) -> RecommendationResponse:
        # Check cache
        cache_key = f"recommendation:{hash(request.model_dump_json())}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving recommendation list from Redis cache.")
            cached["created_at"] = datetime.fromisoformat(cached["created_at"])
            return RecommendationResponse(**cached)

        # 1. Run Opportunity Engine
        opportunities = OpportunityEngine.detect_opportunities(
            request.analytics_summary,
            request.forecast_summary,
            request.business_rules
        )

        # 2. Run Risk Engine
        risks = RiskEngine.evaluate_risks(
            request.analytics_summary,
            request.forecast_summary,
            request.business_rules
        )

        all_recommendations = opportunities + risks

        # If empty, generate a baseline baseline recommendation
        if not all_recommendations:
            all_recommendations.append(
                RecommendationItem(
                    title="Maintain Baseline Operations",
                    type="Operational Efficiency",
                    priority="Low",
                    business_impact="No high-variance risks or positive expansion opportunities are flagged. Maintain standard business levels.",
                    confidence=0.80,
                    reasoning="Compiled because analytics and forecast summaries indicate a stable, flat business performance.",
                    affected_kpis=["revenue", "operational_cost"],
                    affected_departments=["Operations"],
                    estimated_benefits="Sustained operational baseline without additional capital expenditures.",
                    estimated_risks="Potential complacency risk if competitor innovations emerge.",
                    suggested_actions=["Review monthly variance reports for minor performance shifts."]
                )
            )

        response = RecommendationResponse(
            id=uuid.uuid4(),
            recommendations=all_recommendations,
            created_at=datetime.now(timezone.utc)
        )

        # 3. Log history
        history = RecommendationHistory(
            input_summary={
                "has_rules": len(request.business_rules) > 0,
                "anomalies_flagged": len(request.analytics_summary.get("outliers", []))
            },
            recommendation_json=response.model_dump(mode="json")
        )
        await self.repo.create(history)

        # 4. Cache recommendation (TTL 1 hour)
        resp_dict = response.model_dump()
        resp_dict["created_at"] = resp_dict["created_at"].isoformat()
        cache.set(cache_key, resp_dict, ttl=3600)

        return response

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[RecommendationHistory]:
        return await self.repo.list_history(skip, limit)
