from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Domain Schemas
class DomainBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None

class DomainCreate(DomainBase):
    pass

class DomainResponse(DomainBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# Glossary Schemas
class GlossaryBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    domain_id: uuid.UUID

class GlossaryCreate(GlossaryBase):
    pass

class GlossaryResponse(GlossaryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# Nested schemas for create
class KPICreate(BaseModel):
    name: str
    formula: str
    description: Optional[str] = None

class RuleCreate(BaseModel):
    name: str
    rule_definition: str
    description: Optional[str] = None

class ColumnMappingCreate(BaseModel):
    connection_id: uuid.UUID
    schema_name: str
    table_name: str
    column_name: str

class TableMappingCreate(BaseModel):
    connection_id: uuid.UUID
    schema_name: str
    table_name: str

# Term Schemas
class TermBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    glossary_id: uuid.UUID

class TermCreate(TermBase):
    synonyms: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    kpis: List[KPICreate] = Field(default_factory=list)
    rules: List[RuleCreate] = Field(default_factory=list)
    column_mappings: List[ColumnMappingCreate] = Field(default_factory=list)
    table_mappings: List[TableMappingCreate] = Field(default_factory=list)

class TermUpdate(BaseModel):
    description: Optional[str] = None
    synonyms: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    kpis: Optional[List[KPICreate]] = None
    rules: Optional[List[RuleCreate]] = None
    column_mappings: Optional[List[ColumnMappingCreate]] = None
    table_mappings: Optional[List[TableMappingCreate]] = None

class KPIResponse(BaseModel):
    id: uuid.UUID
    name: str
    formula: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}

class RuleResponse(BaseModel):
    id: uuid.UUID
    name: str
    rule_definition: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}

class ColumnMappingResponse(BaseModel):
    id: uuid.UUID
    connection_id: uuid.UUID
    schema_name: str
    table_name: str
    column_name: str
    model_config = {"from_attributes": True}

class TableMappingResponse(BaseModel):
    id: uuid.UUID
    connection_id: uuid.UUID
    schema_name: str
    table_name: str
    model_config = {"from_attributes": True}

class TermResponse(TermBase):
    id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime
    synonyms: List[str] = []
    tags: List[str] = []
    kpis: List[KPIResponse] = []
    rules: List[RuleResponse] = []
    column_mappings: List[ColumnMappingResponse] = []
    table_mappings: List[TableMappingResponse] = []

    model_config = {"from_attributes": True}

    @field_validator("synonyms", mode="before")
    @classmethod
    def serialize_synonyms(cls, v):
        if isinstance(v, list):
            return [x.synonym_name if hasattr(x, "synonym_name") else x for x in v]
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def serialize_tags(cls, v):
        if isinstance(v, list):
            return [x.tag_name if hasattr(x, "tag_name") else x for x in v]
        return v

# Semantic Search Schemas
class SemanticSearchResult(BaseModel):
    id: str
    name: str
    type: str # term, kpi, rule, column, table
    description: str
    confidence: float
    explainability: str
    metadata: Dict[str, Any]

# Lineage Schemas
class LineageCreate(BaseModel):
    source_connection_id: uuid.UUID
    source_schema: str
    source_table: str
    source_column: Optional[str] = None
    target_schema: str
    target_table: str
    target_column: Optional[str] = None
    transformation_rule: Optional[str] = None

class LineageResponse(LineageCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = {"from_attributes": True}
