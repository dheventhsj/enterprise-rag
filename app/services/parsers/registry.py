"""Document parser registry."""

from app.models.document import DocumentType
from app.services.parsers.base import ParsedDocument
from app.services.parsers.docx_parser import DOCXParser
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.txt_parser import TXTParser


class DocumentParserRegistry:
    """Resolve the correct parser for a document type."""

    def __init__(self) -> None:
        self._parsers = {
            DocumentType.PDF: PDFParser(),
            DocumentType.DOCX: DOCXParser(),
            DocumentType.TXT: TXTParser(),
        }

    def parse(self, *, file_type: DocumentType, content: bytes) -> ParsedDocument:
        """Parse document content using the appropriate parser."""
        parser = self._parsers.get(file_type)
        if parser is None:
            from app.exceptions import ValidationError

            raise ValidationError(f"No parser available for file type: {file_type.value}")
        return parser.parse(content)
