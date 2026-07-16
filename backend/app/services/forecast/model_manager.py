import numpy as np
from typing import List, Dict, Any
import logging

from app.services.forecast.forecast_engine import ARIMAPredictor, MLPredictor

logger = logging.getLogger(__name__)

class ModelManager:
    @classmethod
    def select_and_forecast(cls, history: List[float], horizon: int) -> tuple[str, List[float], List[float], List[float], Dict[str, float]]:
        # 1. Validation split (80/20 split)
        split_idx = int(len(history) * 0.8)
        if split_idx < 4:
            # Too short dataset, default to Random Forest on full history
            logger.info("Dataset too small for train/test split. Defaulting to Random Forest.")
            preds, upper, lower, metrics = MLPredictor.forecast(history, horizon)
            return "Random Forest Regressor", preds, upper, lower, metrics
            
        train = history[:split_idx]
        val = history[split_idx:]
        
        # Test ARIMA on validation slice
        arima_preds, _, _, arima_metrics = ARIMAPredictor.forecast(train, len(val))
        arima_mape = arima_metrics["mape"]
        
        # Test ML on validation slice
        ml_preds, _, _, ml_metrics = MLPredictor.forecast(train, len(val))
        ml_mape = ml_metrics["mape"]

        # 2. Select best model based on validation MAPE
        if arima_mape <= ml_mape:
            logger.info(f"ARIMA selected (Validation MAPE: {arima_mape}% vs ML MAPE: {ml_mape}%)")
            preds, upper, lower, metrics = ARIMAPredictor.forecast(history, horizon)
            return "ARIMA (1,1,0)", preds, upper, lower, metrics
        else:
            logger.info(f"Random Forest selected (Validation MAPE: {ml_mape}% vs ARIMA MAPE: {arima_mape}%)")
            preds, upper, lower, metrics = MLPredictor.forecast(history, horizon)
            return "Random Forest Regressor", preds, upper, lower, metrics

    @staticmethod
    def detect_drift(history: List[float]) -> bool:
        """
        Detects if the latter portion of history deviates significantly 
        from initial trend boundaries.
        """
        if len(history) < 6:
            return False
            
        mid = len(history) // 2
        p1 = history[:mid]
        p2 = history[mid:]
        
        m1 = np.mean(p1)
        std1 = np.std(p1)
        if std1 == 0:
            return False
            
        m2 = np.mean(p2)
        # Drift flagged if mean shift > 2 standard deviations
        return bool(abs(m2 - m1) > 2.0 * std1)
