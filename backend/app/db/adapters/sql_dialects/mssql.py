from app.db.adapters.sql_dialects.base import BaseDialectAdapter

class SQLServerDialectAdapter(BaseDialectAdapter):
    def quote_identifier(self, name: str) -> str:
        # SQL Server uses square brackets
        return f"[{name}]"

    def format_limit(self, limit: int) -> str:
        # SQL Server uses OFFSET FETCH or TOP, we use FETCH here for SQL Server 2012+
        return f"OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
