"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the Enterprise RAG platform."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "enterprise-rag"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(..., min_length=32)
    access_token_expire_minutes: int = 60

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "enterprise_rag_chunks"
    qdrant_api_key: str | None = None

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    # LLM
    llm_provider: Literal["openai", "gemini"] = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    # RAG
    chunk_size: int = 512
    chunk_overlap: int = 64
    retrieval_top_k: int = 20
    rerank_top_k: int = 5
    max_context_tokens: int = 4096

    # Upload
    max_upload_size_mb: int = 25
    allowed_extensions: list[str] = ["pdf", "docx", "txt"]
    upload_dir: str = "uploads"

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # Monitoring
    metrics_enabled: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Parse CORS origins from JSON string or list."""
        if isinstance(value, str):
            import json

            return json.loads(value)
        return value

    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, value: str | list[str]) -> list[str]:
        """Parse allowed file extensions from JSON string or list."""
        if isinstance(value, str):
            import json

            return json.loads(value)
        return value

    @property
    def max_upload_size_bytes(self) -> int:
        """Maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Whether the application runs in production mode."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()  # type: ignore[call-arg]
