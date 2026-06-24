"""Unit tests for SQLAlchemy models."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.conversation import Conversation
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.embedding import Embedding
from app.models.message import Message, MessageRole
from app.models.user import User


@pytest.mark.asyncio
async def test_user_document_chunk_relationship(db_session: AsyncSession) -> None:
    """Verify core ingestion entity relationships persist correctly."""
    user = User(
        email="engineer@example.com",
        hashed_password="hashed",
        full_name="Test Engineer",
    )
    db_session.add(user)
    await db_session.flush()

    document = Document(
        user_id=user.id,
        filename="report.pdf",
        original_filename="Q4 Report.pdf",
        file_type=DocumentType.PDF,
        file_size_bytes=1024,
        storage_path="/uploads/report.pdf",
        status=DocumentStatus.COMPLETED,
        chunk_count=1,
    )
    db_session.add(document)
    await db_session.flush()

    chunk = Chunk(
        document_id=document.id,
        chunk_index=0,
        content="Revenue increased 12% year over year.",
        token_count=10,
        page_number=1,
        qdrant_point_id=str(uuid.uuid4()),
    )
    db_session.add(chunk)
    await db_session.flush()

    embedding = Embedding(
        chunk_id=chunk.id,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        dimension=384,
        qdrant_collection="enterprise_rag_chunks",
        qdrant_point_id=chunk.qdrant_point_id or "",
    )
    db_session.add(embedding)
    await db_session.commit()

    assert user.id is not None
    assert document.user_id == user.id
    assert chunk.document_id == document.id
    assert embedding.chunk_id == chunk.id


@pytest.mark.asyncio
async def test_conversation_message_flow(db_session: AsyncSession) -> None:
    """Verify chat history entities link user to messages."""
    user = User(email="chat@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.flush()

    conversation = Conversation(user_id=user.id, title="Policy questions")
    db_session.add(conversation)
    await db_session.flush()

    user_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="What is the PTO policy?",
    )
    assistant_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content="Employees receive 20 days PTO annually.",
        citations=[{"document_id": str(uuid.uuid4()), "chunk_index": 0}],
    )
    db_session.add_all([user_msg, assistant_msg])
    await db_session.commit()

    assert user_msg.conversation_id == conversation.id
    assert assistant_msg.citations[0]["chunk_index"] == 0
    assert assistant_msg.role.value == "assistant"
