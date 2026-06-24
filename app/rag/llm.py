"""LLM provider abstraction."""

from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config.settings import Settings
from app.exceptions import ExternalServiceError, ValidationError


class LLMService:
    """Unified LLM interface for OpenAI and Gemini."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model = self._build_model()

    def _build_model(self):
        if self._settings.llm_provider == "openai":
            if not self._settings.openai_api_key:
                raise ValidationError("OPENAI_API_KEY is not configured")
            return ChatOpenAI(
                model=self._settings.openai_model,
                api_key=self._settings.openai_api_key,
                temperature=0.2,
                streaming=True,
            )
        if not self._settings.gemini_api_key:
            raise ValidationError("GEMINI_API_KEY is not configured")
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=self._settings.gemini_model,
            google_api_key=self._settings.gemini_api_key,
            temperature=0.2,
        )

    @property
    def model_name(self) -> str:
        if self._settings.llm_provider == "openai":
            return self._settings.openai_model
        return self._settings.gemini_model

    async def generate(self, messages: list[dict[str, str]]) -> str:
        """Generate a complete response."""
        lc_messages = self._to_lc_messages(messages)
        try:
            response = await self._model.ainvoke(lc_messages)
        except Exception as exc:
            raise ExternalServiceError(str(exc), service=self._settings.llm_provider) from exc
        content = response.content
        return content if isinstance(content, str) else str(content)

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        """Stream response tokens."""
        lc_messages = self._to_lc_messages(messages)
        try:
            async for chunk in self._model.astream(lc_messages):
                if isinstance(chunk, AIMessage) and chunk.content:
                    yield chunk.content if isinstance(chunk.content, str) else str(chunk.content)
        except Exception as exc:
            raise ExternalServiceError(str(exc), service=self._settings.llm_provider) from exc

    @staticmethod
    def _to_lc_messages(messages: list[dict[str, str]]):
        mapped = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                mapped.append(SystemMessage(content=content))
            elif role == "assistant":
                mapped.append(AIMessage(content=content))
            else:
                mapped.append(HumanMessage(content=content))
        return mapped
