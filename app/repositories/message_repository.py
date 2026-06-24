"""Message data access repository."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message, MessageRole


class MessageRepository:
    """Persistence layer for chat messages."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        citations: list[dict[str, Any]] | None = None,
        retrieval_metadata: dict[str, Any] | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations=citations or [],
            retrieval_metadata=retrieval_metadata or {},
        )
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        return message
