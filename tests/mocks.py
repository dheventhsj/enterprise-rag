"""Test mocks for external services."""

from uuid import uuid4

from app.rag.types import RetrievedChunk


class MockEmbeddingService:
    """Return deterministic fake embeddings without loading ML models."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.01] * 384 for _ in texts]

    def embed_query(self, query: str) -> list[float]:
        return [0.01] * 384


class MockVectorStore:
    """In-memory vector store stub for tests."""

    def upsert_vectors(self, **kwargs) -> list[str]:
        return [str(uuid4()) for _ in kwargs["chunk_ids"]]

    def search(self, **kwargs) -> list[RetrievedChunk]:
        return []

    def delete_by_document(self, **kwargs) -> None:
        return None
