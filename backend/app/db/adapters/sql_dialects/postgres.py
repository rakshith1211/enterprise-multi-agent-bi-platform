from app.db.adapters.sql_dialects.base import BaseDialectAdapter

class PostgresDialectAdapter(BaseDialectAdapter):
    def quote_identifier(self, name: str) -> str:
        # PostgreSQL uses double quotes
        return f'"{name}"'

    def format_limit(self, limit: int) -> str:
        return f"LIMIT {limit}"
