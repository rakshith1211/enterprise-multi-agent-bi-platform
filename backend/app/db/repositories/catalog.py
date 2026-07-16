from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
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
from typing import List, Optional
import uuid

class CatalogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Domains
    async def create_domain(self, domain: BusinessDomain) -> BusinessDomain:
        self.db.add(domain)
        await self.db.commit()
        await self.db.refresh(domain)
        return domain

    async def get_domain(self, id: uuid.UUID) -> Optional[BusinessDomain]:
        res = await self.db.execute(select(BusinessDomain).where(BusinessDomain.id == id))
        return res.scalars().first()

    async def list_domains(self) -> List[BusinessDomain]:
        res = await self.db.execute(select(BusinessDomain))
        return list(res.scalars().all())

    # Glossaries
    async def create_glossary(self, glossary: BusinessGlossary) -> BusinessGlossary:
        self.db.add(glossary)
        await self.db.commit()
        await self.db.refresh(glossary)
        return glossary

    async def get_glossary(self, id: uuid.UUID) -> Optional[BusinessGlossary]:
        res = await self.db.execute(select(BusinessGlossary).where(BusinessGlossary.id == id))
        return res.scalars().first()

    async def list_glossaries(self) -> List[BusinessGlossary]:
        res = await self.db.execute(select(BusinessGlossary))
        return list(res.scalars().all())

    # Terms
    async def create_term(self, term: BusinessTerm) -> BusinessTerm:
        self.db.add(term)
        await self.db.commit()
        await self.db.refresh(term)
        return term

    async def get_term_by_id(self, id: uuid.UUID) -> Optional[BusinessTerm]:
        res = await self.db.execute(
            select(BusinessTerm)
            .where(BusinessTerm.id == id)
            .options(
                selectinload(BusinessTerm.synonyms),
                selectinload(BusinessTerm.tags),
                selectinload(BusinessTerm.kpis),
                selectinload(BusinessTerm.rules),
                selectinload(BusinessTerm.column_mappings),
                selectinload(BusinessTerm.table_mappings)
            )
        )
        return res.scalars().first()

    async def get_term_by_name(self, name: str) -> Optional[BusinessTerm]:
        res = await self.db.execute(
            select(BusinessTerm)
            .where(BusinessTerm.name.ilike(name))
            .options(
                selectinload(BusinessTerm.synonyms),
                selectinload(BusinessTerm.tags),
                selectinload(BusinessTerm.kpis),
                selectinload(BusinessTerm.rules),
                selectinload(BusinessTerm.column_mappings),
                selectinload(BusinessTerm.table_mappings)
            )
        )
        return res.scalars().first()

    async def list_terms(self, skip: int = 0, limit: int = 100) -> List[BusinessTerm]:
        res = await self.db.execute(
            select(BusinessTerm)
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(BusinessTerm.synonyms),
                selectinload(BusinessTerm.tags),
                selectinload(BusinessTerm.kpis),
                selectinload(BusinessTerm.rules),
                selectinload(BusinessTerm.column_mappings),
                selectinload(BusinessTerm.table_mappings)
            )
        )
        return list(res.scalars().all())

    async def search_exact(self, query: str) -> List[BusinessTerm]:
        res = await self.db.execute(
            select(BusinessTerm)
            .where(BusinessTerm.name.ilike(query))
            .options(
                selectinload(BusinessTerm.synonyms),
                selectinload(BusinessTerm.tags),
                selectinload(BusinessTerm.kpis),
                selectinload(BusinessTerm.rules),
                selectinload(BusinessTerm.column_mappings),
                selectinload(BusinessTerm.table_mappings)
            )
        )
        return list(res.scalars().all())

    async def search_fuzzy(self, query: str) -> List[BusinessTerm]:
        # Fuzzy ilike match on names and descriptions
        res = await self.db.execute(
            select(BusinessTerm)
            .where(
                (BusinessTerm.name.ilike(f"%{query}%")) |
                (BusinessTerm.description.ilike(f"%{query}%"))
            )
            .options(
                selectinload(BusinessTerm.synonyms),
                selectinload(BusinessTerm.tags),
                selectinload(BusinessTerm.kpis),
                selectinload(BusinessTerm.rules),
                selectinload(BusinessTerm.column_mappings),
                selectinload(BusinessTerm.table_mappings)
            )
        )
        return list(res.scalars().all())

    async def update_term(self, term: BusinessTerm) -> BusinessTerm:
        self.db.add(term)
        await self.db.commit()
        await self.db.refresh(term)
        return term

    async def delete_term(self, id: uuid.UUID) -> bool:
        term = await self.get_term_by_id(id)
        if not term:
            return False
        await self.db.delete(term)
        await self.db.commit()
        return True

    # Lineage
    async def create_lineage(self, lineage: DataLineage) -> DataLineage:
        self.db.add(lineage)
        await self.db.commit()
        await self.db.refresh(lineage)
        return lineage

    async def get_lineage(self, id: uuid.UUID) -> Optional[DataLineage]:
        res = await self.db.execute(select(DataLineage).where(DataLineage.id == id))
        return res.scalars().first()

    async def list_lineage(self) -> List[DataLineage]:
        res = await self.db.execute(select(DataLineage))
        return list(res.scalars().all())

    # Audit Logs
    async def create_audit_history(self, history: AuditHistory) -> AuditHistory:
        self.db.add(history)
        await self.db.commit()
        return history
