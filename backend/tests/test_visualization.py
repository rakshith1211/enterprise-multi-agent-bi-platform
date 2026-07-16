import pytest
from httpx import AsyncClient
from app.services.visualization.recommendation_engine import ChartRecommendationEngine
from app.services.visualization.spec_compilers import SpecCompilers

def test_chart_recommendations():
    # 1. Time-series temporal dataset -> Line Chart
    cols = ["month", "sales"]
    rows = [{"month": "Jan", "sales": 100}, {"month": "Feb", "sales": 120}]
    primary, alts = ChartRecommendationEngine.recommend(cols, rows)
    assert primary.chart_type == "Line"
    assert any(a.chart_type == "Bar" for a in alts)

    # 2. Numeric correlation dataset -> Scatter Chart
    cols_scatter = ["height", "weight"]
    rows_scatter = [{"height": 180, "weight": 75}, {"height": 165, "weight": 60}]
    primary_sc, _ = ChartRecommendationEngine.recommend(cols_scatter, rows_scatter)
    assert primary_sc.chart_type == "Scatter"

    # 3. Categorical comparison dataset -> Bar Chart
    cols_bar = ["category", "sales"]
    rows_bar = [{"category": "Apparel", "sales": 100}, {"category": "Electronics", "sales": 200}]
    primary_b, _ = ChartRecommendationEngine.recommend(cols_bar, rows_bar)
    assert primary_b.chart_type == "Bar"

def test_spec_compilers():
    cols = ["category", "sales"]
    rows = [{"category": "A", "sales": 10}, {"category": "B", "sales": 20}]
    
    plotly = SpecCompilers.compile_plotly("Bar", cols, rows)
    assert len(plotly["data"]) == 1
    assert plotly["data"][0]["type"] == "bar"
    assert "title" in plotly["layout"]

    recharts = SpecCompilers.compile_recharts("Bar", cols, rows)
    assert recharts["xAxisKey"] == "category"
    assert recharts["yAxisKeys"] == ["sales"]
    assert len(recharts["data"]) == 2

    vega = SpecCompilers.compile_vega_lite("Bar", cols, rows)
    assert vega["mark"] == "bar"
    assert vega["encoding"]["x"]["field"] == "category"

    echarts = SpecCompilers.compile_echarts("Bar", cols, rows)
    assert len(echarts["series"]) == 1
    assert echarts["xAxis"]["data"] == ["A", "B"]

@pytest.mark.asyncio
async def test_visualization_agent_endpoint(client: AsyncClient):
    payload = {
        "columns": ["month", "sales", "profit"],
        "rows": [
            {"month": "Jan", "sales": 1000, "profit": 200},
            {"month": "Feb", "sales": 1200, "profit": 240},
            {"month": "Mar", "sales": 1100, "profit": 220}
        ]
    }
    
    resp = await client.post("/api/v1/visualization/spec", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    
    # Assert specifications compiled
    assert res["primary_recommendation"]["chart_type"] == "Line"
    assert "plotly_spec" in res
    assert "recharts_spec" in res
    assert "vega_lite_spec" in res
    assert "echarts_spec" in res
    
    # Accessibility checks
    assert "accessibility" in res
    assert res["accessibility"]["aria_label"] is not None
    assert len(res["accessibility"]["color_palette_hints"]) > 0

    # History validation
    hist_resp = await client.get("/api/v1/visualization/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
