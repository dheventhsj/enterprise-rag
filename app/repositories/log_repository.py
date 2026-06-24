"""Query audit log repository."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log import QueryLog


class QueryLogRepository:
    """Persistence layer for API query logs."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID | None,
        endpoint: str,
        method: str,
        query_text: str | None,
        status_code: int,
        latency_ms: float,
        retrieval_latency_ms: float | None = None,
        llm_latency_ms: float | None = None,
        chunks_retrieved: int | None = None,
        model_name: str | None = None,
        extra: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> QueryLog:
        log = QueryLog(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            query_text=query_text,
            status_code=status_code,
            latency_ms=latency_ms,
            retrieval_latency_ms=retrieval_latency_ms,
            llm_latency_ms=llm_latency_ms,
            chunks_retrieved=chunks_retrieved,
            model_name=model_name,
            extra=extra or {},
            error_message=error_message,
        )
        self._session.add(log)
        await self._session.flush()
        return log
