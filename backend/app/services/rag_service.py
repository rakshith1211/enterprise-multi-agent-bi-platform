import uuid
import logging
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.rag import RAGDocumentHistory
from app.schemas.rag import (
    RAGIngestRequest, RAGUploadResponse, RAGRetrieveRequest, RAGRetrieveResponse, CitationNode
)
from app.db.repositories.rag import RAGRepository
from app.services.rag.loaders import DocumentLoaderFactory
from app.services.rag.chunker import RAGChunker
from app.services.rag.retriever import HybridRetriever
from app.services.rag.context_builder import ContextBuilder
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RAGRepository(db)
        self.retriever = HybridRetriever()

    async def ingest_document(self, request: RAGIngestRequest) -> RAGUploadResponse:
        # 1. Parse text using Loader Factory
        text = DocumentLoaderFactory.load_document(
            file_type=request.file_type,
            content_base64=request.content_base64,
            text_content=request.text_content
        )
        
        # 2. Chunk text
        strategy = request.metadata.get("chunk_strategy", "recursive")
        chunks = RAGChunker.chunk_document(text, strategy=strategy)
        
        # 3. Check for incremental indexing / versioning
        existing = await self.repo.get_by_name(request.document_name)
        next_ver = (existing.doc_version + 1) if existing else 1
        
        # Delete old index chunks if it exists (de-duplication / update)
        if existing:
            logger.info(f"Removing old chunks for version {existing.doc_version} of document {request.document_name}")
            self.retriever.store.delete_document_chunks(request.document_name)
            
        # 4. Store in vector DB
        global_meta = dict(request.metadata)
        global_meta.update({
            "doc_version": next_ver,
            "document_id": str(uuid.uuid4())
        })
        
        self.retriever.store.upsert_chunks(request.document_name, chunks, global_meta)
        
        # 5. Log Document History in db
        history = RAGDocumentHistory(
            id=uuid.UUID(global_meta["document_id"]),
            document_name=request.document_name,
            file_type=request.file_type,
            doc_version=next_ver,
            chunks_count=len(chunks),
            metadata_json=global_meta
        )
        await self.repo.create(history)
        
        # Flush retrieval caches on new ingestion
        cache.clear_pattern("rag:retrieve:*")

        return RAGUploadResponse(
            id=history.id,
            document_name=history.document_name,
            chunks_count=history.chunks_count,
            version=history.doc_version,
            status="ingested"
        )

    async def retrieve_context(self, request: RAGRetrieveRequest) -> RAGRetrieveResponse:
        # Role-based document visibility filtering
        # Check permissions in metadata filters
        updated_filters = dict(request.filters)
        
        # Role access rules: viewer can only see public or self-owned docs, admin sees all
        if request.role != "admin":
            # For simplicity, filter docs matching access role permission tags
            updated_filters["permissions"] = "public"
            
        # Check cache
        cache_key = f"rag:retrieve:{hash(request.model_dump_json())}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving RAG retrieval context from Redis cache.")
            return RAGRetrieveResponse(**cached)
            
        # Retrieve hybrid nodes
        matches = self.retriever.retrieve(request.query, limit=request.limit, filters=updated_filters)
        
        context_prompt = ContextBuilder.build_prompt_context(matches)
        citations = ContextBuilder.extract_citations(matches)
        
        response = RAGRetrieveResponse(
            context_prompt=context_prompt,
            citations=citations,
            explainability={
                "retrieved_nodes_count": len(matches),
                "similarity_scores": [m["score"] for m in matches]
            }
        )
        
        # Cache context payload (TTL 1 hour)
        cache.set(cache_key, response.model_dump(mode="json"), ttl=3600)
        return response

    async def delete_document(self, doc_id: uuid.UUID) -> Dict[str, Any]:
        # Fetch document to get name
        res = await self.db.execute(
            select(RAGDocumentHistory).where(RAGDocumentHistory.id == doc_id)
        )
        doc = res.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="RAG Document ID not found")
            
        # Delete from Vector Store
        self.retriever.store.delete_document_chunks(doc.document_name)
        
        # Delete from DB
        await self.repo.delete(doc_id)
        
        # Flush retrieval cache
        cache.clear_pattern("rag:retrieve:*")
        
        return {"status": "deleted", "document_name": doc.document_name}

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[RAGDocumentHistory]:
        return await self.repo.list_history(skip, limit)
