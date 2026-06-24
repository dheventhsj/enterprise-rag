"""Shared FastAPI dependency injection providers."""

from functools import lru_cache
from pathlib import Path

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.database.session import get_db_session
from app.rag.embeddings_factory import create_embedding_service
from app.rag.llm import LLMService
from app.rag.pipeline import RAGPipeline
from app.rag.reranker import Reranker
from app.rag.vector_store import VectorStore
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.log_repository import QueryLogRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.ingestion_service import IngestionService
from app.services.parsers.registry import DocumentParserRegistry
from app.services.storage.base import LocalStorageBackend, StorageBackend
from app.services.upload_service import UploadService


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(session)


async def get_document_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentRepository:
    return DocumentRepository(session)


async def get_conversation_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationRepository:
    return ConversationRepository(session)


async def get_message_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MessageRepository:
    return MessageRepository(session)


async def get_log_repository(
    session: AsyncSession = Depends(get_db_session),
) -> QueryLogRepository:
    return QueryLogRepository(session)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(user_repository, settings)


@lru_cache
def get_storage_backend() -> StorageBackend:
    settings = get_settings()
    return LocalStorageBackend(Path(settings.upload_dir))


@lru_cache
def get_parser_registry() -> DocumentParserRegistry:
    return DocumentParserRegistry()


@lru_cache
def get_embedding_service():
    return create_embedding_service(get_settings())


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore(get_settings())


@lru_cache
def get_reranker() -> Reranker:
    return Reranker(get_settings())


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService(get_settings())


@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    settings = get_settings()
    return RAGPipeline(
        settings=settings,
        embedding_service=get_embedding_service(),
        vector_store=get_vector_store(),
        reranker=get_reranker(),
        llm_service=get_llm_service(),
    )


def get_ingestion_service(
    settings: Settings = Depends(get_settings),
    storage: StorageBackend = Depends(get_storage_backend),
    parser_registry: DocumentParserRegistry = Depends(get_parser_registry),
    embedding_service=Depends(get_embedding_service),
    vector_store: VectorStore = Depends(get_vector_store),
) -> IngestionService:
    return IngestionService(
        settings=settings,
        storage=storage,
        parser_registry=parser_registry,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )


def get_upload_service(
    document_repository: DocumentRepository = Depends(get_document_repository),
    storage: StorageBackend = Depends(get_storage_backend),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
    settings: Settings = Depends(get_settings),
    vector_store: VectorStore = Depends(get_vector_store),
) -> UploadService:
    return UploadService(
        document_repository=document_repository,
        storage=storage,
        ingestion_service=ingestion_service,
        settings=settings,
        vector_store=vector_store,
    )


def get_chat_service(
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
    message_repository: MessageRepository = Depends(get_message_repository),
    log_repository: QueryLogRepository = Depends(get_log_repository),
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline),
    llm_service: LLMService = Depends(get_llm_service),
) -> ChatService:
    return ChatService(
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        log_repository=log_repository,
        rag_pipeline=rag_pipeline,
        llm_service=llm_service,
    )
