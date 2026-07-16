from app.db.adapters.base import BaseDatabaseAdapter
from app.db.adapters.postgres import PostgresAdapter
from app.db.adapters.mysql import MySQLAdapter
from app.db.adapters.sqlite import SQLiteAdapter
from app.db.adapters.duckdb import DuckDBAdapter
from app.db.adapters.mssql import SQLServerAdapter
from app.db.adapters.oracle import OracleAdapter
from typing import Dict, Any

class DatabaseAdapterFactory:
    @staticmethod
    def get_adapter(db_type: str, connection_details: Dict[str, Any], pool_params: Dict[str, Any] = None) -> BaseDatabaseAdapter:
        db_type = db_type.lower()
        if db_type == "postgresql":
            return PostgresAdapter(connection_details, pool_params)
        elif db_type == "mysql":
            return MySQLAdapter(connection_details, pool_params)
        elif db_type == "sqlite":
            return SQLiteAdapter(connection_details, pool_params)
        elif db_type == "duckdb":
            return DuckDBAdapter(connection_details, pool_params)
        elif db_type == "mssql":
            return SQLServerAdapter(connection_details, pool_params)
        elif db_type == "oracle":
            return OracleAdapter(connection_details, pool_params)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
