"""Background document ingestion pipeline."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config.settings import Settings
from app.database.session import get_session_factory
from app.logging.logger import logger
from app.models.document import DocumentStatus
from app.rag.chunking import TextChunker
from app.rag.embeddings_factory import create_embedding_service
from app.rag.vector_store import VectorStore
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.parsers.registry import DocumentParserRegistry
from app.services.storage.base import StorageBackend


class IngestionService:
    """Parse, chunk, embed, and index uploaded documents."""

    def __init__(
        self,
        *,
        settings: Settings,
        storage: StorageBackend,
        parser_registry: DocumentParserRegistry,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        embedding_service=None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self._settings = settings
        self._storage = storage
        self._parsers = parser_registry
        self._session_factory = session_factory or get_session_factory(settings)
        self._embeddings = embedding_service or create_embedding_service(settings)
        self._vector_store = vector_store or VectorStore(settings)
        self._chunker = TextChunker(settings)

    async def process_document(self, document_id: UUID) -> None:
        """Run full ingestion for a document in a dedicated database session."""
        async with self._session_factory() as session:
            doc_repo = DocumentRepository(session)
            chunk_repo = ChunkRepository(session)
            embed_repo = EmbeddingRepository(session)
            document = await doc_repo.get_by_id(document_id)
            if document is None:
                logger.error("Ingestion skipped: document %s not found", document_id)
                return

            try:
                await doc_repo.update_status(document, status=DocumentStatus.PROCESSING)
                await session.commit()

                content = await self._storage.read(document.storage_path)
                parsed = self._parsers.parse(file_type=document.file_type, content=content)
                text_chunks = self._chunker.chunk_document(parsed)

                if not text_chunks:
                    raise ValueError("No chunks generated from document")

                db_chunks = await chunk_repo.create_batch(
                    document_id=document.id,
                    chunks=text_chunks,
                )
                vectors = self._embeddings.embed_texts([c.content for c in text_chunks])
                point_ids = self._vector_store.upsert_vectors(
                    user_id=document.user_id,
                    document_id=document.id,
                    chunk_ids=[c.id for c in db_chunks],
                    vectors=vectors,
                    payloads=[
                        {
                            "content": chunk.content,
                            "chunk_index": chunk.chunk_index,
                            "page_number": chunk.page_number,
                            "original_filename": document.original_filename,
                        }
                        for chunk in db_chunks
                    ],
                )
                await chunk_repo.update_qdrant_ids(db_chunks, point_ids)
                await embed_repo.create_batch(
                    chunk_ids=[c.id for c in db_chunks],
                    point_ids=point_ids,
                    model_name=self._settings.embedding_model,
                    dimension=self._settings.embedding_dimension,
                    collection=self._settings.qdrant_collection,
                )

                await doc_repo.update_status(
                    document,
                    status=DocumentStatus.COMPLETED,
                    chunk_count=len(db_chunks),
                    extra_metadata={
                        "page_count": parsed.page_count,
                        "character_count": parsed.character_count,
                        "parsed": True,
                        "embedded": True,
                    },
                )
                await session.commit()
                logger.info(
                    "Document ingestion completed",
                    extra={
                        "document_id": str(document_id),
                        "chunk_count": len(db_chunks),
                    },
                )
            except Exception as exc:
                await session.rollback()
                document = await doc_repo.get_by_id(document_id)
                if document is not None:
                    await doc_repo.update_status(
                        document,
                        status=DocumentStatus.FAILED,
                        error_message=str(exc),
                    )
                    await session.commit()
                logger.exception(
                    "Document ingestion failed for %s",
                    document_id,
                    extra={"error": str(exc)},
                )
