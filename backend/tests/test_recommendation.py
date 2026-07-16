import pytest
from httpx import AsyncClient
from app.services.recommendation.opportunity_engine import OpportunityEngine
from app.services.recommendation.risk_engine import RiskEngine

def test_opportunity_heuristics():
    analytics = {"kpis": {"profit_margin": 30.0}}
    forecast = {"trend": "Increasing"}
    rules = ["Corporate margin standards: high margins preferred."]

    items = OpportunityEngine.detect_opportunities(analytics, forecast, rules)
    assert len(items) == 2
    assert any(i.type == "Revenue Optimization" for i in items)
    assert any(i.type == "Pricing Optimization" for i in items)

def test_risk_heuristics():
    analytics = {"outliers": [{"column": "revenue", "value": 99999.0}, {"column": "cost", "value": 44444.0}]}
    forecast = {"trend": "Decreasing"}
    rules = []

    items = RiskEngine.evaluate_risks(analytics, forecast, rules)
    assert len(items) == 2
    assert any(i.type == "Customer Retention" for i in items)
    assert any(i.type == "Risk Alerts" for i in items)

@pytest.mark.asyncio
async def test_recommendation_agent_endpoint(client: AsyncClient):
    payload = {
        "analytics_summary": {
            "kpis": {"profit_margin": 12.0},
            "outliers": []
        },
        "forecast_summary": {
            "trend": "Increasing"
        },
        "business_rules": []
    }

    resp = await client.post("/api/v1/recommendation/generate", json=payload)
    assert resp.status_code == 200
    res = resp.json()

    assert len(res["recommendations"]) == 1
    assert res["recommendations"][0]["type"] == "Revenue Optimization"
    assert res["recommendations"][0]["priority"] == "High"
    assert "revenue" in res["recommendations"][0]["affected_kpis"]
    assert "Sales" in res["recommendations"][0]["affected_departments"]
    assert len(res["recommendations"][0]["suggested_actions"]) >= 1

    # Baseline fallback validation
    baseline_payload = {
        "analytics_summary": {"kpis": {}, "outliers": []},
        "forecast_summary": {"trend": "Flat"},
        "business_rules": []
    }
    base_resp = await client.post("/api/v1/recommendation/generate", json=baseline_payload)
    assert base_resp.status_code == 200
    base_res = base_resp.json()
    assert base_res["recommendations"][0]["type"] == "Operational Efficiency"
    assert base_res["recommendations"][0]["priority"] == "Low"

    # History validation
    hist_resp = await client.get("/api/v1/recommendation/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
