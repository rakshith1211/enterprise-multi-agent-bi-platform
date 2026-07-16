import abc
import time
import logging
from typing import List, Dict, Any
from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

class BaseDatabaseAdapter(abc.ABC):
    def __init__(self, connection_details: Dict[str, Any], pool_params: Dict[str, Any] = None):
        self.connection_details = connection_details
        self.pool_params = pool_params or {}
        self.engine = None

    @abc.abstractmethod
    def get_connection_string(self) -> str:
        pass

    @abc.abstractmethod
    def get_dialect_name(self) -> str:
        pass

    def get_engine(self):
        if not self.engine:
            conn_str = self.get_connection_string()
            pool_size = self.pool_params.get("pool_size", 5)
            pool_timeout = self.pool_params.get("pool_timeout", 30)
            pool_recycle = self.pool_params.get("pool_recycle", 1800)
            max_overflow = self.pool_params.get("max_overflow", 10)
            
            dialect = self.get_dialect_name()
            if dialect in ["sqlite", "duckdb"]:
                self.engine = create_engine(conn_str, poolclass=NullPool)
            else:
                self.engine = create_engine(
                    conn_str,
                    pool_size=pool_size,
                    pool_timeout=pool_timeout,
                    pool_recycle=pool_recycle,
                    max_overflow=max_overflow
                )
        return self.engine

    def test_connection(self) -> float:
        """
        Tests connection and returns connection latency in milliseconds.
        """
        engine = self.get_engine()
        start = time.time()
        with engine.connect() as conn:
            # Dialect agnostic query
            dialect = self.get_dialect_name()
            if dialect == "oracle":
                conn.exec_driver_sql("SELECT 1 FROM DUAL")
            else:
                conn.exec_driver_sql("SELECT 1")
        latency = (time.time() - start) * 1000
        return latency

    def get_schemas(self) -> List[str]:
        engine = self.get_engine()
        inspector = inspect(engine)
        return inspector.get_schema_names()

    def get_tables(self, schema: str = None) -> List[str]:
        engine = self.get_engine()
        inspector = inspect(engine)
        return inspector.get_table_names(schema=schema)

    def get_views(self, schema: str = None) -> List[str]:
        engine = self.get_engine()
        inspector = inspect(engine)
        try:
            return inspector.get_view_names(schema=schema)
        except Exception:
            return []

    def get_columns(self, table_name: str, schema: str = None) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name, schema=schema)
        pk_constraint = inspector.get_pk_constraint(table_name, schema=schema)
        pk_columns = pk_constraint.get("constrained_columns", []) if pk_constraint else []
        
        result = []
        for col in columns:
            result.append({
                "name": col["name"],
                "data_type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default_value": str(col.get("default")) if col.get("default") is not None else None,
                "is_primary_key": col["name"] in pk_columns
            })
        return result

    def get_foreign_keys(self, table_name: str, schema: str = None) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        inspector = inspect(engine)
        try:
            return inspector.get_foreign_keys(table_name, schema=schema)
        except Exception:
            return []

    def get_indexes(self, table_name: str, schema: str = None) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        inspector = inspect(engine)
        try:
            indexes = inspector.get_indexes(table_name, schema=schema)
            result = []
            for idx in indexes:
                result.append({
                    "name": idx["name"],
                    "columns": idx["column_names"],
                    "unique": idx.get("unique", False)
                })
            return result
        except Exception:
            return []

    def get_unique_constraints(self, table_name: str, schema: str = None) -> List[Dict[str, Any]]:
        engine = self.get_engine()
        inspector = inspect(engine)
        try:
            constraints = inspector.get_unique_constraints(table_name, schema=schema)
            result = []
            for c in constraints:
                result.append({
                    "name": c["name"],
                    "columns": c["column_names"]
                })
            return result
        except Exception:
            return []

    def execute_query(self, sql: str, params: Dict[str, Any] = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Executes a SELECT query securely using parameter binding and returns column headers and rows list.
        """
        engine = self.get_engine()
        with engine.connect() as conn:
            import sqlalchemy
            stmt = sqlalchemy.text(sql)
            res = conn.execute(stmt, params or {})
            
            # Fetch keys (columns)
            columns = list(res.keys())
            
            # Fetch all rows mapped as dict
            rows = []
            for row in res.all():
                rows.append(dict(row._mapping))
                
            return {
                "columns": columns,
                "rows": rows
            }
