from app.db.adapters.base import BaseDatabaseAdapter
from typing import Dict, Any

class DuckDBAdapter(BaseDatabaseAdapter):
    def get_dialect_name(self) -> str:
        return "duckdb"

    def get_connection_string(self) -> str:
        if self.connection_details.get("connection_string"):
            return self.connection_details["connection_string"]
        db = self.connection_details["database_name"]
        if db == ":memory:":
            return "duckdb:///:memory:"
        return f"duckdb:///{db}"
