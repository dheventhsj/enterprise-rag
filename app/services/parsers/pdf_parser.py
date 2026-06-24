"""PDF document parser."""

from io import BytesIO

from pypdf import PdfReader

from app.exceptions import ValidationError
from app.services.parsers.base import ParsedDocument, ParsedPage


class PDFParser:
    """Extract text from PDF files."""

    def parse(self, content: bytes) -> ParsedDocument:
        """Parse PDF bytes into structured pages."""
        try:
            reader = PdfReader(BytesIO(content))
        except Exception as exc:
            raise ValidationError("Failed to read PDF file") from exc

        pages: list[ParsedPage] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(ParsedPage(page_number=index, text=text.strip()))

        if not any(page.text for page in pages):
            raise ValidationError("PDF contains no extractable text")

        return ParsedDocument(pages=pages)
