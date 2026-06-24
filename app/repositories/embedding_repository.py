"""Embedding metadata repository."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embedding import Embedding


class EmbeddingRepository:
    """Persistence layer for embedding metadata."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_batch(
        self,
        *,
        chunk_ids: list[UUID],
        point_ids: list[str],
        model_name: str,
        dimension: int,
        collection: str,
    ) -> list[Embedding]:
        """Persist embedding metadata linked to Qdrant points."""
        records = [
            Embedding(
                chunk_id=chunk_id,
                model_name=model_name,
                dimension=dimension,
                qdrant_collection=collection,
                qdrant_point_id=point_id,
            )
            for chunk_id, point_id in zip(chunk_ids, point_ids, strict=True)
        ]
        self._session.add_all(records)
        await self._session.flush()
        return records
