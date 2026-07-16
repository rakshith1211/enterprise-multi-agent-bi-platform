import pytest
import uuid
from httpx import AsyncClient
from app.services.intent_classifier import IntentClassifier
from app.services.time_intelligence import TimeIntelligence
from app.services.entity_extractor import EntityExtractor

def test_intent_classification():
    assert IntentClassifier.classify("forecast next 3 months revenue") == "forecast"
    assert IntentClassifier.classify("plot sales by region") == "visualization"
    assert IntentClassifier.classify("generate monthly PDF report") == "report_generation"
    assert IntentClassifier.classify("what columns are in database?") == "metadata_search"
    assert IntentClassifier.classify("show total sales") == "analytics"

def test_time_intelligence():
    res = TimeIntelligence.parse_time_range("show sales for last 6 months")
    assert res["raw_time_expression"] == "Last 6 Months"
    assert res["start_date"] is not None
    assert "interval 6 month" in res["sql_filter"]

    res_ytd = TimeIntelligence.parse_time_range("show YTD profits")
    assert res_ytd["raw_time_expression"] == "Year-to-Date"
    assert res_ytd["start_date"] is not None

def test_entity_extraction():
    entities = EntityExtractor.extract_entities("show monthly revenue for the South region")
    assert "Revenue" in entities["metrics"]
    assert "region" in entities["dimensions"]
    assert "month" in entities["dimensions"]
    assert len(entities["filters"]) == 1
    assert entities["filters"][0]["column"] == "region"
    assert entities["filters"][0]["value"] == "South"

@pytest.mark.asyncio
async def test_query_planner_flow(client: AsyncClient):
    # Setup prerequisite catalog mapping database data so planner returns matched tables/columns
    # 1. Create Domain
    domain_resp = await client.post("/api/v1/catalog/domains", json={"name": "Sales Domain"})
    domain_id = domain_resp.json()["id"]

    # 2. Create Glossary
    glossary_resp = await client.post("/api/v1/catalog/glossaries", json={
        "name": "Ecom Glossary",
        "domain_id": domain_id
    })
    glossary_id = glossary_resp.json()["id"]

    # 3. Create Term with Mappings
    term_payload = {
        "name": "Revenue",
        "description": "Total sales revenue from retail transactions",
        "glossary_id": glossary_id,
        "column_mappings": [
            {
                "connection_id": str(uuid.uuid4()),
                "schema_name": "sales",
                "table_name": "orders",
                "column_name": "total_sales"
            }
        ],
        "table_mappings": [
            {
                "connection_id": str(uuid.uuid4()),
                "schema_name": "sales",
                "table_name": "orders"
            }
        ]
    }
    await client.post("/api/v1/catalog/terms", json=term_payload)

    # 4. Generate plan
    plan_payload = {
        "user_query": "Show monthly revenue for the South region during the last 12 months."
    }
    resp = await client.post("/api/v1/planner/plan", json=plan_payload)
    assert resp.status_code == 200
    plan = resp.json()
    
    # Verify extended schema mappings
    assert plan["intent"] == "analytics"
    assert plan["complexity"] in ["Simple", "Medium", "Complex"]
    assert plan["recommended_agent"] == "SQL Agent"
    assert len(plan["execution_steps"]) >= 1
    assert plan["execution_steps"][0]["agent"] == "SQL Agent"
    assert plan["confidence"] > 0.0
    assert "cost_estimate" in plan
    assert plan["cost_estimate"]["sql_execution_ms"] > 0
    assert "explainability" in plan

    # 5. Fetch plan history
    hist_resp = await client.get("/api/v1/planner/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
    assert hist_resp.json()[0]["user_query"] == plan_payload["user_query"]
