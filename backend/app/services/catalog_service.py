import uuid
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from chromadb.utils import embedding_functions

from app.models.catalog import (
    BusinessDomain,
    BusinessGlossary,
    BusinessTerm,
    KPI,
    BusinessRule,
    Synonym,
    ColumnMapping,
    TableMapping,
    DataLineage,
    Tag,
    AuditHistory
)
from app.schemas.catalog import (
    DomainCreate,
    GlossaryCreate,
    TermCreate,
    TermUpdate,
    LineageCreate,
    SemanticSearchResult
)
from app.db.repositories.catalog import CatalogRepository
from app.db.chroma_client import get_chroma_client
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class CatalogService:
    def __init__(self, db: AsyncSession):
        self.repo = CatalogRepository(db)
        self.chroma = get_chroma_client()
        # Initialize default ONNX embedding function
        ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.chroma.get_or_create_collection(
            name="semantic_catalog",
            embedding_function=ef
        )

    async def _audit(self, action: str, entity_type: str, entity_id: str, version: int, changes: dict, user: str = "system"):
        log = AuditHistory(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            version=version,
            changes=changes,
            user=user
        )
        await self.repo.create_audit_history(log)

    # Domain CRUD
    async def create_domain(self, schema: DomainCreate) -> BusinessDomain:
        domain = BusinessDomain(name=schema.name, description=schema.description)
        return await self.repo.create_domain(domain)

    async def get_domain(self, id: uuid.UUID) -> BusinessDomain:
        d = await self.repo.get_domain(id)
        if not d:
            raise HTTPException(status_code=404, detail="Domain not found")
        return d

    async def list_domains(self) -> List[BusinessDomain]:
        return await self.repo.list_domains()

    # Glossary CRUD
    async def create_glossary(self, schema: GlossaryCreate) -> BusinessGlossary:
        glossary = BusinessGlossary(
            name=schema.name,
            description=schema.description,
            domain_id=schema.domain_id
        )
        return await self.repo.create_glossary(glossary)

    async def get_glossary(self, id: uuid.UUID) -> BusinessGlossary:
        g = await self.repo.get_glossary(id)
        if not g:
            raise HTTPException(status_code=404, detail="Glossary not found")
        return g

    async def list_glossaries(self) -> List[BusinessGlossary]:
        return await self.repo.list_glossaries()

    # Term CRUD
    async def create_term(self, schema: TermCreate, user: str = "system") -> BusinessTerm:
        existing = await self.repo.get_term_by_name(schema.name)
        if existing:
            raise HTTPException(status_code=400, detail="Business term already exists")

        term = BusinessTerm(
            name=schema.name,
            description=schema.description,
            glossary_id=schema.glossary_id
        )

        # Children
        term.synonyms = [Synonym(synonym_name=s) for s in schema.synonyms]
        term.tags = [Tag(tag_name=t) for t in schema.tags]
        term.kpis = [KPI(name=k.name, formula=k.formula, description=k.description) for k in schema.kpis]
        term.rules = [BusinessRule(name=r.name, rule_definition=r.rule_definition, description=r.description) for r in schema.rules]
        term.column_mappings = [ColumnMapping(
            connection_id=c.connection_id,
            schema_name=c.schema_name,
            table_name=c.table_name,
            column_name=c.column_name
        ) for c in schema.column_mappings]
        term.table_mappings = [TableMapping(
            connection_id=t.connection_id,
            schema_name=t.schema_name,
            table_name=t.table_name
        ) for t in schema.table_mappings]

        saved = await self.repo.create_term(term)

        # Index in ChromaDB using eager loaded relationships
        eager_term = await self.repo.get_term_by_id(saved.id)
        if eager_term:
            self._index_term(eager_term)

        # Audit History
        await self._audit("CREATE", "BusinessTerm", str(saved.id), 1, saved.description, user=user)
        return saved

    async def get_term(self, id: uuid.UUID) -> BusinessTerm:
        t = await self.repo.get_term_by_id(id)
        if not t:
            raise HTTPException(status_code=404, detail="Business term not found")
        return t

    async def list_terms(self, skip: int = 0, limit: int = 100) -> List[BusinessTerm]:
        return await self.repo.list_terms(skip, limit)

    async def update_term(self, id: uuid.UUID, schema: TermUpdate, user: str = "system") -> BusinessTerm:
        term = await self.get_term(id)
        changes = {}

        if schema.description is not None:
            changes["description"] = {"old": term.description, "new": schema.description}
            term.description = schema.description

        # Increment version
        term.version += 1
        term.updated_at = datetime.now(timezone.utc)

        # Update children if provided
        if schema.synonyms is not None:
            term.synonyms = [Synonym(synonym_name=s) for s in schema.synonyms]
        if schema.tags is not None:
            term.tags = [Tag(tag_name=t) for t in schema.tags]
        if schema.kpis is not None:
            term.kpis = [KPI(name=k.name, formula=k.formula, description=k.description) for k in schema.kpis]
        if schema.rules is not None:
            term.rules = [BusinessRule(name=r.name, rule_definition=r.rule_definition, description=r.description) for r in schema.rules]
        if schema.column_mappings is not None:
            term.column_mappings = [ColumnMapping(
                connection_id=c.connection_id,
                schema_name=c.schema_name,
                table_name=c.table_name,
                column_name=c.column_name
            ) for c in schema.column_mappings]
        if schema.table_mappings is not None:
            term.table_mappings = [TableMapping(
                connection_id=t.connection_id,
                schema_name=t.schema_name,
                table_name=t.table_name
            ) for t in schema.table_mappings]

        updated = await self.repo.update_term(term)

        # Re-index in ChromaDB using eager loaded relationships
        eager_term = await self.repo.get_term_by_id(id)
        if eager_term:
            self._index_term(eager_term)

        # Audit History
        await self._audit("UPDATE", "BusinessTerm", str(id), updated.version, changes, user=user)
        
        # Evict cache
        cache.delete(f"term:{id}")
        return updated

    async def delete_term(self, id: uuid.UUID, user: str = "system") -> bool:
        term = await self.get_term(id)
        success = await self.repo.delete_term(id)
        if success:
            # Delete from ChromaDB
            self.collection.delete(ids=[f"term:{id}"])
            # Remove KPI, rules, columns, tables indexed elements
            self.collection.delete(where={"term_id": str(id)})
            await self._audit("DELETE", "BusinessTerm", str(id), term.version, {}, user=user)
            cache.delete(f"term:{id}")
            return True
        return False

    def _index_term(self, term: BusinessTerm):
        # Index Business Term
        self.collection.upsert(
            ids=[f"term:{term.id}"],
            documents=[f"Term: {term.name}. Description: {term.description}. Synonyms: {', '.join([s.synonym_name for s in term.synonyms])}."],
            metadatas=[{
                "id": str(term.id),
                "name": term.name,
                "type": "term",
                "description": term.description
            }]
        )

        # Index KPIs
        for k in term.kpis:
            self.collection.upsert(
                ids=[f"kpi:{k.id}"],
                documents=[f"KPI: {k.name}. Formula: {k.formula}. Description: {k.description}."],
                metadatas=[{
                    "id": str(k.id),
                    "term_id": str(term.id),
                    "name": k.name,
                    "type": "kpi",
                    "description": k.description
                }]
            )

        # Index Rules
        for r in term.rules:
            self.collection.upsert(
                ids=[f"rule:{r.id}"],
                documents=[f"Business Rule: {r.name}. Rule logic: {r.rule_definition}. Description: {r.description}."],
                metadatas=[{
                    "id": str(r.id),
                    "term_id": str(term.id),
                    "name": r.name,
                    "type": "rule",
                    "description": r.description
                }]
            )

    # Lineage CRUD
    async def create_lineage(self, schema: LineageCreate) -> DataLineage:
        lineage = DataLineage(
            source_connection_id=schema.source_connection_id,
            source_schema=schema.source_schema,
            source_table=schema.source_table,
            source_column=schema.source_column,
            target_schema=schema.target_schema,
            target_table=schema.target_table,
            target_column=schema.target_column,
            transformation_rule=schema.transformation_rule
        )
        saved = await self.repo.create_lineage(lineage)
        
        # Index lineage for impact analytics mapping
        self.collection.upsert(
            ids=[f"lineage:{saved.id}"],
            documents=[f"Lineage transformation: {saved.source_schema}.{saved.source_table} -> {saved.target_schema}.{saved.target_table}. Rule: {saved.transformation_rule}"],
            metadatas=[{
                "id": str(saved.id),
                "type": "lineage"
            }]
        )
        return saved

    async def list_lineage(self) -> List[DataLineage]:
        return await self.repo.list_lineage()

    # Search & AI Context Builder
    async def search(self, query: str, limit: int = 10, confidence_threshold: float = 0.0) -> List[SemanticSearchResult]:
        # 1. Semantic Search using ChromaDB
        res = self.collection.query(
            query_texts=[query],
            n_results=limit
        )

        results = []
        if res and res.get("ids") and len(res["ids"]) > 0 and len(res["ids"][0]) > 0:
            ids = res["ids"][0]
            docs = res.get("documents", [])[0] if res.get("documents") and len(res["documents"]) > 0 else [""] * len(ids)
            metadatas = res.get("metadatas", [])[0] if res.get("metadatas") and len(res["metadatas"]) > 0 else [{}] * len(ids)
            distances = res.get("distances", [])[0] if res.get("distances") and len(res["distances"]) > 0 else [0.0] * len(ids)

            for i in range(len(ids)):
                # L2 distance converted to confidence score (1.0 / (1.0 + distance))
                dist = distances[i]
                confidence = round(1.0 / (1.0 + dist), 2)
                
                if confidence < confidence_threshold:
                    continue

                meta = metadatas[i]
                results.append(SemanticSearchResult(
                    id=ids[i],
                    name=meta.get("name", "Unnamed"),
                    type=meta.get("type", "unknown"),
                    description=meta.get("description", docs[i]),
                    confidence=confidence,
                    explainability=f"Vector match cosine distance: {round(dist, 4)}. Maps query semantics directly to the schema definition context.",
                    metadata=meta
                ))

        # Sort by confidence descending
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results

    async def get_similar_terms(self, term_id: uuid.UUID, limit: int = 5) -> List[Dict[str, Any]]:
        term = await self.get(term_id)
        # Search using term description
        results = await self.search(term.description, limit=limit + 1)
        # Filter out current term
        return [r.model_dump() for r in results if r.id != f"term:{term_id}"][:limit]

    async def build_ai_context(self, query: str) -> Dict[str, Any]:
        """
        Compiles structured, high-confidence semantic matches to inject into the SQL Agent.
        """
        matches = await self.search(query, limit=5, confidence_threshold=0.3)
        
        context = {
            "business_terms": [],
            "kpis": [],
            "business_rules": [],
            "mappings": {
                "tables": [],
                "columns": []
            }
        }

        # Deduplicate targets
        seen_tables = set()
        seen_columns = set()

        for match in matches:
            if match.type == "term":
                term_id = uuid.UUID(match.metadata["id"])
                term = await self.repo.get_term_by_id(term_id)
                if term:
                    context["business_terms"].append({
                        "name": term.name,
                        "description": term.description,
                        "synonyms": [s.synonym_name for s in term.synonyms],
                        "confidence": match.confidence,
                        "explainability": match.explainability
                    })
                    # Add mappings
                    for t in term.table_mappings:
                        tbl_key = f"{t.connection_id}.{t.schema_name}.{t.table_name}"
                        if tbl_key not in seen_tables:
                            seen_tables.add(tbl_key)
                            context["mappings"]["tables"].append({
                                "connection_id": str(t.connection_id),
                                "schema": t.schema_name,
                                "table": t.table_name
                            })
                    for c in term.column_mappings:
                        col_key = f"{c.connection_id}.{c.schema_name}.{c.table_name}.{c.column_name}"
                        if col_key not in seen_columns:
                            seen_columns.add(col_key)
                            context["mappings"]["columns"].append({
                                "connection_id": str(c.connection_id),
                                "schema": c.schema_name,
                                "table": c.table_name,
                                "column": c.column_name
                            })
            elif match.type == "kpi":
                term_id = uuid.UUID(match.metadata["term_id"])
                term = await self.repo.get_term_by_id(term_id)
                if term:
                    kpi_match = next((k for k in term.kpis if str(k.id) == match.metadata["id"]), None)
                    if kpi_match:
                        context["kpis"].append({
                            "name": kpi_match.name,
                            "formula": kpi_match.formula,
                            "description": kpi_match.description,
                            "context_term": term.name
                        })
            elif match.type == "rule":
                term_id = uuid.UUID(match.metadata["term_id"])
                term = await self.repo.get_term_by_id(term_id)
                if term:
                    rule_match = next((r for r in term.rules if str(r.id) == match.metadata["id"]), None)
                    if rule_match:
                        context["business_rules"].append({
                            "name": rule_match.name,
                            "definition": rule_match.rule_definition,
                            "description": rule_match.description,
                            "context_term": term.name
                        })
        return context

    async def reindex_all(self):
        """
        Rebuilds ChromaDB indexes by reflecting all tables.
        """
        terms = await self.repo.list_terms(skip=0, limit=10000)
        # Clear collection
        self.collection.delete(ids=[f"term:{t.id}" for t in terms])
        for term in terms:
            self._index_term(term)
        return {"status": "success", "indexed_count": len(terms)}
