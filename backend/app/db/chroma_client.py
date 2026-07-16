import os
import chromadb
from app.core.config import settings

def get_chroma_client():
    if os.getenv("TESTING") == "true":
        return chromadb.EphemeralClient()
    os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
    return chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
