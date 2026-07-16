from app.db.adapters.sql_dialects.postgres import PostgresDialectAdapter
from app.db.adapters.sql_dialects.mysql import MySQLDialectAdapter
from app.db.adapters.sql_dialects.mssql import SQLServerDialectAdapter
from app.db.adapters.sql_dialects.oracle import OracleDialectAdapter
from app.db.adapters.sql_dialects.sqlite import SQLiteDialectAdapter
from app.db.adapters.sql_dialects.duckdb import DuckDBDialectAdapter
from app.db.adapters.sql_dialects.base import BaseDialectAdapter

class DialectAdapterFactory:
    @staticmethod
    def get_adapter(dialect: str) -> BaseDialectAdapter:
        d = dialect.lower()
        if d == "postgresql":
            return PostgresDialectAdapter()
        elif d == "mysql":
            return MySQLDialectAdapter()
        elif d == "mssql":
            return SQLServerDialectAdapter()
        elif d == "oracle":
            return OracleDialectAdapter()
        elif d == "sqlite":
            return SQLiteDialectAdapter()
        elif d == "duckdb":
            return DuckDBDialectAdapter()
        else:
            raise ValueError(f"Unsupported SQL dialect: {dialect}")
