from app.db.adapters.sql_dialects.base import BaseDialectAdapter

class OracleDialectAdapter(BaseDialectAdapter):
    def quote_identifier(self, name: str) -> str:
        # Oracle uses double quotes and defaults to upper case
        return f'"{name.upper()}"'

    def format_limit(self, limit: int) -> str:
        return f"FETCH FIRST {limit} ROWS ONLY"
