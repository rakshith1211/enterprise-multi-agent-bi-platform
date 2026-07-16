import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_query_execution_flow(client: AsyncClient):
    # 1. Create a SQLite connection profile
    conn_payload = {
        "name": "SQLite Exec DB",
        "database_type": "sqlite",
        "database_name": ":memory:",
        "environment": "Development"
    }
    
    conn_resp = await client.post("/api/v1/connections", json=conn_payload)
    assert conn_resp.status_code == 201
    conn_id = conn_resp.json()["id"]

    # 2. Execute SELECT query
    exec_payload = {
        "sql": "SELECT 42 AS answer, 'hello' AS text_val",
        "connection_id": conn_id,
        "parameters": {},
        "timeout_seconds": 15
    }
    
    resp = await client.post("/api/v1/query/execute", json=exec_payload)
    assert resp.status_code == 200
    res = resp.json()
    
    # Assert normalized response columns and rows mapping
    assert res["columns"] == ["answer", "text_val"]
    assert res["row_count"] == 1
    assert res["rows"][0]["answer"] == 42
    assert res["rows"][0]["text_val"] == "hello"
    assert res["data_types"]["answer"] == "Integer"
    assert res["data_types"]["text_val"] == "String"
    assert res["execution_time_ms"] >= 0
    assert "sqlite" in res["metadata"]["dialect"]

    # 3. Test caching (repeat execution)
    cached_resp = await client.post("/api/v1/query/execute", json=exec_payload)
    assert cached_resp.status_code == 200
    assert cached_resp.json()["rows"] == res["rows"]

    # 4. Fetch history log
    hist_resp = await client.get("/api/v1/query/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
    assert hist_resp.json()[0]["sql_query"] == exec_payload["sql"]

    # 5. Fetch telemetry metrics
    metrics_resp = await client.get("/api/v1/query/metrics")
    assert metrics_resp.status_code == 200
    assert metrics_resp.json()["total_queries"] >= 1
    assert metrics_resp.json()["avg_latency_ms"] > 0

    # 6. Test block unsafe injection query (fails SELECT-only validation)
    unsafe_payload = {
        "sql": "DROP TABLE sales",
        "connection_id": conn_id
    }
    unsafe_resp = await client.post("/api/v1/query/execute", json=unsafe_payload)
    assert unsafe_resp.status_code == 400
    
    # Verify failure is logged in history
    hist_resp2 = await client.get("/api/v1/query/history")
    assert any(h["status"] == "failed" for h in hist_resp2.json())

@pytest.mark.asyncio
async def test_query_validation_endpoint(client: AsyncClient):
    # Safe SELECT
    resp = await client.post("/api/v1/query/validate", json={"sql": "SELECT 1"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # Unsafe INSERT
    resp = await client.post("/api/v1/query/validate", json={"sql": "INSERT INTO t VALUES (1)"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "failed"
