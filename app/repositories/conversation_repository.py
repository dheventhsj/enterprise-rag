"""Conversation data access repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation


class ConversationRepository:
    """Persistence layer for chat conversations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id_for_user(
        self, conversation_id: UUID, user_id: UUID
    ) -> Conversation | None:
        result = await self._session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[Conversation]:
        result = await self._session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, *, user_id: UUID, title: str | None = None) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        self._session.add(conversation)
        await self._session.flush()
        await self._session.refresh(conversation)
        return conversation

    async def update_title(self, conversation: Conversation, title: str) -> Conversation:
        conversation.title = title
        await self._session.flush()
        return conversation
