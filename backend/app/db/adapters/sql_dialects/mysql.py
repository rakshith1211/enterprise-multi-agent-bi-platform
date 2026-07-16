from app.db.adapters.sql_dialects.base import BaseDialectAdapter

class MySQLDialectAdapter(BaseDialectAdapter):
    def quote_identifier(self, name: str) -> str:
        # MySQL uses backticks
        return f"`{name}`"

    def format_limit(self, limit: int) -> str:
        return f"LIMIT {limit}"
