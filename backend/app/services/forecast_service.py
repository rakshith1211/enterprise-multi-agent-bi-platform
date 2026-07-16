import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.forecast import ForecastHistory
from app.schemas.forecast import ForecastRequest, ForecastResponse, PredictionPoint, AccuracyMetrics
from app.db.repositories.forecast import ForecastRepository
from app.services.forecast.model_manager import ModelManager
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class ForecastService:
    def __init__(self, db: AsyncSession):
        self.repo = ForecastRepository(db)

    async def predict(self, request: ForecastRequest) -> ForecastResponse:
        # Check cache
        cache_key = f"forecast:{hash(request.model_dump_json())}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving forecast prediction from Redis cache.")
            cached["created_at"] = datetime.fromisoformat(cached["created_at"])
            return ForecastResponse(**cached)

        if len(request.history_values) < 3:
            raise HTTPException(status_code=400, detail="Cannot compute forecast with less than 3 historical values.")

        # 1. Run Auto Model Selection & Predict
        model_name, preds, upper, lower, metrics = ModelManager.select_and_forecast(
            request.history_values,
            request.horizon
        )

        # 2. Date parsing and projection extensions
        history_dates = [datetime.fromisoformat(d.replace("Z", "+00:00")) for d in request.history_dates]
        last_date = history_dates[-1]
        
        # Infer frequency (e.g. monthly vs daily)
        freq_days = 30
        if len(history_dates) > 1:
            diff = (history_dates[-1] - history_dates[-2]).days
            if diff > 0:
                freq_days = diff

        # Generate future prediction nodes
        points = []
        for i in range(request.horizon):
            pred_date = last_date + timedelta(days=freq_days * (i + 1))
            points.append(PredictionPoint(
                date=pred_date.isoformat(),
                value=round(float(preds[i]), 2),
                upper_bound=round(float(upper[i]), 2),
                lower_bound=round(float(lower[i]), 2)
            ))

        # 3. Trend classification
        trend = "Flat"
        if preds[-1] > request.history_values[-1] * 1.05:
            trend = "Increasing"
        elif preds[-1] < request.history_values[-1] * 0.95:
            trend = "Decreasing"

        # 4. Drift detection
        drift_flag = ModelManager.detect_drift(request.history_values)

        # 5. Business explanation builder
        explanation = (
            f"Forecast compiled using {model_name}. Accuracy verified at MAPE {metrics['mape']}%. "
            f"Projected trend direction is classified as '{trend}'. "
            f"Dataset drift indicators: {'Detected significant variance drift' if drift_flag else 'No significant data drift detected'}."
        )

        response = ForecastResponse(
            id=uuid.uuid4(),
            forecast_values=points,
            trend=trend,
            seasonality="Monthly" if freq_days >= 28 and freq_days <= 31 else "None",
            model_used=model_name,
            accuracy_metrics=AccuracyMetrics(**metrics),
            business_explanation=explanation,
            confidence_score=round(max(0.1, 1.0 - (metrics["mape"] / 100.0)), 2),
            created_at=datetime.now(timezone.utc)
        )

        # 6. Save report history
        history = ForecastHistory(
            input_summary={"history_points": len(request.history_values), "horizon": request.horizon},
            forecast_json=response.model_dump(mode="json")
        )
        await self.repo.create(history)

        # 7. Cache prediction (TTL 1 hour)
        resp_dict = response.model_dump()
        resp_dict["created_at"] = resp_dict["created_at"].isoformat()
        cache.set(cache_key, resp_dict, ttl=3600)

        return response

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[ForecastHistory]:
        return await self.repo.list_history(skip, limit)
