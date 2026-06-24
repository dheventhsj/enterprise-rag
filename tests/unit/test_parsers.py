"""Unit tests for document parsers."""

from io import BytesIO

import pytest
from docx import Document as DocxDocument

from app.exceptions import ValidationError
from app.models.document import DocumentType
from app.services.parsers.registry import DocumentParserRegistry


@pytest.fixture
def registry() -> DocumentParserRegistry:
    return DocumentParserRegistry()


def test_parse_txt(registry: DocumentParserRegistry) -> None:
    """TXT parser extracts plain text."""
    content = b"Policy: 20 days PTO per year."
    parsed = registry.parse(file_type=DocumentType.TXT, content=content)
    assert parsed.full_text == "Policy: 20 days PTO per year."
    assert parsed.page_count == 1


def test_parse_docx(registry: DocumentParserRegistry) -> None:
    """DOCX parser extracts paragraph text."""
    buffer = BytesIO()
    document = DocxDocument()
    document.add_paragraph("Quarterly revenue increased.")
    document.save(buffer)
    parsed = registry.parse(file_type=DocumentType.DOCX, content=buffer.getvalue())
    assert "Quarterly revenue increased." in parsed.full_text


def test_parse_empty_txt_raises(registry: DocumentParserRegistry) -> None:
    """Empty text files raise validation error."""
    with pytest.raises(ValidationError, match="empty"):
        registry.parse(file_type=DocumentType.TXT, content=b"   ")


def test_parse_invalid_pdf_raises(registry: DocumentParserRegistry) -> None:
    """Invalid PDF bytes raise validation error."""
    with pytest.raises(ValidationError):
        registry.parse(file_type=DocumentType.PDF, content=b"%PDF-invalid")
