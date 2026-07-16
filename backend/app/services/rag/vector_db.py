from typing import Dict, Any, List
import chromadb
from chromadb.utils import embedding_functions
from app.db.chroma_client import get_chroma_client

class VectorStoreManager:
    def __init__(self):
        self.chroma = get_chroma_client()
        # Pluggable embedding providers wrapper
        ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.chroma.get_or_create_collection(
            name="rag_knowledge_base",
            embedding_function=ef
        )

    def upsert_chunks(self, document_name: str, chunks: List[Dict[str, Any]], global_meta: Dict[str, Any]):
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = f"doc:{document_name}:c{chunk['chunk_index']}"
            meta = dict(global_meta)
            meta.update({
                "document_name": document_name,
                "chunk_index": chunk["chunk_index"],
                "strategy": chunk["strategy"]
            })
            # Ensure values are simple types for ChromaDB
            meta_clean = {k: (str(v) if isinstance(v, (list, dict)) else v) for k, v in meta.items()}
            
            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append(meta_clean)
            
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query_semantic(self, query: str, limit: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Map filters to ChromaDB structure (e.g. {"author": "John"} or similar)
        where_clause = {}
        if filters:
            clean_filters = {k: v for k, v in filters.items() if v is not None}
            if len(clean_filters) == 1:
                where_clause = clean_filters
            elif len(clean_filters) > 1:
                where_clause = {"$and": [{k: v} for k, v in clean_filters.items()]}
            
        res = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where_clause if where_clause else None
        )
        
        results = []
        if res and res.get("ids") and len(res["ids"]) > 0 and len(res["ids"][0]) > 0:
            ids = res["ids"][0]
            docs = res.get("documents", [])[0] if res.get("documents") and len(res["documents"]) > 0 else [""] * len(ids)
            metadatas = res.get("metadatas", [])[0] if res.get("metadatas") and len(res["metadatas"]) > 0 else [{}] * len(ids)
            distances = res.get("distances", [])[0] if res.get("distances") and len(res["distances"]) > 0 else [0.0] * len(ids)
            
            for i in range(len(ids)):
                dist = distances[i]
                confidence = round(1.0 / (1.0 + dist), 2)
                results.append({
                    "id": ids[i],
                    "text": docs[i],
                    "metadata": metadatas[i],
                    "score": confidence
                })
        return results

    def delete_document_chunks(self, document_name: str):
        # Delete using metadata query filter match
        self.collection.delete(
            where={"document_name": document_name}
        )
