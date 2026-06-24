"""RAG pipeline state and data transfer objects."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class TextChunk:
    """In-memory chunk before persistence."""

    chunk_index: int
    content: str
    token_count: int
    page_number: int | None = None


@dataclass
class RetrievedChunk:
    """Chunk returned from vector search."""

    chunk_id: UUID
    document_id: UUID
    content: str
    score: float
    chunk_index: int
    original_filename: str
    page_number: int | None = None
    rerank_score: float | None = None


@dataclass
class RAGResult:
    """Final RAG pipeline output."""

    answer: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    retrieval_metadata: dict[str, Any] = field(default_factory=dict)
