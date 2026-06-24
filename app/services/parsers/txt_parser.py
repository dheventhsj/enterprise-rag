"""Plain text document parser."""

from app.exceptions import ValidationError
from app.services.parsers.base import ParsedDocument, ParsedPage


class TXTParser:
    """Extract text from UTF-8 plain text files."""

    def parse(self, content: bytes) -> ParsedDocument:
        """Parse UTF-8 text bytes."""
        try:
            text = content.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise ValidationError("Text file must be valid UTF-8") from exc

        if not text:
            raise ValidationError("Text file is empty")

        return ParsedDocument(pages=[ParsedPage(page_number=1, text=text)])
