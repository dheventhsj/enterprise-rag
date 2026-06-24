# AWS Deployment

## Recommended Architecture

```
Route 53 → ALB → ECS Fargate (FastAPI)
                  ├── RDS PostgreSQL
                  ├── ElastiCache Redis
                  ├── Qdrant (ECS/EKS or Qdrant Cloud)
                  └── S3 (document storage — future)
CloudWatch ← Prometheus sidecar (optional)
```

## ECS Fargate Task

- **Image**: Build from `docker/Dockerfile`, push to ECR
- **CPU/Memory**: 2 vCPU / 4 GB minimum (embedding model)
- **Port**: 8000
- **Health check**: `/health`

## Environment Variables

Set via ECS task definition or AWS Secrets Manager:

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | RDS PostgreSQL connection string |
| `REDIS_URL` | ElastiCache endpoint |
| `SECRET_KEY` | Secrets Manager |
| `OPENAI_API_KEY` | Secrets Manager |
| `QDRANT_HOST` | Qdrant Cloud or internal service discovery |

## RDS

- Engine: PostgreSQL 16
- Instance: `db.t3.medium` (dev) / `db.r6g.large` (prod)
- Run `alembic upgrade head` via ECS one-off task

## ElastiCache

- Engine: Redis 7
- Node type: `cache.t3.micro` (dev)

## Monitoring

- Prometheus metrics at `/metrics`
- Export to Amazon Managed Prometheus or CloudWatch via ADOT collector
- Grafana on Amazon Managed Grafana

## CI/CD

GitHub Actions builds and pushes to ECR on merge to `main`.
Deploy via ECS rolling update or AWS CodeDeploy blue/green.
