import os
import duckdb
from app.core.config import settings

def get_duckdb_conn():
    os.makedirs(os.path.dirname(settings.DUCKDB_PATH), exist_ok=True)
    return duckdb.connect(settings.DUCKDB_PATH)
