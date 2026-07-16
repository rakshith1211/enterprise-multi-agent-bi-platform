import pytest
import pandas as pd
from httpx import AsyncClient
from app.services.analytics.data_quality import DataQualityEngine
from app.services.analytics.statistics_engine import StatisticsEngine
from app.services.analytics.kpi_engine import KPIEngine
from app.services.analytics.trend_engine import TrendEngine
from app.services.analytics.anomaly_detection import AnomalyEngine

def test_data_quality_math():
    df = pd.DataFrame([
        {"sales": 100, "region": "South"},
        {"sales": 200, "region": None},
        {"sales": 100, "region": "South"} # duplicate row
    ])
    quality = DataQualityEngine.evaluate(df)
    assert quality.missing_count == 1
    assert quality.duplicate_rows == 1
    assert quality.completeness_score == round(5/6, 4)

def test_descriptive_statistics():
    df = pd.DataFrame({"sales": [10, 20, 30, 40, 50]})
    stats = StatisticsEngine.calculate_stats(df)
    assert stats["sales"].mean == 30.0
    assert stats["sales"].median == 30.0
    assert stats["sales"].std_dev > 0.0

def test_trend_direction():
    df = pd.DataFrame({"revenue": [100, 150, 200, 250, 300]})
    trends = TrendEngine.calculate_trends(df)
    assert trends["revenue"].direction == "Upward"
    assert trends["revenue"].cagr > 0.0

def test_anomaly_z_score():
    # Regular values with a single huge outlier at the end
    df = pd.DataFrame({"revenue": [100]*10 + [1000]})
    anomalies = AnomalyEngine.detect_anomalies(df)
    assert len(anomalies) == 1
    assert anomalies[0].column == "revenue"
    assert anomalies[0].value == 1000.0

@pytest.mark.asyncio
async def test_analytics_agent_endpoint(client: AsyncClient):
    # Post a dataset
    payload = {
        "columns": ["month", "revenue", "profit", "customers"],
        "rows": [
            {"month": "Jan", "revenue": 1000.0, "profit": 200.0, "customers": 50},
            {"month": "Feb", "revenue": 1200.0, "profit": 240.0, "customers": 55},
            {"month": "Mar", "revenue": 1100.0, "profit": 220.0, "customers": 52},
            {"month": "Apr", "revenue": 1400.0, "profit": 310.0, "customers": 60},
            {"month": "May", "revenue": 1500.0, "profit": 350.0, "customers": 62},
            {"month": "Jun", "revenue": 1300.0, "profit": 270.0, "customers": 58},
            {"month": "Jul", "revenue": 1250.0, "profit": 260.0, "customers": 57},
            {"month": "Aug", "revenue": 1350.0, "profit": 280.0, "customers": 59},
            {"month": "Sep", "revenue": 1450.0, "profit": 300.0, "customers": 61},
            {"month": "Oct", "revenue": 1200.0, "profit": 250.0, "customers": 56},
            {"month": "Nov", "revenue": 1150.0, "profit": 230.0, "customers": 54},
            {"month": "Dec", "revenue": 9999.0, "profit": 2200.0, "customers": 65}
        ]
    }
    
    resp = await client.post("/api/v1/analytics/analyze", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    
    # Assert descriptive statistics
    assert "revenue" in res["statistics"]
    assert res["statistics"]["revenue"]["mean"] > 0
    
    # Assert KPIs calculated
    assert res["kpis"]["revenue"] == 23899.0
    assert res["kpis"]["profit"] == 5110.0
    assert res["kpis"]["average_order_value"] == round(23899.0 / 12, 2)
    
    # Assert Outliers
    assert len(res["outliers"]) == 2
    assert res["outliers"][0]["column"] == "revenue"
    assert res["outliers"][0]["value"] == 9999.0
    
    # Assert Insights
    assert len(res["insights"]) >= 1
    assert "explainability" in res
    assert res["confidence"] > 0.0

    # Test cache retrieval
    cache_resp = await client.post("/api/v1/analytics/analyze", json=payload)
    assert cache_resp.status_code == 200

    # Test list reports history
    hist_resp = await client.get("/api/v1/analytics/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
