"""Application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.error_handlers import register_exception_handlers
from app.api.router import api_router
from app.config.settings import get_settings
from app.database.session import close_db, init_db
from app.logging import setup_logging
from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup and shutdown lifecycle hooks."""
    settings = get_settings()
    setup_logging(settings)
    if settings.app_env == "development" or settings.serverless_mode:
        await init_db(settings)
    yield
    await close_db()


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if settings.rate_limit_enabled and not settings.serverless_mode:
        app.add_middleware(RateLimitMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    if settings.metrics_enabled:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
