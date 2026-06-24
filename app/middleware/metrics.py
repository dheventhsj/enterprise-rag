"""Prometheus metrics definitions."""

from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_duration_seconds",
    "RAG retrieval latency",
)

LLM_LATENCY = Histogram(
    "rag_llm_duration_seconds",
    "LLM generation latency",
)
