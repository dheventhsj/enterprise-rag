"""Document data access repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus, DocumentType


class DocumentRepository:
    """Persistence layer for uploaded documents."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, document_id: UUID) -> Document | None:
        """Fetch a document by primary key."""
        result = await self._session.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def get_by_id_for_user(self, document_id: UUID, user_id: UUID) -> Document | None:
        """Fetch a document scoped to a specific user."""
        result = await self._session.execute(
            select(Document).where(Document.id == document_id, Document.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[Document]:
        """List all documents belonging to a user."""
        result = await self._session.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        user_id: UUID,
        filename: str,
        original_filename: str,
        file_type: DocumentType,
        file_size_bytes: int,
        storage_path: str,
        extra_metadata: dict | None = None,
    ) -> Document:
        """Create a new document record."""
        document = Document(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            storage_path=storage_path,
            status=DocumentStatus.PENDING,
            extra_metadata=extra_metadata or {},
        )
        self._session.add(document)
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def update_status(
        self,
        document: Document,
        *,
        status: DocumentStatus,
        error_message: str | None = None,
        chunk_count: int | None = None,
        extra_metadata: dict | None = None,
    ) -> Document:
        """Update document ingestion status and optional fields."""
        document.status = status
        if error_message is not None:
            document.error_message = error_message
        if chunk_count is not None:
            document.chunk_count = chunk_count
        if extra_metadata is not None:
            document.extra_metadata = {**document.extra_metadata, **extra_metadata}
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def delete(self, document: Document) -> None:
        """Delete a document record (cascades to chunks)."""
        await self._session.delete(document)
        await self._session.flush()
