"""Document API schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    """Uploaded document metadata returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    original_filename: str
    file_type: DocumentType
    file_size_bytes: int
    status: DocumentStatus
    chunk_count: int
    error_message: str | None
    extra_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """List of user documents."""

    documents: list[DocumentResponse]
    total: int
