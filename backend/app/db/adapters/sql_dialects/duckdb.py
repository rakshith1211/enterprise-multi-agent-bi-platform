from app.db.adapters.sql_dialects.base import BaseDialectAdapter

class DuckDBDialectAdapter(BaseDialectAdapter):
    def quote_identifier(self, name: str) -> str:
        # DuckDB supports double quotes
        return f'"{name}"'

    def format_limit(self, limit: int) -> str:
        return f"LIMIT {limit}"
