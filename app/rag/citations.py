"""Source citation generation."""

from typing import Any

from app.rag.types import RetrievedChunk


def generate_citations(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    """Map retrieved chunks to citation objects."""
    citations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for chunk in chunks:
        key = f"{chunk.document_id}:{chunk.chunk_index}"
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            {
                "document_id": str(chunk.document_id),
                "chunk_id": str(chunk.chunk_id),
                "chunk_index": chunk.chunk_index,
                "filename": chunk.original_filename,
                "page_number": chunk.page_number,
                "score": chunk.rerank_score or chunk.score,
                "excerpt": chunk.content[:200],
            }
        )
    return citations
