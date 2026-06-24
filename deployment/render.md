# Render Deployment

## Services

1. **Web Service** — FastAPI API (`docker/Dockerfile`)
2. **PostgreSQL** — Render managed Postgres
3. **Redis** — Render Key Value (or external Redis)
4. **Qdrant** — Qdrant Cloud or self-hosted on a Render private service

## Environment Variables

```bash
APP_ENV=production
DEBUG=false
SECRET_KEY=<generate-64-char-secret>
DATABASE_URL=<render-postgres-internal-url>
REDIS_URL=<redis-url>
QDRANT_HOST=<qdrant-host>
QDRANT_PORT=6333
QDRANT_API_KEY=<optional>
OPENAI_API_KEY=<your-key>
LLM_PROVIDER=openai
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
UPLOAD_DIR=/var/data/uploads
CORS_ORIGINS=["https://your-frontend.com"]
```

## Steps

1. Push repository to GitHub
2. Create Render Web Service → connect repo → set Dockerfile path: `docker/Dockerfile`
3. Add managed PostgreSQL and link `DATABASE_URL`
4. Add Redis instance and set `REDIS_URL`
5. Provision Qdrant Cloud cluster; set `QDRANT_HOST`, `QDRANT_API_KEY`
6. Add persistent disk mount at `/var/data/uploads` for document storage
7. Run migrations: `alembic upgrade head` (one-off job or pre-deploy command)
8. Deploy and verify `GET /health` and `GET /metrics`

## Health Check

- Path: `/health`
- Expected: `200 OK`

## Scaling

- Start with 1 instance (embedding model loads in-process)
- Scale horizontally once embeddings move to a dedicated worker service
