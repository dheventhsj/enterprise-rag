# Vercel Deployment

## Live URL

After deploy: `https://enterprise-rag.vercel.app` (or your assigned Vercel domain)

## Provisioned Services

- **Neon Postgres** — via `vercel install neon` (DATABASE_URL auto-injected)
- **OpenAI** — required for embeddings + chat (`OPENAI_API_KEY`)
- **Qdrant Cloud** — required for vector search (`QDRANT_URL`, `QDRANT_API_KEY`)

## Required Environment Variables

Set in Vercel dashboard or CLI:

```bash
OPENAI_API_KEY=sk-...
QDRANT_URL=https://xxxx.cloud.qdrant.io
QDRANT_API_KEY=...
EMBEDDING_PROVIDER=openai
EMBEDDING_DIMENSION=1536
LLM_PROVIDER=openai
APP_ENV=production
SECRET_KEY=<32+ char secret>
```

## Deploy

```bash
vercel link
vercel install neon --name enterprise-rag-db --plan free_v3 -e production -e preview
vercel deploy --prod
```

## Verify

```bash
curl https://YOUR-DOMAIN/health
curl https://YOUR-DOMAIN/api/v1/docs
```

## Notes

- Vercel serverless uses OpenAI embeddings (no local ML models)
- Document ingestion runs synchronously on upload (no background workers)
- Uploads stored in `/tmp` (ephemeral; vectors persist in Qdrant after ingestion)
