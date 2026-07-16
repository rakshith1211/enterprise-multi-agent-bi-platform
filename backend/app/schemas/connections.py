from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ConnectionBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1024)
    database_type: str = Field(...) # postgresql, mysql, mssql, oracle, sqlite, duckdb
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    database_name: Optional[str] = None
    ssl_enabled: bool = False
    extra_parameters: Dict[str, Any] = Field(default_factory=dict)
    environment: str = Field("Development") # Development, Test, Production
    tags: List[str] = Field(default_factory=list)

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 65535):
            raise ValueError("Port number must be between 1 and 65535")
        return v

    @field_validator("database_type")
    @classmethod
    def validate_db_type(cls, v: str) -> str:
        valid_types = ["postgresql", "mysql", "mssql", "oracle", "sqlite", "duckdb"]
        if v.lower() not in valid_types:
            raise ValueError(f"Unsupported database type. Must be one of {valid_types}")
        return v.lower()

class ConnectionCreate(ConnectionBase):
    password: Optional[str] = None
    connection_string: Optional[str] = None

class ConnectionUpdate(BaseModel):
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    database_name: Optional[str] = None
    ssl_enabled: Optional[bool] = None
    extra_parameters: Optional[Dict[str, Any]] = None
    environment: Optional[str] = None
    tags: Optional[List[str]] = None

class ConnectionResponse(ConnectionBase):
    id: uuid.UUID
    status: str
    last_successful_connection: Optional[datetime] = None
    last_failed_connection: Optional[datetime] = None
    failure_reason: Optional[str] = None
    average_response_time_ms: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    model_config = {"from_attributes": True}

class ConnectionTestRequest(BaseModel):
    database_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: Optional[str] = None
    connection_string: Optional[str] = None
    ssl_enabled: bool = False
    extra_parameters: Dict[str, Any] = Field(default_factory=dict)
