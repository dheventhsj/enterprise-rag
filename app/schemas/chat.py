"""Chat API schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """RAG chat request payload."""

    message: str = Field(..., min_length=1, max_length=4096)
    conversation_id: UUID | None = None
    document_ids: list[UUID] | None = None
    stream: bool = False


class MessageResponse(BaseModel):
    """Chat message response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    retrieval_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ChatResponse(BaseModel):
    """Synchronous chat response."""

    conversation_id: UUID
    message: MessageResponse


class ConversationResponse(BaseModel):
    """Conversation with optional messages."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    """List of conversations."""

    conversations: list[ConversationResponse]
    total: int
