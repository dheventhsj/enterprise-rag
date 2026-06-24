"""Async database session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import Settings, get_settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(settings: Settings | None = None):
    """Create or return the async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = settings or get_settings()
        _engine = create_async_engine(
            str(settings.database_url),
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=settings.debug,
        )
    return _engine


def get_session_factory(settings: Settings | None = None) -> async_sessionmaker[AsyncSession]:
    """Create or return the async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(settings),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db(settings: Settings | None = None) -> None:
    """Create all tables (development bootstrap; use Alembic in production)."""
    from app.database.base import Base
    from app.models import (  # noqa: F401 — register models
        chunk,
        conversation,
        document,
        embedding,
        feedback,
        log,
        message,
        user,
    )

    engine = get_engine(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose engine on shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
