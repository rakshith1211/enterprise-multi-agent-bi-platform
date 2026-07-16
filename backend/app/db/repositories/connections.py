from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.connections import DatabaseConnection
from app.models.audit import AuditLog
from typing import List, Optional
import uuid
from datetime import datetime

class ConnectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, connection: DatabaseConnection) -> DatabaseConnection:
        self.db.add(connection)
        await self.db.commit()
        await self.db.refresh(connection)
        return connection

    async def get_by_id(self, id: uuid.UUID) -> Optional[DatabaseConnection]:
        result = await self.db.execute(
            select(DatabaseConnection).where(DatabaseConnection.id == id, DatabaseConnection.is_deleted == False)
        )
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[DatabaseConnection]:
        result = await self.db.execute(
            select(DatabaseConnection).where(DatabaseConnection.name == name, DatabaseConnection.is_deleted == False)
        )
        return result.scalars().first()

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[DatabaseConnection]:
        result = await self.db.execute(
            select(DatabaseConnection)
            .where(DatabaseConnection.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search(self, query: str) -> List[DatabaseConnection]:
        result = await self.db.execute(
            select(DatabaseConnection)
            .where(
                DatabaseConnection.is_deleted == False,
                (DatabaseConnection.name.ilike(f"%{query}%")) | 
                (DatabaseConnection.description.ilike(f"%{query}%")) |
                (DatabaseConnection.database_type.ilike(f"%{query}%"))
            )
        )
        return list(result.scalars().all())

    async def update(self, connection: DatabaseConnection) -> DatabaseConnection:
        self.db.add(connection)
        await self.db.commit()
        await self.db.refresh(connection)
        return connection

    async def soft_delete(self, id: uuid.UUID) -> bool:
        db_conn = await self.get_by_id(id)
        if not db_conn:
            return False
        db_conn.is_deleted = True
        db_conn.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def restore(self, id: uuid.UUID) -> Optional[DatabaseConnection]:
        result = await self.db.execute(
            select(DatabaseConnection).where(DatabaseConnection.id == id, DatabaseConnection.is_deleted == True)
        )
        db_conn = result.scalars().first()
        if db_conn:
            db_conn.is_deleted = False
            db_conn.deleted_at = None
            await self.db.commit()
            await self.db.refresh(db_conn)
            return db_conn
        return None

    async def create_audit_log(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log
