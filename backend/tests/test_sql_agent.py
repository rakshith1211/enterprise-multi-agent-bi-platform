import pytest
from httpx import AsyncClient
from app.services.sql_validator import SQLValidator
from app.services.sql_optimizer import SQLOptimizer

def test_sql_validator_security():
    # Safe SELECT query
    assert SQLValidator.validate_safety("SELECT total_sales FROM sales WHERE region = :param_0 LIMIT 1000;") is True

    # Reject Insert/Delete DML
    assert SQLValidator.validate_safety("INSERT INTO sales (amount) VALUES (100)") is False
    assert SQLValidator.validate_safety("DELETE FROM sales") is False

    # Reject DDL
    assert SQLValidator.validate_safety("DROP TABLE sales") is False

    # Reject Multiple Statements (semicolon injection)
    assert SQLValidator.validate_safety("SELECT * FROM sales; DROP TABLE users;") is False

    # Reject Unsafe Functions
    assert SQLValidator.validate_safety("SELECT pg_sleep(10)") is False

def test_sql_optimizer():
    # Prune unnecessary joins
    required = ["sales"]
    joins = ["JOIN users ON sales.user_id = users.id", "JOIN products ON sales.prod_id = products.id"]
    pruned = SQLOptimizer.prune_joins(required, joins)
    assert len(pruned) == 0  # Since only 1 table is required, no joins are needed

    # Parameterize filters
    filters = [{"column": "region", "operator": "=", "value": "South"}]
    clauses, params = SQLOptimizer.parameterize_filters(filters)
    assert clauses[0] == "region = :param_0"
    assert params["param_0"] == "South"

@pytest.mark.asyncio
async def test_sql_generation_flow(client: AsyncClient):
    # Post Query Plan
    payload = {
        "database_type": "postgresql",
        "metric": "Revenue",
        "aggregation": "SUM",
        "dimensions": ["month"],
        "filters": [
            {"column": "region", "operator": "=", "value": "South"}
        ],
        "required_tables": ["sales"],
        "required_columns": ["total_sales", "month"],
        "business_rules": ["Exclude cancelled orders"]
    }
    
    resp = await client.post("/api/v1/sql/generate", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    
    # Verify SQL query structure
    sql = res["sql"]
    assert "SELECT" in sql
    assert '"total_sales"' in sql
    assert '"sales"' in sql
    assert "SUM" in sql
    assert "LIMIT" in sql
    
    # Parameter bindings
    assert res["parameters"]["param_0"] == "South"
    assert res["parameters"]["param_1"] == "Cancelled"  # Injected business rule parameter
    assert res["dialect"] == "postgresql"
    assert "explainability" in res

    # Verify history is populated
    hist_resp = await client.get("/api/v1/sql/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1
    assert hist_resp.json()[0]["sql_query"] == sql

@pytest.mark.asyncio
async def test_sql_validation_endpoint(client: AsyncClient):
    # Valid SELECT
    resp = await client.post("/api/v1/sql/validate", json={"sql": "SELECT * FROM sales"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # Invalid DDL
    resp = await client.post("/api/v1/sql/validate", json={"sql": "DROP TABLE sales"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "failed"
