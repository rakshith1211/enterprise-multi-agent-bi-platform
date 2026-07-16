import abc
from typing import List, Dict, Any

class BaseDialectAdapter(abc.ABC):
    @abc.abstractmethod
    def quote_identifier(self, name: str) -> str:
        pass

    @abc.abstractmethod
    def format_limit(self, limit: int) -> str:
        pass

    def format_table(self, table: str, schema: str = None) -> str:
        t = self.quote_identifier(table)
        if schema:
            return f"{self.quote_identifier(schema)}.{t}"
        return t

    def format_column(self, col: str, table: str = None) -> str:
        c = self.quote_identifier(col)
        if table:
            return f"{self.quote_identifier(table)}.{c}"
        return c
