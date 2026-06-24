"""Qdrant vector store client."""

from typing import Any
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config.settings import Settings
from app.logging.logger import logger
from app.rag.types import RetrievedChunk


class VectorStore:
    """Manage dense vectors in Qdrant."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        if settings.qdrant_url:
            self._client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                check_compatibility=False,
            )
        else:
            self._client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key,
                check_compatibility=False,
            )
        self._collection = settings.qdrant_collection
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create collection if it does not exist."""
        try:
            collections = {c.name for c in self._client.get_collections().collections}
            if self._collection not in collections:
                self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=VectorParams(
                        size=self._settings.embedding_dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("Created Qdrant collection: %s", self._collection)
        except Exception as exc:
            logger.warning("Qdrant collection setup skipped: %s", exc)

    def upsert_vectors(
        self,
        *,
        user_id: UUID,
        document_id: UUID,
        chunk_ids: list[UUID],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> list[str]:
        """Insert or update vectors; return Qdrant point IDs."""
        point_ids: list[str] = []
        points: list[PointStruct] = []
        for chunk_id, vector, payload in zip(chunk_ids, vectors, payloads, strict=True):
            point_id = str(uuid4())
            point_ids.append(point_id)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "user_id": str(user_id),
                        "document_id": str(document_id),
                        "chunk_id": str(chunk_id),
                        **payload,
                    },
                )
            )
        self._client.upsert(collection_name=self._collection, points=points)
        return point_ids

    def search(
        self,
        *,
        query_vector: list[float],
        user_id: UUID,
        top_k: int,
        document_ids: list[UUID] | None = None,
    ) -> list[RetrievedChunk]:
        """Semantic search scoped to a user."""
        must_conditions = [
            FieldCondition(key="user_id", match=MatchValue(value=str(user_id))),
        ]
        if document_ids:
            should = [
                FieldCondition(key="document_id", match=MatchValue(value=str(doc_id)))
                for doc_id in document_ids
            ]
            query_filter = Filter(must=must_conditions, should=should)
        else:
            query_filter = Filter(must=must_conditions)

        results = self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
        )

        chunks: list[RetrievedChunk] = []
        for hit in results:
            payload = hit.payload or {}
            chunks.append(
                RetrievedChunk(
                    chunk_id=UUID(payload["chunk_id"]),
                    document_id=UUID(payload["document_id"]),
                    content=payload.get("content", ""),
                    score=float(hit.score or 0.0),
                    chunk_index=int(payload.get("chunk_index", 0)),
                    original_filename=payload.get("original_filename", ""),
                    page_number=payload.get("page_number"),
                )
            )
        return chunks

    def delete_by_document(self, *, user_id: UUID, document_id: UUID) -> None:
        """Remove all vectors for a document."""
        self._client.delete(
            collection_name=self._collection,
            points_selector=Filter(
                must=[
                    FieldCondition(key="user_id", match=MatchValue(value=str(user_id))),
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=str(document_id)),
                    ),
                ]
            ),
        )
