import uuid
import logging
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.analytics import AnalyticsHistory
from app.schemas.analytics import AnalyticsRequest, AnalyticsResponse
from app.db.repositories.analytics import AnalyticsRepository
from app.services.analytics.data_quality import DataQualityEngine
from app.services.analytics.statistics_engine import StatisticsEngine
from app.services.analytics.kpi_engine import KPIEngine
from app.services.analytics.trend_engine import TrendEngine
from app.services.analytics.correlation_engine import CorrelationEngine
from app.services.analytics.anomaly_detection import AnomalyEngine
from app.services.analytics.insight_generator import InsightGenerator
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repo = AnalyticsRepository(db)

    async def analyze_dataset(self, request: AnalyticsRequest) -> AnalyticsResponse:
        # Check cache
        cache_key = f"analytics:{hash(request.model_dump_json())}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving analytics report from Redis Cache.")
            cached["created_at"] = datetime.fromisoformat(cached["created_at"])
            return AnalyticsResponse(**cached)

        if not request.rows:
            raise HTTPException(status_code=400, detail="Cannot analyze empty rows dataset")

        # 1. Load DataFrame using Pandas (vectorized math)
        df = pd.DataFrame(request.rows, columns=request.columns)

        # 2. Execute Data Quality checks
        quality = DataQualityEngine.evaluate(df)

        # 3. Calculate descriptive statistics
        stats = StatisticsEngine.calculate_stats(df)

        # 4. Calculate standard KPIs
        kpis = KPIEngine.calculate_kpis(df)

        # 5. Detect trends
        trends = TrendEngine.calculate_trends(df)

        # 6. Correlation Analysis
        correlations = CorrelationEngine.calculate_correlations(df)

        # 7. Outliers detection
        anomalies = AnomalyEngine.detect_anomalies(df)

        # 8. Business Insight & Explainability generator
        insights = InsightGenerator.generate_insights(kpis, trends, anomalies)

        explainability = (
            f"Calculated descriptive aggregates across {len(stats)} numeric fields. "
            f"Evaluated data quality completeness score: {quality.completeness_score}. "
            f"Identified {len(anomalies)} outliers and compiled growth performance."
        )

        response = AnalyticsResponse(
            id=uuid.uuid4(),
            summary={"row_count": len(df), "columns_count": len(df.columns)},
            statistics=stats,
            trends=trends,
            outliers=anomalies,
            correlations=correlations,
            kpis=kpis,
            data_quality=quality,
            insights=insights,
            explainability=explainability,
            confidence=0.96 if quality.completeness_score > 0.9 else 0.70,
            created_at=datetime.now(timezone.utc)
        )

        # 9. Log execution to history db
        history = AnalyticsHistory(
            input_summary=response.summary,
            analytics_json=response.model_dump(mode="json")
        )
        await self.repo.create(history)

        # 10. Cache result (TTL 10 mins)
        resp_dict = response.model_dump()
        resp_dict["created_at"] = resp_dict["created_at"].isoformat()
        cache.set(cache_key, resp_dict, ttl=600)

        return response

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[AnalyticsHistory]:
        return await self.repo.list_history(skip, limit)
