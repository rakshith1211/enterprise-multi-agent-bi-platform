import pytest
import sqlite3
import os
from httpx import AsyncClient
from app.core.crypto import encryptor

@pytest.mark.asyncio
async def test_encryption_decryption():
    plain = "secret_password"
    cipher = encryptor.encrypt(plain)
    assert cipher != plain
    assert encryptor.decrypt(cipher) == plain

@pytest.mark.asyncio
async def test_connection_validation(client: AsyncClient):
    # Invalid Port
    resp = await client.post("/api/v1/connections", json={
        "name": "Invalid Port DB",
        "database_type": "postgresql",
        "port": 99999
    })
    assert resp.status_code == 422

    # Invalid Engine type
    resp = await client.post("/api/v1/connections", json={
        "name": "Invalid Engine DB",
        "database_type": "mongodb"
    })
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_connection_lifecycle(client: AsyncClient):
    # 1. Create Connection
    payload = {
        "name": "Test Connection Lifecycle DB",
        "description": "Standard development SQLite database for unit test cycles",
        "database_type": "sqlite",
        "database_name": "test_lifecycle.db",
        "environment": "Development",
        "tags": ["testing", "local"]
    }
    resp = await client.post("/api/v1/connections", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    conn_id = data["id"]
    assert data["name"] == payload["name"]
    assert data["database_type"] == payload["database_type"]
    assert data["is_deleted"] is False

    # Try duplicate name
    resp = await client.post("/api/v1/connections", json=payload)
    assert resp.status_code == 400

    # 2. Get connection details
    resp = await client.get(f"/api/v1/connections/{conn_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == conn_id

    # 3. Search connection
    resp = await client.get("/api/v1/connections/search?q=Lifecycle")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # 4. Update connection
    resp = await client.put(f"/api/v1/connections/{conn_id}", json={
        "description": "Updated SQLite Description",
        "tags": ["testing", "local", "updated"]
    })
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated SQLite Description"

    # 5. Disable & Enable
    resp = await client.patch(f"/api/v1/connections/{conn_id}/disable")
    assert resp.status_code == 200
    assert resp.json()["status"] == "disabled"

    # Test health check when disabled
    resp = await client.get(f"/api/v1/connections/{conn_id}/health")
    assert resp.status_code == 500  # returns internal error for unhealthy/disabled status

    resp = await client.patch(f"/api/v1/connections/{conn_id}/enable")
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"

    # 6. Test connection transient logic
    resp = await client.post("/api/v1/connections/test", json={
        "database_type": "sqlite",
        "database_name": ":memory:"
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # 7. Health check on active SQLite DB
    resp = await client.get(f"/api/v1/connections/{conn_id}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

    # 8. Soft Delete
    resp = await client.delete(f"/api/v1/connections/{conn_id}")
    assert resp.status_code == 204

    # Verify not in list
    resp = await client.get("/api/v1/connections")
    conns = resp.json()
    assert not any(c["id"] == conn_id for c in conns)

    # 9. Restore
    resp = await client.post(f"/api/v1/connections/{conn_id}/restore")
    assert resp.status_code == 200
    assert resp.json()["is_deleted"] is False

@pytest.mark.asyncio
async def test_metadata_discovery(client: AsyncClient):
    db_file = "test_discovery.db"
    
    # Setup test table structure using sqlite3 natively
    if os.path.exists(db_file):
        os.remove(db_file)
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

    try:
        # 1. Register SQLite Connection details
        payload = {
            "name": "Discovery Target DB",
            "database_type": "sqlite",
            "database_name": db_file,
        }
        resp = await client.post("/api/v1/connections", json=payload)
        assert resp.status_code == 201
        conn_id = resp.json()["id"]

        # 2. Get Schemas
        resp = await client.get(f"/api/v1/connections/{conn_id}/schemas")
        assert resp.status_code == 200
        assert "main" in resp.json()

        # 3. Get Tables
        resp = await client.get(f"/api/v1/connections/{conn_id}/schemas/main/tables")
        assert resp.status_code == 200
        tables = resp.json()
        assert "users" in tables
        assert "orders" in tables

        # 4. Get Columns
        resp = await client.get(f"/api/v1/connections/{conn_id}/schemas/main/tables/users/columns")
        assert resp.status_code == 200
        columns = resp.json()
        
        # Verify schema details reflected
        id_col = next(c for c in columns if c["name"] == "id")
        assert id_col["is_primary_key"] is True
        assert id_col["data_type"] == "INTEGER"
        
        email_col = next(c for c in columns if c["name"] == "email")
        assert email_col["nullable"] is False

        # 5. Refresh entire catalog metadata
        resp = await client.post(f"/api/v1/connections/{conn_id}/refresh-metadata")
        assert resp.status_code == 200
        meta = resp.json()
        assert meta["status"] == "success"
        schema_map = meta["schema_map"]
        assert "main" in schema_map
        assert "users" in schema_map["main"]["tables"]
        assert "orders" in schema_map["main"]["tables"]

    finally:
        # Clean up db file
        if os.path.exists(db_file):
            os.remove(db_file)
