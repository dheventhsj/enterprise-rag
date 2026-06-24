"""Embedding service factory."""

from app.config.settings import Settings
from app.rag.embeddings import EmbeddingService
from app.rag.embeddings_openai import OpenAIEmbeddingService


def create_embedding_service(settings: Settings) -> EmbeddingService | OpenAIEmbeddingService:
    """Return the appropriate embedding backend for the environment."""
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddingService(settings)
    return EmbeddingService(settings)
