import os
os.environ["TESTING"] = "true"
import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import get_db
from app.db.base import Base

# Import models to ensure register
from app.models.connections import DatabaseConnection
from app.models.audit import AuditLog
from app.models.planner import QueryPlanHistory
from app.models.sql_agent import SQLAgentHistory
from app.models.query_execution import QueryExecutionHistory
from app.models.analytics import AnalyticsHistory
from app.models.visualization import VisualizationHistory
from app.models.forecast import ForecastHistory
from app.models.recommendation import RecommendationHistory
from app.models.report import ReportHistory
from app.models.orchestrator import WorkflowHistory
from app.models.rag import RAGDocumentHistory

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    # Sync wrapper to initialize tables at session start
    loop = asyncio.new_event_loop()
    async def _init():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    loop.run_until_complete(_init())
    loop.close()
    
    yield
    
    loop = asyncio.new_event_loop()
    async def _drop():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    loop.run_until_complete(_drop())
    loop.close()

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(autouse=True)
def override_db_dependency(db_session):
    async def _get_test_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
