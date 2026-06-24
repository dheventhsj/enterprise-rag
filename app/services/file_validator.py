"""Upload file validation utilities."""

import re
from dataclasses import dataclass

from fastapi import UploadFile

from app.config.settings import Settings
from app.exceptions import ValidationError
from app.models.document import DocumentType

_MAGIC_SIGNATURES: dict[DocumentType, list[bytes]] = {
    DocumentType.PDF: [b"%PDF"],
    DocumentType.DOCX: [b"PK\x03\x04"],
    DocumentType.TXT: [],
}

_MIME_MAP: dict[str, DocumentType] = {
    "application/pdf": DocumentType.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentType.DOCX,
    "text/plain": DocumentType.TXT,
}


@dataclass(frozen=True)
class ValidatedUpload:
    """Result of successful upload validation."""

    original_filename: str
    safe_filename: str
    file_type: DocumentType
    content: bytes
    content_type: str | None


def _sanitize_filename(filename: str) -> str:
    """Strip path components and unsafe characters from a filename."""
    name = filename.replace("\\", "/").split("/")[-1].strip()
    name = re.sub(r"[^\w.\- ]", "_", name)
    if not name or name in {".", ".."}:
        raise ValidationError("Invalid filename")
    return name


def _extension(filename: str) -> str:
    """Return lowercase file extension without dot."""
    if "." not in filename:
        raise ValidationError("File must have an extension")
    return filename.rsplit(".", 1)[-1].lower()


def _detect_type_from_content(content: bytes, extension: str) -> DocumentType:
    """Detect document type from magic bytes and extension."""
    try:
        doc_type = DocumentType(extension)
    except ValueError as exc:
        raise ValidationError(f"Unsupported file extension: {extension}") from exc

    signatures = _MAGIC_SIGNATURES[doc_type]
    if signatures and not any(content.startswith(sig) for sig in signatures):
        raise ValidationError(f"File content does not match .{extension} format")

    if doc_type == DocumentType.TXT:
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError("Text file must be valid UTF-8") from exc

    return doc_type


async def validate_upload(file: UploadFile, settings: Settings) -> ValidatedUpload:
    """Validate uploaded file size, extension, and content signature."""
    if not file.filename:
        raise ValidationError("Filename is required")

    safe_filename = _sanitize_filename(file.filename)
    extension = _extension(safe_filename)

    if extension not in settings.allowed_extensions:
        raise ValidationError(
            f"File type '.{extension}' is not allowed",
            details={"allowed_extensions": settings.allowed_extensions},
        )

    content = await file.read()
    if not content:
        raise ValidationError("Uploaded file is empty")

    if len(content) > settings.max_upload_size_bytes:
        raise ValidationError(
            f"File exceeds maximum size of {settings.max_upload_size_mb} MB",
            details={"max_upload_size_mb": settings.max_upload_size_mb},
        )

    file_type = _detect_type_from_content(content, extension)

    if file.content_type and file.content_type in _MIME_MAP:
        mime_type = _MIME_MAP[file.content_type]
        if mime_type != file_type:
            raise ValidationError(
                "Content-Type header does not match file extension",
                details={"content_type": file.content_type, "extension": extension},
            )

    return ValidatedUpload(
        original_filename=file.filename,
        safe_filename=safe_filename,
        file_type=file_type,
        content=content,
        content_type=file.content_type,
    )
