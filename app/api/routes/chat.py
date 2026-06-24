"""Chat API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_chat_service
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse, HistoryResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse, summary="Ask a question with RAG")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse | EventSourceResponse:
    """Generate a grounded answer using retrieved documents."""
    if request.stream:
        return EventSourceResponse(
            chat_service.stream_chat(user=current_user, request=request),
            media_type="text/event-stream",
        )
    return await chat_service.chat(user=current_user, request=request)


@router.get("/history", response_model=HistoryResponse, summary="List chat history")
async def history(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> HistoryResponse:
    """Return all conversations for the authenticated user."""
    conversations = await chat_service.get_history(current_user)
    return HistoryResponse(conversations=conversations, total=len(conversations))


@router.get(
    "/history/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation with messages",
)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationResponse:
    """Return a single conversation including all messages."""
    return await chat_service.get_conversation(
        user=current_user,
        conversation_id=conversation_id,
    )
