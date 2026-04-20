# Brand Orchestration Platform

A minimal, opinionated API for running multiple brands as first-class entities — each with its own agents, routing, and ops surface.

## Quick start (local)

```bash
pip install -r requirements.txt
DATABASE_URL=sqlite:///./platform.db alembic upgrade head
uvicorn platform_api.main:app --reload
```

Open `http://localhost:8000/docs` for the interactive API spec.

## Adding a brand

```bash
# Create brand
curl -X POST http://localhost:8000/brands \
  -H "Content-Type: application/json" \
  -d '{"slug": "acme-blog", "name": "Acme Blog", "api_key": "my-secret-key"}'

# Register an agent for a task type
curl -X POST http://localhost:8000/brands/acme-blog/agents \
  -H "Content-Type: application/json" \
  -H "X-Brand-API-Key: my-secret-key" \
  -d '{"task_type": "content.draft", "agent_ref": "https://my-agent.example.com/run"}'

# Dispatch a task
curl -X POST http://localhost:8000/brands/acme-blog/tasks \
  -H "Content-Type: application/json" \
  -H "X-Brand-API-Key: my-secret-key" \
  -d '{"task_type": "content.draft", "payload": {"topic": "AI trends"}}'
```

## Adding a second brand

Repeat the steps above with a different `slug`. Every brand is isolated — its own API key, its own agent registry, no shared state.

## Deploy (Railway)

1. Push to `main` — GitHub Actions builds the Docker image and pushes to `ghcr.io`.
2. Connect the Railway project to this repo and set `DATABASE_URL` in Railway environment variables.
3. Railway runs `alembic upgrade head && uvicorn …` on each deploy.
4. Health check: `GET /health` → `{"status": "ok", "build": "<git-sha>"}`.

## Key endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | none | Health check |
| GET | /metrics | none | Prometheus metrics |
| POST | /brands | none | Create brand |
| GET | /brands/:slug | none | Get brand |
| PATCH | /brands/:slug | none | Update brand |
| DELETE | /brands/:slug | none | Delete brand |
| POST | /brands/:slug/agents | API key | Register agent |
| DELETE | /brands/:slug/agents/:id | API key | Unregister agent |
| POST | /brands/:slug/tasks | API key | Dispatch task |

## Architecture

See [RFC (WIL-4)](https://github.com/gymdawg92/brand-orchestration-platform) for the full design rationale.

- **FastAPI + SQLModel**: async API with unified Pydantic/SQLAlchemy models
- **Alembic**: schema migrations (upgrade + rollback tested in CI)
- **Postgres**: single DB, per-brand rows — no cross-brand joins
- **Railway**: one-command deploy, managed Postgres, log drain
- **Prometheus**: request count + latency exported at `/metrics`
