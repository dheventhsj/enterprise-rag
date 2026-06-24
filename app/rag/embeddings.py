"""Embedding generation service."""

from functools import lru_cache

import numpy as np

from app.config.settings import Settings
from app.logging.logger import logger


@lru_cache
def _load_model(model_name: str):
    """Lazy-load sentence-transformers model."""
    from sentence_transformers import SentenceTransformer

    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name)


class EmbeddingService:
    """Generate dense vector embeddings for text."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model = None

    def _get_model(self):
        if self._model is None:
            self._model = _load_model(self._settings.embedding_model)
        return self._model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""
        if not texts:
            return []
        model = self._get_model()
        vectors = model.encode(
            texts,
            batch_size=self._settings.embedding_batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.asarray(vectors).tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        return self.embed_texts([query])[0]
