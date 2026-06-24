"""LangGraph RAG pipeline orchestration."""

import re
import time
from typing import Any, TypedDict
from uuid import UUID

from langgraph.graph import END, StateGraph

from app.config.settings import Settings
from app.rag.citations import generate_citations
from app.rag.embeddings import EmbeddingService
from app.rag.llm import LLMService
from app.rag.prompts import build_context, build_prompt
from app.rag.reranker import Reranker
from app.rag.types import RAGResult, RetrievedChunk
from app.rag.vector_store import VectorStore


class RAGState(TypedDict, total=False):
    """LangGraph state for the RAG pipeline."""

    query: str
    user_id: str
    document_ids: list[str]
    cleaned_query: str
    retrieved: list[RetrievedChunk]
    reranked: list[RetrievedChunk]
    context: str
    answer: str
    citations: list[dict[str, Any]]
    retrieval_latency_ms: float
    llm_latency_ms: float
    model_name: str


class RAGPipeline:
    """End-to-end retrieval-augmented generation pipeline."""

    def __init__(
        self,
        *,
        settings: Settings,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        reranker: Reranker,
        llm_service: LLMService,
    ) -> None:
        self._settings = settings
        self._embeddings = embedding_service
        self._vector_store = vector_store
        self._reranker = reranker
        self._llm = llm_service
        self._graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(RAGState)
        graph.add_node("clean_query", self._clean_query)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("rerank", self._rerank)
        graph.add_node("build_context", self._build_context)
        graph.add_node("generate", self._generate)
        graph.add_node("cite", self._cite)

        graph.set_entry_point("clean_query")
        graph.add_edge("clean_query", "retrieve")
        graph.add_edge("retrieve", "rerank")
        graph.add_edge("rerank", "build_context")
        graph.add_edge("build_context", "generate")
        graph.add_edge("generate", "cite")
        graph.add_edge("cite", END)
        return graph.compile()

    async def run(
        self,
        *,
        query: str,
        user_id: UUID,
        document_ids: list[UUID] | None = None,
    ) -> RAGResult:
        """Execute the full RAG pipeline."""
        initial: RAGState = {
            "query": query,
            "user_id": str(user_id),
            "document_ids": [str(d) for d in document_ids] if document_ids else [],
        }
        final = await self._graph.ainvoke(initial)
        return RAGResult(
            answer=final.get("answer", ""),
            citations=final.get("citations", []),
            retrieval_metadata={
                "retrieval_latency_ms": final.get("retrieval_latency_ms", 0.0),
                "llm_latency_ms": final.get("llm_latency_ms", 0.0),
                "model_name": final.get("model_name", ""),
                "chunks_retrieved": len(final.get("reranked", [])),
            },
        )

    async def prepare_context(
        self,
        *,
        query: str,
        user_id: UUID,
        document_ids: list[UUID] | None = None,
    ) -> RAGState:
        """Run retrieval and context building without LLM generation."""
        initial: RAGState = {
            "query": query,
            "user_id": str(user_id),
            "document_ids": [str(d) for d in document_ids] if document_ids else [],
        }
        state = await self._clean_query(initial)
        initial.update(state)
        state = await self._retrieve(initial)
        initial.update(state)
        state = await self._rerank(initial)
        initial.update(state)
        state = await self._build_context(initial)
        initial.update(state)
        state = await self._cite(initial)
        initial.update(state)
        return initial

    async def _clean_query(self, state: RAGState) -> dict[str, Any]:
        cleaned = re.sub(r"\s+", " ", state["query"].strip())
        return {"cleaned_query": cleaned}

    async def _retrieve(self, state: RAGState) -> dict[str, Any]:
        start = time.perf_counter()
        query_vector = self._embeddings.embed_query(state["cleaned_query"])
        doc_ids = [UUID(d) for d in state.get("document_ids", [])] or None
        retrieved = self._vector_store.search(
            query_vector=query_vector,
            user_id=UUID(state["user_id"]),
            top_k=self._settings.retrieval_top_k,
            document_ids=doc_ids,
        )
        latency = (time.perf_counter() - start) * 1000
        return {"retrieved": retrieved, "retrieval_latency_ms": latency}

    async def _rerank(self, state: RAGState) -> dict[str, Any]:
        reranked = self._reranker.rerank(state["cleaned_query"], state.get("retrieved", []))
        return {"reranked": reranked}

    async def _build_context(self, state: RAGState) -> dict[str, Any]:
        context = build_context(state.get("reranked", []), self._settings.max_context_tokens)
        if not context:
            context = "No relevant documents found in the knowledge base."
        return {"context": context}

    async def _generate(self, state: RAGState) -> dict[str, Any]:
        start = time.perf_counter()
        messages = build_prompt(state["cleaned_query"], state["context"])
        answer = await self._llm.generate(messages)
        latency = (time.perf_counter() - start) * 1000
        return {
            "answer": answer,
            "llm_latency_ms": latency,
            "model_name": self._llm.model_name,
        }

    async def _cite(self, state: RAGState) -> dict[str, Any]:
        citations = generate_citations(state.get("reranked", []))
        return {"citations": citations}
