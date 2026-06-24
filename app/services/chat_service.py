"""Chat and RAG orchestration service."""

import json
import time
from collections.abc import AsyncIterator
from uuid import UUID

from app.exceptions import NotFoundError
from app.models.message import MessageRole
from app.models.user import User
from app.rag.llm import LLMService
from app.rag.pipeline import RAGPipeline
from app.rag.prompts import build_prompt
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.log_repository import QueryLogRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse, MessageResponse


class ChatService:
    """Handle RAG-powered chat with conversation memory."""

    def __init__(
        self,
        *,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        log_repository: QueryLogRepository,
        rag_pipeline: RAGPipeline,
        llm_service: LLMService,
    ) -> None:
        self._conversations = conversation_repository
        self._messages = message_repository
        self._logs = log_repository
        self._rag = rag_pipeline
        self._llm = llm_service

    async def chat(self, *, user: User, request: ChatRequest) -> ChatResponse:
        """Run RAG pipeline and persist conversation."""
        start = time.perf_counter()
        conversation = await self._get_or_create_conversation(user, request.conversation_id)
        await self._messages.create(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message,
        )

        result = await self._rag.run(
            query=request.message,
            user_id=user.id,
            document_ids=request.document_ids,
        )

        assistant = await self._messages.create(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=result.answer,
            citations=result.citations,
            retrieval_metadata=result.retrieval_metadata,
        )

        if not conversation.title:
            await self._conversations.update_title(conversation, request.message[:80])

        await self._log_chat(user, request.message, result.retrieval_metadata, start)
        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse.model_validate(assistant),
        )

    async def stream_chat(self, *, user: User, request: ChatRequest) -> AsyncIterator[str]:
        """Stream RAG response as Server-Sent Events."""
        start = time.perf_counter()
        conversation = await self._get_or_create_conversation(user, request.conversation_id)
        await self._messages.create(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message,
        )

        state = await self._rag.prepare_context(
            query=request.message,
            user_id=user.id,
            document_ids=request.document_ids,
        )
        messages = build_prompt(state["cleaned_query"], state["context"])
        citations = state.get("citations", [])

        full_answer = ""
        llm_start = time.perf_counter()
        async for token in self._llm.stream(messages):
            full_answer += token
            yield f"data: {json.dumps({'token': token})}\n\n"
        llm_latency = (time.perf_counter() - llm_start) * 1000

        assistant = await self._messages.create(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=full_answer,
            citations=citations,
            retrieval_metadata={
                "retrieval_latency_ms": state.get("retrieval_latency_ms", 0.0),
                "llm_latency_ms": llm_latency,
                "model_name": self._llm.model_name,
                "chunks_retrieved": len(state.get("reranked", [])),
            },
        )

        if not conversation.title:
            await self._conversations.update_title(conversation, request.message[:80])

        yield f"data: {json.dumps({'done': True, 'message_id': str(assistant.id), 'citations': citations})}\n\n"

        await self._log_chat(
            user,
            request.message,
            {
                "retrieval_latency_ms": state.get("retrieval_latency_ms", 0.0),
                "llm_latency_ms": llm_latency,
                "model_name": self._llm.model_name,
                "chunks_retrieved": len(state.get("reranked", [])),
            },
            start,
            endpoint="/chat/stream",
        )

    async def get_history(self, user: User) -> list[ConversationResponse]:
        """Return conversation list for a user."""
        conversations = await self._conversations.list_for_user(user.id)
        return [ConversationResponse.model_validate(c) for c in conversations]

    async def get_conversation(
        self, *, user: User, conversation_id: UUID
    ) -> ConversationResponse:
        """Return a single conversation with messages."""
        conversation = await self._conversations.get_by_id_for_user(conversation_id, user.id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return ConversationResponse.model_validate(conversation)

    async def _get_or_create_conversation(self, user: User, conversation_id: UUID | None):
        if conversation_id:
            conversation = await self._conversations.get_by_id_for_user(
                conversation_id, user.id
            )
            if conversation is None:
                raise NotFoundError("Conversation not found")
            return conversation
        return await self._conversations.create(user_id=user.id)

    async def _log_chat(
        self,
        user: User,
        query: str,
        metadata: dict,
        start: float,
        endpoint: str = "/chat",
    ) -> None:
        latency = (time.perf_counter() - start) * 1000
        await self._logs.create(
            user_id=user.id,
            endpoint=endpoint,
            method="POST",
            query_text=query,
            status_code=200,
            latency_ms=latency,
            retrieval_latency_ms=metadata.get("retrieval_latency_ms"),
            llm_latency_ms=metadata.get("llm_latency_ms"),
            chunks_retrieved=metadata.get("chunks_retrieved"),
            model_name=metadata.get("model_name"),
        )
