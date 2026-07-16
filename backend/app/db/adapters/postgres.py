from app.db.adapters.base import BaseDatabaseAdapter
from typing import Dict, Any

class PostgresAdapter(BaseDatabaseAdapter):
    def get_dialect_name(self) -> str:
        return "postgresql"

    def get_connection_string(self) -> str:
        if self.connection_details.get("connection_string"):
            return self.connection_details["connection_string"]
        user = self.connection_details["username"]
        pwd = self.connection_details["password"]
        host = self.connection_details["host"]
        port = self.connection_details.get("port", 5432)
        db = self.connection_details["database_name"]
        return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
