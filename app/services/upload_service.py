"""Document upload orchestration."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import BackgroundTasks, UploadFile

from app.config.settings import Settings
from app.exceptions import NotFoundError
from app.logging.logger import logger
from app.models.document import Document
from app.models.user import User
from app.rag.vector_store import VectorStore
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse
from app.services.file_validator import validate_upload
from app.services.ingestion_service import IngestionService
from app.services.storage.base import StorageBackend


class UploadService:
    """Handle validated file uploads and schedule background ingestion."""

    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        storage: StorageBackend,
        ingestion_service: IngestionService,
        settings: Settings,
        vector_store: VectorStore | None = None,
    ) -> None:
        self._documents = document_repository
        self._storage = storage
        self._ingestion = ingestion_service
        self._settings = settings
        self._vector_store = vector_store

    async def upload_file(
        self,
        *,
        user: User,
        file: UploadFile,
        background_tasks: BackgroundTasks,
    ) -> DocumentResponse:
        """Validate, store, and enqueue ingestion for an uploaded file."""
        validated = await validate_upload(file, self._settings)

        document_id = uuid.uuid4()
        stored_filename = f"{document_id}.{validated.file_type.value}"
        relative_path = str(Path(str(user.id)) / str(document_id) / stored_filename)

        storage_path = await self._storage.save(
            relative_path=relative_path,
            content=validated.content,
        )

        document = await self._documents.create(
            user_id=user.id,
            filename=stored_filename,
            original_filename=validated.original_filename,
            file_type=validated.file_type,
            file_size_bytes=len(validated.content),
            storage_path=storage_path,
            extra_metadata={
                "content_type": validated.content_type,
            },
        )

        background_tasks.add_task(self._ingestion.process_document, document.id)
        logger.info(
            "Document uploaded",
            extra={
                "document_id": str(document.id),
                "user_id": str(user.id),
                "file_type": validated.file_type.value,
            },
        )
        return DocumentResponse.model_validate(document)

    async def list_documents(self, user: User) -> list[DocumentResponse]:
        """Return all documents for the authenticated user."""
        documents = await self._documents.list_for_user(user.id)
        return [DocumentResponse.model_validate(doc) for doc in documents]

    async def get_document(self, *, user: User, document_id: uuid.UUID) -> DocumentResponse:
        """Return a single document if owned by the user."""
        document = await self._documents.get_by_id_for_user(document_id, user.id)
        if document is None:
            raise NotFoundError("Document not found")
        return DocumentResponse.model_validate(document)

    async def delete_document(self, *, user: User, document_id: uuid.UUID) -> None:
        """Delete document, chunks, vectors, and stored file."""
        document = await self._documents.get_by_id_for_user(document_id, user.id)
        if document is None:
            raise NotFoundError("Document not found")

        if self._vector_store:
            self._vector_store.delete_by_document(
                user_id=user.id,
                document_id=document.id,
            )

        await self._storage.delete(document.storage_path)
        await self._documents.delete(document)
