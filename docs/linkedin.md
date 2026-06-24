# LinkedIn Deliverables

## Project Description

**Enterprise RAG Platform** — Production-grade Retrieval-Augmented Generation system enabling organizations to upload PDF, DOCX, and TXT documents, perform semantic search via Qdrant, and generate grounded AI answers with source citations.

Built with FastAPI, LangGraph, PostgreSQL, Redis, sentence-transformers, and OpenAI/Gemini. Features multi-user JWT auth, streaming responses, Prometheus monitoring, Docker deployment, and CI/CD.

**GitHub:** `enterprise-rag`

---

## Resume Bullet Points

- Architected and built a production **Enterprise RAG platform** using **FastAPI**, **LangGraph**, **Qdrant**, and **PostgreSQL**, supporting PDF/DOCX/TXT ingestion, semantic retrieval, reranking, and citation-grounded LLM answers for multi-tenant users.

- Implemented **clean architecture** with repository pattern, dependency injection, JWT authentication, Redis rate limiting, and **Prometheus/Grafana** observability exposing request, retrieval, and LLM latency metrics.

- Designed end-to-end **RAG pipeline** — document parsing, token-aware chunking, sentence-transformer embeddings, vector search, reranking, and streaming SSE chat with conversation memory.

- Containerized the full stack with **Docker Compose** (API, Postgres, Redis, Qdrant, Prometheus, Grafana) and established **GitHub Actions CI/CD** for lint, test, and build on every push.

---

## LinkedIn Post

🚀 Just shipped an Enterprise RAG Platform from scratch.

What it does:
✅ Upload PDFs, DOCX, and TXT files
✅ Semantic search with Qdrant + reranking
✅ Grounded AI answers with source citations
✅ Multi-user auth, streaming chat, conversation history
✅ Full observability with Prometheus + Grafana
✅ Production-ready Docker deployment

Tech stack: Python · FastAPI · LangGraph · PostgreSQL · Redis · Qdrant · OpenAI · Docker · GitHub Actions

This isn't a notebook demo — it's a real software project with clean architecture, 12-factor config, typed APIs, and CI/CD.

Building AI systems that enterprises can actually deploy. 🔧

#AI #RAG #FastAPI #LangChain #MachineLearning #SoftwareEngineering #LLM #Python
