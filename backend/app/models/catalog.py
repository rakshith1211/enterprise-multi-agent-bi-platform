import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class BusinessDomain(Base):
    __tablename__ = "business_domains"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    glossaries: Mapped[list["BusinessGlossary"]] = relationship(back_populates="domain", cascade="all, delete-orphan")

class BusinessGlossary(Base):
    __tablename__ = "business_glossaries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_domains.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    domain: Mapped["BusinessDomain"] = relationship(back_populates="glossaries")
    terms: Mapped[list["BusinessTerm"]] = relationship(back_populates="glossary", cascade="all, delete-orphan")

class BusinessTerm(Base):
    __tablename__ = "business_terms"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    glossary_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_glossaries.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    glossary: Mapped["BusinessGlossary"] = relationship(back_populates="terms")
    kpis: Mapped[list["KPI"]] = relationship(back_populates="term", cascade="all, delete-orphan")
    rules: Mapped[list["BusinessRule"]] = relationship(back_populates="term", cascade="all, delete-orphan")
    synonyms: Mapped[list["Synonym"]] = relationship(back_populates="term", cascade="all, delete-orphan")
    column_mappings: Mapped[list["ColumnMapping"]] = relationship(back_populates="term", cascade="all, delete-orphan")
    table_mappings: Mapped[list["TableMapping"]] = relationship(back_populates="term", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(back_populates="term", cascade="all, delete-orphan")

class KPI(Base):
    __tablename__ = "kpis"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_terms.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    formula: Mapped[str] = mapped_column(Text, nullable=False) # e.g. SQL expression
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    term: Mapped["BusinessTerm"] = relationship(back_populates="kpis")

class BusinessRule(Base):
    __tablename__ = "business_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_terms.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_definition: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    term: Mapped["BusinessTerm"] = relationship(back_populates="rules")

class Synonym(Base):
    __tablename__ = "synonyms"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_terms.id", ondelete="CASCADE"), nullable=False)
    synonym_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    term: Mapped["BusinessTerm"] = relationship(back_populates="synonyms")

class ColumnMapping(Base):
    __tablename__ = "column_mappings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_terms.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    schema_name: Mapped[str] = mapped_column(String(100), nullable=False)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    column_name: Mapped[str] = mapped_column(String(100), nullable=False)

    term: Mapped["BusinessTerm"] = relationship(back_populates="column_mappings")

class TableMapping(Base):
    __tablename__ = "table_mappings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_terms.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    schema_name: Mapped[str] = mapped_column(String(100), nullable=False)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)

    term: Mapped["BusinessTerm"] = relationship(back_populates="table_mappings")

class DataLineage(Base):
    __tablename__ = "data_lineage"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_connection_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    source_schema: Mapped[str] = mapped_column(String(100), nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_column: Mapped[str] = mapped_column(String(100), nullable=True)
    
    target_schema: Mapped[str] = mapped_column(String(100), nullable=False)
    target_table: Mapped[str] = mapped_column(String(100), nullable=False)
    target_column: Mapped[str] = mapped_column(String(100), nullable=True)
    
    transformation_rule: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("business_terms.id", ondelete="CASCADE"), nullable=False)
    tag_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    term: Mapped["BusinessTerm"] = relationship(back_populates="tags")

class AuditHistory(Base):
    __tablename__ = "audit_histories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    action: Mapped[str] = mapped_column(String(100), nullable=False) # CREATE, UPDATE, DELETE
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False) # BusinessTerm, etc.
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    changes: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    user: Mapped[str] = mapped_column(String(255), default="system", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
