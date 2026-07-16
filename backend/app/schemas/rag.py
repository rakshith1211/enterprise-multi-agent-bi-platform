from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class RAGIngestRequest(BaseModel):
    document_name: str = Field(..., description="Document source filename")
    file_type: str = Field(..., description="pdf, docx, pptx, csv, xlsx, md, html, txt, json, sql, rule")
    content_base64: Optional[str] = Field(None, description="Optional raw base64 data")
    text_content: Optional[str] = Field(None, description="Optional parsed textual contents")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata tags, author, domain, permissions")

class RAGUploadResponse(BaseModel):
    id: uuid.UUID
    document_name: str
    chunks_count: int
    version: int
    status: str

class RAGRetrieveRequest(BaseModel):
    query: str = Field(..., description="Semantic question to search context for")
    limit: int = Field(5, description="Maximum number of contexts to fetch")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Metadata filters (author, business_domain, permissions)")
    role: str = Field("viewer", description="Role of the requestor (viewer, editor, admin)")

class CitationNode(BaseModel):
    document_name: str
    chunk_index: int
    matched_text: str
    score: float
    metadata: Dict[str, Any]

class RAGRetrieveResponse(BaseModel):
    context_prompt: str
    citations: List[CitationNode]
    explainability: Dict[str, Any]

class RAGHistoryResponse(BaseModel):
    id: uuid.UUID
    document_name: str
    file_type: str
    doc_version: int
    chunks_count: int
    metadata_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
