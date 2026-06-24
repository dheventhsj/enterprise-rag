"""OpenAI API embedding service for serverless deployments."""

from openai import OpenAI

from app.config.settings import Settings
from app.exceptions import ValidationError


class OpenAIEmbeddingService:
    """Generate embeddings via OpenAI API (no local ML models)."""

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise ValidationError("OPENAI_API_KEY is required for OpenAI embeddings")
        self._settings = settings
        self._client = OpenAI(api_key=settings.openai_api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""
        if not texts:
            return []
        response = self._client.embeddings.create(
            input=texts,
            model=self._settings.openai_embedding_model,
        )
        return [item.embedding for item in response.data]

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        return self.embed_texts([query])[0]
