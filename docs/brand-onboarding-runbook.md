# Brand Onboarding Runbook

How to onboard a new brand onto the platform. Brand #1 (`auxo`, AI-based fitness app) used these steps.

---

## Prerequisites

- Platform is live at `https://gentle-peace-production-4b05.up.railway.app`
- You have a brand name, slug (URL-safe, lowercase, hyphens), and the agent endpoint URLs

---

## Step 1 — Create the brand

Choose a URL-safe slug (lowercase, hyphens) that is unique across the platform.

```bash
# Generate an API key — store this securely, it is hashed on write and cannot be recovered
API_KEY="bop-<your-slug>-$(openssl rand -hex 12)"

curl -X POST https://gentle-peace-production-4b05.up.railway.app/brands \
  -H "Content-Type: application/json" \
  -d "{
    \"slug\": \"your-slug\",
    \"name\": \"Your Brand Name\",
    \"status\": \"active\",
    \"api_key\": \"$API_KEY\",
    \"config\": {
      \"description\": \"One-line brand description\",
      \"vertical\": \"e.g. ai-fitness / ecomm / media\",
      \"agent_model\": \"claude-sonnet-4-6\",
      \"timezone\": \"America/New_York\"
    }
  }"
```

Example (brand #1): `slug=auxo`, `name=Auxo`, `vertical=ai-fitness`.

Verify:

```bash
curl https://gentle-peace-production-4b05.up.railway.app/brands/your-slug | jq '.'
```

---

## Step 2 — Register agents

Each brand needs at least three agents: `content`, `ops`, `support`.  
`agent_ref` is the HTTPS URL the platform will POST tasks to.

```bash
BRAND_API_KEY="bop-<brand>-<your-key>"

for TYPE in content ops support; do
  curl -X POST https://gentle-peace-production-4b05.up.railway.app/brands/your-slug/agents \
    -H "Content-Type: application/json" \
    -H "X-Brand-API-Key: $BRAND_API_KEY" \
    -d "{
      \"task_type\": \"$TYPE\",
      \"agent_ref\": \"https://your-agent-endpoint.example.com/tasks\",
      \"priority\": 10
    }"
done
```

For testing without a live agent, use the built-in echo stub:

```bash
agent_ref: "https://gentle-peace-production-4b05.up.railway.app/echo"
```

List registered agents:

```bash
curl https://gentle-peace-production-4b05.up.railway.app/brands/your-slug/agents \
  -H "X-Brand-API-Key: $BRAND_API_KEY" | jq '.'
```

---

## Step 3 — Test task routing

```bash
# Content task
curl -X POST https://gentle-peace-production-4b05.up.railway.app/brands/your-slug/tasks \
  -H "Content-Type: application/json" \
  -H "X-Brand-API-Key: $BRAND_API_KEY" \
  -d '{"task_type": "content", "payload": {"topic": "launch post", "format": "tweet"}}'

# Ops task
curl -X POST https://gentle-peace-production-4b05.up.railway.app/brands/your-slug/tasks \
  -H "Content-Type: application/json" \
  -H "X-Brand-API-Key: $BRAND_API_KEY" \
  -d '{"task_type": "ops", "payload": {"action": "check_status"}}'

# Support task
curl -X POST https://gentle-peace-production-4b05.up.railway.app/brands/your-slug/tasks \
  -H "Content-Type: application/json" \
  -H "X-Brand-API-Key: $BRAND_API_KEY" \
  -d '{"task_type": "support", "payload": {"query": "how do I reset my password?"}}'
```

Expected response from echo stub:
```json
{"status": "ok", "received": {"brand_id": "...", "task_type": "content", "payload": {...}}}
```

---

## Step 4 — Validate observability

```bash
# Metrics (Prometheus format)
curl https://gentle-peace-production-4b05.up.railway.app/metrics

# Health
curl https://gentle-peace-production-4b05.up.railway.app/health
```

---

## Step 5 — Update brand config

Use `PATCH` (no auth required) to update name, status, or config:

```bash
curl -X PATCH https://gentle-peace-production-4b05.up.railway.app/brands/your-slug \
  -H "Content-Type: application/json" \
  -d '{"config": {"vertical": "fitness"}}'
```

Note: `PATCH` does **not** support changing `slug`. To rename a brand, create the new one and delete the old one (see below).

---

## Step 6 — Declare project refs and tech stack

Brands should declare their codebase/project references and a machine-readable tech stack so agents can plan work without the board having to dictate the stack each time. Both live inside `brand.config` as `project_refs` (a list) and `tech_stack` (an object). Read them back with:

```bash
curl https://gentle-peace-production-4b05.up.railway.app/brands/your-slug/tech-stack | jq '.'
```

Response shape:

```json
{
  "project_refs": [
    { "type": "claude_code", "id": "<project-id>", "label": "<label>", "repo_url": "<url-or-null>" }
  ],
  "tech_stack": {
    "languages": ["..."],
    "frameworks": ["..."],
    "data": ["..."],
    "distribution": ["..."],
    "notes": "..."
  },
  "updated_at": "2026-04-20T..."
}
```

`project_refs` is **typed but opaque** — the platform does not introspect or validate the referenced project today. The first `type` we support is `claude_code`; more can be added later without a schema change.

Set both via a normal `PATCH /brands/:slug`:

```bash
curl -X PATCH https://gentle-peace-production-4b05.up.railway.app/brands/your-slug \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "project_refs": [
        {
          "type": "claude_code",
          "id": "my-project-id",
          "label": "My Project",
          "repo_url": "https://github.com/you/your-repo"
        }
      ],
      "tech_stack": {
        "languages": ["typescript"],
        "frameworks": ["next.js"],
        "data": ["postgres"],
        "distribution": ["vercel"],
        "notes": "Describe anything that does not fit the taxonomy above."
      }
    }
  }'
```

Notes:

- `PATCH` replaces `config` wholesale. Preserve existing keys (e.g. `vertical`, `agent_model`, `timezone`) by fetching the brand first and merging before PATCHing. The helper script in `scripts/seed-auxo-tech-stack.sh` shows the merge pattern.
- If a Claude Code project is not yet registered for the brand, attach a **placeholder ref** and leave a TODO to fill in the real project id + repo url later:

  ```json
  {
    "type": "claude_code",
    "id": "<brand>-<surface>-placeholder",
    "label": "<brand> <surface>",
    "repo_url": null
  }
  ```

- Keys under `tech_stack` are free-form today — keep them narrow (`languages`, `frameworks`, `data`, `distribution`, `notes`) so agents can rely on the shape. No validation on the server yet.

Done when `GET /brands/your-slug/tech-stack` returns a non-empty stack and at least one project ref.

### Seeded for Auxo

Auxo's iOS codebase is not yet registered as its own Paperclip project, so it runs with a placeholder ref. Run the helper post-deploy to apply the seed:

```bash
./scripts/seed-auxo-tech-stack.sh
```

Replace the `auxo-ios-placeholder` id and fill `repo_url` once Auxo's codebase is registered.

---

## Step 7 — Delete / rename a brand

Deleting a brand also removes its registered agents. No auth is required for delete.

```bash
curl -X DELETE https://gentle-peace-production-4b05.up.railway.app/brands/old-slug
# → HTTP 204
```

To rename: create the new brand with the desired slug (Step 1), register its agents (Step 2), smoke-test (Step 3), then delete the old one.

---

## Agent endpoint contract

The platform dispatches tasks via `POST <agent_ref>` with:

```json
{
  "brand_id": "<uuid>",
  "task_type": "content|ops|support",
  "payload": {}
}
```

The agent must return HTTP 200 with any JSON body. Non-200 → platform returns 502. Connection failure → 503.

---

## Definition of done for each brand

- [ ] Brand created (`status: active`)
- [ ] Three agents registered (content, ops, support) pointing to real endpoints
- [ ] All three task types return 200
- [ ] Health and metrics endpoints clean
- [ ] API key stored in brand's secrets manager

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Slug already exists` | Brand slug taken | Choose a different slug |
| `Missing X-Brand-API-Key` | No auth header | Pass `-H "X-Brand-API-Key: <key>"` |
| `Invalid API key` | Wrong key | Use the key set at creation time |
| `Agent unreachable` | `agent_ref` URL not responding | Check agent endpoint is live |
| `Agent returned an error` | Agent returned non-2xx | Check agent logs |
| `No agent registered for task_type` | Agent not wired up | Run Step 2 for that task type |
