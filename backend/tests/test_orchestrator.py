import pytest
import uuid
from httpx import AsyncClient
from app.services.orchestrator.graph_compiler import compile_agent_workflow
from app.services.orchestrator.state import AgentState

def test_graph_compilation():
    # Verify graph can compile and registers nodes
    graph = compile_agent_workflow(None)
    assert len(graph.graph.nodes) == 9
    assert "planner" in graph.graph.nodes
    assert "sql_agent" in graph.graph.nodes

@pytest.mark.asyncio
async def test_workflow_orchestration_flow(client: AsyncClient):
    # 1. Register connection
    conn_payload = {
        "name": "SQLite Orchestrator DB",
        "database_type": "sqlite",
        "database_name": ":memory:",
        "environment": "Development"
    }
    conn_resp = await client.post("/api/v1/connections", json=conn_payload)
    assert conn_resp.status_code == 201
    conn_id = conn_resp.json()["id"]

    # 2. Run workflow request (contains 'month' in user query to trigger forecast route)
    workflow_payload = {
        "user_query": "show monthly trends of sales",
        "connection_id": conn_id,
        "generate_report": True
    }

    resp = await client.post("/api/v1/workflow/run", json=workflow_payload)
    assert resp.status_code == 200
    res = resp.json()

    # Verify state keys
    assert res["status"] == "success"
    assert "planner" in res["trace"]
    assert "sql_agent" in res["trace"]
    assert "execution" in res["trace"]
    assert "analytics" in res["trace"]
    assert "visualization" in res["trace"]
    assert "forecast" in res["trace"]
    assert "recommendation" in res["trace"]
    assert "report" in res["trace"]
    assert "aggregator" in res["trace"]

    assert res["sql"] is not None
    assert "columns" in res["query_results"]
    assert "kpis" in res["analytics"]
    assert "plotly_spec" in res["visualization"]
    assert len(res["forecast"]["forecast_values"]) > 0
    assert len(res["recommendations"]["recommendations"]) > 0
    assert res["report"]["id"] is not None
    
    # 3. Test chat endpoint redirects similarly
    chat_resp = await client.post("/api/v1/workflow/chat", json=workflow_payload)
    assert chat_resp.status_code == 200
    assert chat_resp.json()["status"] == "success"

    # 4. Get Status
    workflow_id = res["id"]
    status_resp = await client.get(f"/api/v1/workflow/status/{workflow_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["trace"] == res["trace"]

    # 5. List history
    hist_resp = await client.get("/api/v1/workflow/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
