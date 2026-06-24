"""Pytest configuration and shared fixtures."""

import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_ingestion_service, get_storage_backend
from app.config.settings import get_settings
from app.database.base import Base
from app.database.session import get_db_session
from app.main import create_app
from app.services.ingestion_service import IngestionService
from app.services.parsers.registry import DocumentParserRegistry
from app.services.storage.base import LocalStorageBackend

TEST_SECRET = "test-secret-key-minimum-32-characters-long"
TEST_DATABASE_URL = "sqlite+aiosqlite://"

os.environ.setdefault("SECRET_KEY", TEST_SECRET)
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("UPLOAD_DIR", "test_uploads")

get_settings.cache_clear()


@pytest.fixture
async def test_db_engine():
    """Shared in-memory SQLite engine for API and unit tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine) -> AsyncSession:
    """Yield a database session bound to the shared test engine."""
    factory = async_sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_storage(tmp_path):
    """Temporary local storage backend for upload tests."""
    return LocalStorageBackend(tmp_path)


@pytest.fixture
async def client(test_db_engine, test_storage, tmp_path):
    """Async HTTP client with database and storage dependencies overridden."""
    session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def override_storage_backend():
        return test_storage

    def override_ingestion_service():
        return IngestionService(
            settings=get_settings(),
            storage=test_storage,
            parser_registry=DocumentParserRegistry(),
            session_factory=session_factory,
        )

    app = create_app()
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_storage_backend] = override_storage_backend
    app.dependency_overrides[get_ingestion_service] = override_ingestion_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):  # type: ignore[no-untyped-def]
    """Register a user and return authorization headers."""

    async def _register_and_login(
        email: str = "user@example.com",
        password: str = "securepass123",
        full_name: str = "Test User",
    ) -> dict[str, str]:
        register_response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": full_name},
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _register_and_login
