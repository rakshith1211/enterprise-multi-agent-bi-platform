import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    database_type: Mapped[str] = mapped_column(String(50), nullable=False) # postgresql, mysql, mssql, oracle, sqlite, duckdb
    
    # Credentials / Host info
    host: Mapped[str] = mapped_column(String(255), nullable=True)
    port: Mapped[int] = mapped_column(Integer, nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    encrypted_password: Mapped[str] = mapped_column(String(1024), nullable=True)
    encrypted_connection_string: Mapped[str] = mapped_column(String(2048), nullable=True)
    database_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    ssl_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extra_parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    # Governance & Metadata
    environment: Mapped[str] = mapped_column(String(50), default="Development", nullable=False) # Development, Test, Production
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False) # active, disabled
    
    # Telemetry
    last_successful_connection: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_failed_connection: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    failure_reason: Mapped[str] = mapped_column(String(1024), nullable=True)
    average_response_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Audit
    created_by: Mapped[str] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
