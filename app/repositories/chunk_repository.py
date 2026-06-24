"""Chunk data access repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk


class ChunkRepository:
    """Persistence layer for document chunks."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_batch(
        self,
        *,
        document_id: UUID,
        chunks: list,
    ) -> list[Chunk]:
        """Persist multiple chunks for a document."""
        records = [
            Chunk(
                document_id=document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                token_count=chunk.token_count,
                page_number=chunk.page_number,
            )
            for chunk in chunks
        ]
        self._session.add_all(records)
        await self._session.flush()
        for record in records:
            await self._session.refresh(record)
        return records

    async def update_qdrant_ids(self, chunks: list[Chunk], point_ids: list[str]) -> None:
        """Link chunks to Qdrant point IDs."""
        for chunk, point_id in zip(chunks, point_ids, strict=True):
            chunk.qdrant_point_id = point_id
        await self._session.flush()

    async def delete_by_document(self, document_id: UUID) -> None:
        """Delete all chunks for a document."""
        result = await self._session.execute(
            select(Chunk).where(Chunk.document_id == document_id)
        )
        for chunk in result.scalars().all():
            await self._session.delete(chunk)
