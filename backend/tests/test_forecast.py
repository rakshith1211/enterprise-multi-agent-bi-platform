import pytest
from httpx import AsyncClient
from app.services.forecast.forecast_engine import ARIMAPredictor, MLPredictor
from app.services.forecast.model_manager import ModelManager

def test_arima_and_ml_predictions():
    history = [10.0, 12.0, 11.0, 13.0, 15.0, 14.0, 16.0, 18.0]
    horizon = 4

    # 1. Test ARIMA
    preds, upper, lower, metrics = ARIMAPredictor.forecast(history, horizon)
    assert len(preds) == horizon
    assert len(upper) == horizon
    assert metrics["mape"] >= 0.0

    # 2. Test ML
    preds_ml, upper_ml, lower_ml, metrics_ml = MLPredictor.forecast(history, horizon)
    assert len(preds_ml) == horizon
    assert upper_ml[0] >= preds_ml[0]

def test_model_selection_and_drift():
    history_drift = [10, 11, 10, 12, 11, 100, 105, 99, 102, 101]
    
    # Check drift detection
    assert ModelManager.detect_drift(history_drift) is True
    
    # Check model selection (long history splits)
    model, _, _, _, _ = ModelManager.select_and_forecast(history_drift, 3)
    assert model in ["ARIMA (1,1,0)", "Random Forest Regressor"]

@pytest.mark.asyncio
async def test_forecast_agent_endpoint(client: AsyncClient):
    payload = {
        "history_dates": [
            "2026-01-01T00:00:00Z", "2026-02-01T00:00:00Z", "2026-03-01T00:00:00Z",
            "2026-04-01T00:00:00Z", "2026-05-01T00:00:00Z", "2026-06-01T00:00:00Z",
            "2026-07-01T00:00:00Z", "2026-08-01T00:00:00Z", "2026-09-01T00:00:00Z",
            "2026-10-01T00:00:00Z", "2026-11-01T00:00:00Z", "2026-12-01T00:00:00Z"
        ],
        "history_values": [100.0, 110.0, 105.0, 120.0, 125.0, 130.0, 140.0, 135.0, 150.0, 155.0, 160.0, 170.0],
        "horizon": 6
    }
    
    resp = await client.post("/api/v1/forecast/predict", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    
    # Assert prediction values size matches horizon
    assert len(res["forecast_values"]) == 6
    assert res["forecast_values"][0]["upper_bound"] >= res["forecast_values"][0]["value"]
    
    # Metrics
    assert "accuracy_metrics" in res
    assert res["accuracy_metrics"]["mape"] >= 0
    assert "model_used" in res
    assert "business_explanation" in res

    # History validation
    hist_resp = await client.get("/api/v1/forecast/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
