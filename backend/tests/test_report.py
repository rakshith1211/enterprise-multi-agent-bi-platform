import pytest
from httpx import AsyncClient
from app.services.report.pdf_generator import PDFGenerator
from app.services.report.html_generator import HTMLGenerator

def test_pdf_rendering():
    title = "Monthly Performance Review"
    analytics = {"kpis": {"AOV": 150.0, "Revenue": 50000.0}}
    forecast = {"trend": "Increasing", "model_used": "ARIMA"}
    recs = {"recommendations": [{"title": "Incentivize top buyers", "priority": "High", "suggested_actions": ["send emails"]}]}

    pdf_bytes = PDFGenerator.generate(title, analytics, forecast, recs)
    assert len(pdf_bytes) > 0
    # PDF signature check
    assert pdf_bytes.startswith(b"%PDF")

def test_html_and_markdown_rendering():
    title = "Test Doc"
    analytics = {"kpis": {"churn": 2.5}}
    forecast = {"trend": "Flat", "model_used": "Random Forest"}
    recs = {"recommendations": []}

    html = HTMLGenerator.generate_html(title, analytics, forecast, recs)
    assert "<html" in html
    assert "churn" in html

    md = HTMLGenerator.generate_markdown(title, analytics, forecast, recs)
    assert "# Test Doc" in md
    assert "churn" in md

@pytest.mark.asyncio
async def test_report_agent_endpoint(client: AsyncClient):
    payload = {
        "title": "Quarterly Financial Analysis",
        "template": "Executive Report",
        "analytics_data": {
            "kpis": {"AOV": 200.0, "profit_margin": 28.5},
            "outliers": []
        },
        "forecast_data": {
            "trend": "Increasing",
            "model_used": "ARIMA (1,1,0)"
        },
        "visualization_metadata": {},
        "recommendations_data": {
            "recommendations": [
                {"title": "Optimize High Profit Margin", "priority": "Medium", "suggested_actions": ["upsell premium"]}
            ]
        }
    }

    # 1. Generate Report
    resp = await client.post("/api/v1/reports/generate", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    assert res["title"] == "Quarterly Financial Analysis"
    assert "pdf" in res["formats_available"]
    report_id = res["id"]

    # 2. Download PDF
    pdf_resp = await client.get(f"/api/v1/reports/download/{report_id}?format=pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 0
    assert pdf_resp.content.startswith(b"%PDF")

    # 3. Download HTML
    html_resp = await client.get(f"/api/v1/reports/download/{report_id}?format=html")
    assert html_resp.status_code == 200
    assert html_resp.headers["content-type"] == "text/html; charset=utf-8"
    assert b"Quarterly Financial Analysis" in html_resp.content

    # 4. History check
    hist_resp = await client.get("/api/v1/reports/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
