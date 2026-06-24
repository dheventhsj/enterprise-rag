"""Initial database schema.

Revision ID: 001
Revises:
Create Date: 2026-06-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("original_filename", sa.String(length=512), nullable=False),
        sa.Column(
            "file_type",
            sa.Enum("pdf", "docx", "txt", name="document_type"),
            nullable=False,
        ),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="document_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])

    op.create_table(
        "chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("qdrant_point_id", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
    )
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])
    op.create_index("ix_chunks_qdrant_point_id", "chunks", ["qdrant_point_id"])

    op.create_table(
        "embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("dimension", sa.Integer(), nullable=False),
        sa.Column("qdrant_collection", sa.String(length=255), nullable=False),
        sa.Column("qdrant_point_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["chunk_id"], ["chunks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chunk_id"),
        sa.UniqueConstraint("qdrant_point_id"),
    )
    op.create_index("ix_embeddings_qdrant_point_id", "embeddings", ["qdrant_point_id"])

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "assistant", "system", name="message_role"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column(
            "retrieval_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "rating",
            sa.Enum("positive", "negative", name="feedback_rating"),
            nullable=False,
        ),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id"),
    )
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])

    op.create_table(
        "logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("retrieval_latency_ms", sa.Float(), nullable=True),
        sa.Column("llm_latency_ms", sa.Float(), nullable=True),
        sa.Column("chunks_retrieved", sa.Integer(), nullable=True),
        sa.Column("model_name", sa.String(length=255), nullable=True),
        sa.Column("extra", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_logs_endpoint", "logs", ["endpoint"])
    op.create_index("ix_logs_user_id", "logs", ["user_id"])


def downgrade() -> None:
    op.drop_table("logs")
    op.drop_table("feedback")
    op.drop_table("messages")
    op.drop_table("embeddings")
    op.drop_table("chunks")
    op.drop_table("conversations")
    op.drop_table("documents")
    op.drop_table("users")
    sa.Enum(name="feedback_rating").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="message_role").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="document_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="document_type").drop(op.get_bind(), checkfirst=True)
