"""Token-aware text chunking."""

import tiktoken

from app.config.settings import Settings
from app.rag.types import TextChunk
from app.services.parsers.base import ParsedDocument


class TextChunker:
    """Split parsed documents into overlapping token-budget chunks."""

    def __init__(self, settings: Settings) -> None:
        self._chunk_size = settings.chunk_size
        self._chunk_overlap = settings.chunk_overlap
        try:
            self._encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self._encoder = None

    def _count_tokens(self, text: str) -> int:
        if self._encoder:
            return len(self._encoder.encode(text))
        return len(text.split())

    def chunk_document(self, parsed: ParsedDocument) -> list[TextChunk]:
        """Chunk all pages from a parsed document."""
        chunks: list[TextChunk] = []
        index = 0
        for page in parsed.pages:
            page_chunks = self._chunk_text(page.text, page.page_number, start_index=index)
            chunks.extend(page_chunks)
            index += len(page_chunks)
        return chunks

    def _chunk_text(
        self,
        text: str,
        page_number: int | None,
        *,
        start_index: int,
    ) -> list[TextChunk]:
        """Split a text block using token windows."""
        text = text.strip()
        if not text:
            return []

        if self._encoder:
            tokens = self._encoder.encode(text)
            chunks: list[TextChunk] = []
            start = 0
            idx = start_index
            while start < len(tokens):
                end = min(start + self._chunk_size, len(tokens))
                chunk_tokens = tokens[start:end]
                content = self._encoder.decode(chunk_tokens)
                chunks.append(
                    TextChunk(
                        chunk_index=idx,
                        content=content.strip(),
                        token_count=len(chunk_tokens),
                        page_number=page_number,
                    )
                )
                idx += 1
                if end >= len(tokens):
                    break
                start = max(end - self._chunk_overlap, start + 1)
            return [c for c in chunks if c.content]

        words = text.split()
        chunks = []
        idx = start_index
        start = 0
        while start < len(words):
            end = min(start + self._chunk_size, len(words))
            content = " ".join(words[start:end])
            chunks.append(
                TextChunk(
                    chunk_index=idx,
                    content=content,
                    token_count=end - start,
                    page_number=page_number,
                )
            )
            idx += 1
            if end >= len(words):
                break
            start = max(end - self._chunk_overlap, start + 1)
        return chunks
