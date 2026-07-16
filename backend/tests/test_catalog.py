import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_semantic_catalog_flow(client: AsyncClient):
    # 1. Create Domain
    domain_payload = {
        "name": "Finance Domain",
        "description": "Financial metrics and datasets"
    }
    resp = await client.post("/api/v1/catalog/domains", json=domain_payload)
    assert resp.status_code == 201
    domain_id = resp.json()["id"]

    # 2. Create Glossary
    glossary_payload = {
        "name": "Corporate Glossary",
        "description": "Glossary for standard corporate terms",
        "domain_id": domain_id
    }
    resp = await client.post("/api/v1/catalog/glossaries", json=glossary_payload)
    assert resp.status_code == 201
    glossary_id = resp.json()["id"]

    # 3. Create Business Term with KPIs, Rules, and Mappings
    term_payload = {
        "name": "GMV",
        "description": "Gross Merchandise Value represents the total retail value of merchandise sold.",
        "glossary_id": glossary_id,
        "synonyms": ["Gross Revenue", "Gross Sales", "Sales Value"],
        "tags": ["financial", "sales", "kpi"],
        "kpis": [
            {
                "name": "GMV Growth Rate",
                "formula": "(GMV_Current - GMV_Previous) / GMV_Previous",
                "description": "Growth rate of GMV year-over-year"
            }
        ],
        "rules": [
            {
                "name": "GMV Calculation Rule",
                "rule_definition": "Exclude orders with status 'cancelled' or 'returned'.",
                "description": "Standard business rule for GMV calculation filters"
            }
        ],
        "column_mappings": [
            {
                "connection_id": str(uuid.uuid4()),
                "schema_name": "sales",
                "table_name": "orders",
                "column_name": "gross_merchandise_value"
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

    resp = await client.post("/api/v1/catalog/terms", json=term_payload)
    assert resp.status_code == 201
    term_id = resp.json()["id"]
    assert resp.json()["name"] == "GMV"
    assert len(resp.json()["synonyms"]) == 3
    assert len(resp.json()["kpis"]) == 1
    assert len(resp.json()["rules"]) == 1
    assert len(resp.json()["column_mappings"]) == 1

    # 4. Search terms
    # exact
    resp = await client.get("/api/v1/catalog/search?q=GMV")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert results[0]["name"] == "GMV"
    assert results[0]["confidence"] > 0.0
    assert "explainability" in results[0]

    # 5. Build AI Context for future SQL Generator Agent
    resp = await client.get("/api/v1/catalog/context?q=Gross Sales")
    assert resp.status_code == 200
    context = resp.json()
    assert "business_terms" in context
    assert len(context["business_terms"]) >= 1
    assert context["business_terms"][0]["name"] == "GMV"
    assert "kpis" in context
    assert "business_rules" in context
    assert "mappings" in context
    assert len(context["mappings"]["columns"]) >= 1
    assert context["mappings"]["columns"][0]["column"] == "gross_merchandise_value"

    # 6. Update Term (triggers version increment)
    resp = await client.put(f"/api/v1/catalog/terms/{term_id}", json={
        "description": "Updated GMV description representing total checkout transactions value."
    })
    assert resp.status_code == 200
    assert resp.json()["version"] == 2
    assert resp.json()["description"] == "Updated GMV description representing total checkout transactions value."

    # 7. Add Data Lineage
    lineage_payload = {
        "source_connection_id": str(uuid.uuid4()),
        "source_schema": "raw_db",
        "source_table": "transactions",
        "source_column": "amount",
        "target_schema": "sales",
        "target_table": "orders",
        "target_column": "gross_merchandise_value",
        "transformation_rule": "Sum of all order items price minus discounts."
    }
    resp = await client.post("/api/v1/catalog/lineage", json=lineage_payload)
    assert resp.status_code == 201
    assert resp.json()["source_table"] == "transactions"

    # List Lineage
    resp = await client.get("/api/v1/catalog/lineage")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # 8. Delete Term
    resp = await client.delete(f"/api/v1/catalog/terms/{term_id}")
    assert resp.status_code == 204
