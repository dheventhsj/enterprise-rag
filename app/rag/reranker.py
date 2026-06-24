"""Cross-encoder reranking and score fusion."""

from app.config.settings import Settings
from app.rag.types import RetrievedChunk


class Reranker:
    """Rerank retrieved chunks by relevance to the query."""

    def __init__(self, settings: Settings) -> None:
        self._top_k = settings.rerank_top_k

    def rerank(self, query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """Apply lightweight lexical reranking (production: cross-encoder model)."""
        if not chunks:
            return []

        query_terms = set(query.lower().split())
        scored: list[RetrievedChunk] = []
        for chunk in chunks:
            content_terms = set(chunk.content.lower().split())
            overlap = len(query_terms & content_terms)
            lexical = overlap / max(len(query_terms), 1)
            fused = 0.7 * chunk.score + 0.3 * lexical
            scored.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=chunk.score,
                    chunk_index=chunk.chunk_index,
                    original_filename=chunk.original_filename,
                    page_number=chunk.page_number,
                    rerank_score=fused,
                )
            )

        scored.sort(key=lambda c: c.rerank_score or 0.0, reverse=True)
        return scored[: self._top_k]
