"""Unit tests for upload file validation."""

import pytest
from fastapi import UploadFile

from app.config.settings import Settings
from app.exceptions import ValidationError
from app.services.file_validator import validate_upload


@pytest.fixture
def settings() -> Settings:
    return Settings(
        secret_key="test-secret-key-minimum-32-characters-long",
        database_url="sqlite+aiosqlite:///./test.db",
        max_upload_size_mb=1,
        allowed_extensions=["pdf", "docx", "txt"],
    )


def _upload_file(filename: str, content: bytes, content_type: str | None = None) -> UploadFile:
    return UploadFile(filename=filename, file=__import__("io").BytesIO(content), headers={})


@pytest.mark.asyncio
async def test_validate_txt_upload(settings: Settings) -> None:
    """Valid UTF-8 text files pass validation."""
    upload = _upload_file("notes.txt", b"Enterprise knowledge base content.")
    result = await validate_upload(upload, settings)
    assert result.file_type.value == "txt"
    assert result.safe_filename == "notes.txt"


@pytest.mark.asyncio
async def test_validate_rejects_empty_file(settings: Settings) -> None:
    """Empty uploads are rejected."""
    upload = _upload_file("empty.txt", b"")
    with pytest.raises(ValidationError, match="empty"):
        await validate_upload(upload, settings)


@pytest.mark.asyncio
async def test_validate_rejects_disallowed_extension(settings: Settings) -> None:
    """Unsupported extensions are rejected."""
    upload = _upload_file("script.exe", b"MZ")
    with pytest.raises(ValidationError, match="not allowed"):
        await validate_upload(upload, settings)


@pytest.mark.asyncio
async def test_validate_rejects_pdf_with_wrong_magic(settings: Settings) -> None:
    """PDF extension with non-PDF content is rejected."""
    upload = _upload_file("fake.pdf", b"not a pdf")
    with pytest.raises(ValidationError, match="does not match"):
        await validate_upload(upload, settings)


@pytest.mark.asyncio
async def test_validate_rejects_oversized_file(settings: Settings) -> None:
    """Files exceeding size limit are rejected."""
    upload = _upload_file("large.txt", b"x" * (1024 * 1024 + 1))
    with pytest.raises(ValidationError, match="maximum size"):
        await validate_upload(upload, settings)
