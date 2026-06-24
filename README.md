# Enterprise RAG Platform

Production-grade Retrieval-Augmented Generation (RAG) platform for enterprise knowledge assistants.

## Features

- Multi-format document ingestion (PDF, DOCX, TXT)
- Semantic search with Qdrant + reranking
- Grounded LLM answers with source citations (OpenAI / Gemini)
- Multi-user JWT authentication
- Conversation memory and chat history
- Streaming responses (SSE)
- Prometheus metrics + Grafana dashboards
- Redis rate limiting
- Docker Compose local stack
- GitHub Actions CI/CD

## Architecture

See [docs/architecture.md](docs/architecture.md) | [docs/api.md](docs/api.md)

## Quick Start (Docker)

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY and OPENAI_API_KEY

cd docker
docker compose up --build
```

- API: http://localhost:8000/health
- Docs: http://localhost:8000/api/v1/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/upload` | Upload document |
| POST | `/api/v1/chat` | RAG chat (set `stream: true` for SSE) |
| GET | `/api/v1/history` | Chat history |
| GET | `/api/v1/documents` | List documents |
| DELETE | `/api/v1/document/{id}` | Delete document |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

## Deployment

- [Render](deployment/render.md)
- [AWS](deployment/aws.md)

## LinkedIn / Portfolio

See [docs/linkedin.md](docs/linkedin.md)

## License

Proprietary — Enterprise RAG Platform
