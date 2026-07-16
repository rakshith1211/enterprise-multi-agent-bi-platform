import pytest
import uuid
from httpx import AsyncClient
from app.services.rag.chunker import RAGChunker

def test_rag_chunker_fixed():
    text = "Google Antigravity is a pair programming agentic platform. It builds clean code structures."
    chunks = RAGChunker.chunk_fixed(text, chunk_size=5, overlap=1)
    assert len(chunks) >= 2
    assert chunks[0]["strategy"] == "fixed-size"

def test_rag_chunker_semantic():
    text = "Google Antigravity is a platform. It runs on Windows. Python is used."
    chunks = RAGChunker.chunk_semantic(text)
    assert len(chunks) >= 1
    assert chunks[0]["strategy"] == "semantic"

@pytest.mark.asyncio
async def test_rag_ingestion_and_retrieval(client: AsyncClient):
    # 1. Upload/Ingest Markdown document
    ingest_payload = {
        "document_name": "corporate_analytics_policies.md",
        "file_type": "md",
        "text_content": "Enterprise analytics policies mandate that SQL queries must use projected fields only. SELECT * is strictly banned.",
        "metadata": {
            "author": "Alice",
            "permissions": "public",
            "business_domain": "Engineering",
            "chunk_strategy": "recursive"
        }
    }
    
    ingest_resp = await client.post("/api/v1/rag/ingest", json=ingest_payload)
    assert ingest_resp.status_code == 201
    ingest_data = ingest_resp.json()
    assert ingest_data["document_name"] == "corporate_analytics_policies.md"
    assert ingest_data["chunks_count"] >= 1
    assert ingest_data["version"] == 1
    assert ingest_data["status"] == "ingested"

    # 2. Query/Retrieve Context with matching filter
    retrieve_payload = {
        "query": "Is SELECT * allowed in SQL queries?",
        "limit": 3,
        "filters": {
            "author": "Alice"
        },
        "role": "viewer"
    }
    
    retrieve_resp = await client.post("/api/v1/rag/retrieve", json=retrieve_payload)
    assert retrieve_resp.status_code == 200
    retrieve_data = retrieve_resp.json()
    assert "corporate_analytics_policies.md" in retrieve_data["context_prompt"]
    assert len(retrieve_data["citations"]) >= 1
    assert retrieve_data["citations"][0]["document_name"] == "corporate_analytics_policies.md"
    assert retrieve_data["citations"][0]["score"] > 0
    assert retrieve_data["explainability"]["retrieved_nodes_count"] >= 1

    # 3. Retrieve with restricted permissions filter
    retrieve_restricted_payload = {
        "query": "Is SELECT * allowed?",
        "limit": 3,
        "filters": {
            "permissions": "private" # Should find nothing since we uploaded public
        },
        "role": "admin"
    }
    retrieve_restricted_resp = await client.post("/api/v1/rag/retrieve", json=retrieve_restricted_payload)
    assert retrieve_restricted_resp.status_code == 200
    assert len(retrieve_restricted_resp.json()["citations"]) == 0

    # 4. Ingest new version (incremental versioning test)
    ingest_payload_v2 = dict(ingest_payload)
    ingest_payload_v2["text_content"] = ingest_payload["text_content"] + " Version two overrides."
    
    ingest_resp_v2 = await client.post("/api/v1/rag/ingest", json=ingest_payload_v2)
    assert ingest_resp_v2.status_code == 201
    assert ingest_resp_v2.json()["version"] == 2

    # 5. Get History List
    hist_resp = await client.get("/api/v1/rag/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1

    # 6. Delete document
    doc_id = ingest_resp_v2.json()["id"]
    delete_resp = await client.delete(f"/api/v1/rag/document/{doc_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "deleted"
