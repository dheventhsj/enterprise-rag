"""Unit tests for text chunking."""

from app.config.settings import Settings
from app.rag.chunking import TextChunker
from app.services.parsers.base import ParsedDocument, ParsedPage


def test_chunk_document_splits_text() -> None:
    settings = Settings(
        secret_key="test-secret-key-minimum-32-characters-long",
        database_url="sqlite+aiosqlite:///./test.db",
        chunk_size=10,
        chunk_overlap=2,
    )
    chunker = TextChunker(settings)
    parsed = ParsedDocument(
        pages=[ParsedPage(page_number=1, text="word " * 50)]
    )
    chunks = chunker.chunk_document(parsed)
    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert all(chunk.content for chunk in chunks)
