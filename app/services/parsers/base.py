"""Document parsing data structures."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParsedPage:
    """Text extracted from a single page or section."""

    page_number: int
    text: str


@dataclass(frozen=True)
class ParsedDocument:
    """Structured output from document parsing."""

    pages: list[ParsedPage] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Concatenate all page text."""
        return "\n\n".join(page.text for page in self.pages if page.text.strip())

    @property
    def page_count(self) -> int:
        """Number of parsed pages."""
        return len(self.pages)

    @property
    def character_count(self) -> int:
        """Total character count across all pages."""
        return len(self.full_text)
