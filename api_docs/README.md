# OpenWebUI Backend API Reference

> **Auto-generated from source code. Do not edit manually.**
>
> Generation date: 2026-03-01

---

## Table of Contents

- [Route Index (all 394 routes)](00_route_index.md)
- [Authentication & Users — `auths`](02_auths.md)
- [Users — `users`](02_users.md)
- [Groups — `groups`](02_groups.md)
- [Models — `models`](02_models.md)
- [Chats — `chats`](03_chats.md)
- [Channels — `channels`](03_channels.md)
- [Memories — `memories`](03_memories.md)
- [Notes — `notes`](03_notes.md)
- [Files — `files`](04_files.md)
- [Folders — `folders`](04_folders.md)
- [Knowledge — `knowledge`](04_knowledge.md)
- [Retrieval — `retrieval`](04_retrieval.md)
- [Ollama Proxy — `ollama`](05_ollama.md)
- [OpenAI-Compatible Proxy — `openai`](05_openai.md)
- [Audio — `audio`](05_audio.md)
- [Images — `images`](05_images.md)
- [Tools — `tools`](06_tools.md)
- [Functions — `functions`](06_functions.md)
- [Pipelines — `pipelines`](06_pipelines.md)
- [Skills — `skills`](06_skills.md)
- [Tasks — `tasks`](06_tasks.md)
- [Configs — `configs`](07_configs.md)
- [Prompts — `prompts`](07_prompts.md)
- [Evaluations — `evaluations`](07_evaluations.md)
- [Analytics — `analytics`](07_analytics.md)
- [SCIM — `scim`](07_scim.md)
- [Utils — `utils`](07_utils.md)

---

## Statistics

| Metric | Count |
|--------|-------|
| Total modules | 27 |
| Total routes | 394 |
| Auth-required routes | 386 |
| Public (no auth) routes | 8 |
| Admin-scoped routes | 91 |
| Streaming endpoints | 20 |

### Routes per Module

| Module | Routes |
|--------|--------|
| `analytics` | 8 |
| `audio` | 6 |
| `auths` | 20 |
| `channels` | 28 |
| `chats` | 40 |
| `configs` | 15 |
| `evaluations` | 15 |
| `files` | 12 |
| `folders` | 7 |
| `functions` | 17 |
| `groups` | 10 |
| `images` | 6 |
| `knowledge` | 17 |
| `memories` | 7 |
| `models` | 14 |
| `notes` | 7 |
| `ollama` | 39 |
| `openai` | 8 |
| `pipelines` | 8 |
| `prompts` | 16 |
| `retrieval` | 17 |
| `scim` | 15 |
| `skills` | 9 |
| `tasks` | 11 |
| `tools` | 15 |
| `users` | 21 |
| `utils` | 6 |

---

## Quick Reference — 20 Most-Used Endpoints

| Method | Path | Module | Auth | Stream | Description |
|--------|------|--------|------|--------|-------------|
| `POST` | `/api/v1/auths/signin` | auths | ✓ |  | Sign in — get JWT token |
| `GET` | `/api/v1/auths/signout` | auths | ✓ |  | Sign out |
| `POST` | `/api/v1/auths/signup` | auths | ✓ |  | Create new account |
| `GET` | `/api/v1/auths/` | auths | ✓ |  | Get current session user |
| `POST` | `/api/v1/auths/update/profile` | auths | ✓ |  | Update profile |
| `POST` | `/api/v1/auths/update/password` | auths | ✓ |  | Change password |
| `POST` | `/api/v1/auths/api_key` | auths | ✓ |  | Generate API key |
| `GET` | `/api/v1/chats/` | chats | ✓ |  | List user chats |
| `POST` | `/api/v1/chats/new` | chats | ✓ |  | Create new chat |
| `GET` | `/api/v1/chats/{id}` | chats | ✓ |  | Get chat by ID |
| `DELETE` | `/api/v1/chats/{id}` | chats | ✓ |  | Delete chat |
| `GET` | `/api/v1/chats/{id}/messages` | — | ✓ |  | Get chat messages |
| `POST` | `/api/v1/files/` | files | ✓ |  | Upload file |
| `GET` | `/api/v1/files/` | files | ✓ |  | List uploaded files |
| `GET` | `/api/v1/files/{id}/content` | files | ✓ |  | Download file content |
| `GET` | `/api/v1/models/` | models | ✓ |  | List all models |
| `POST` | `/ollama/api/generate` | ollama | ✓ | ⚡ | Generate text (Ollama, streaming) |
| `POST` | `/ollama/api/chat` | ollama | ✓ | ⚡ | Chat completion (Ollama, streaming) |
| `POST` | `/openai/chat/completions` | openai | ✓ | ⚡ | Chat completion (OpenAI-compatible) |
| `GET` | `/api/v1/knowledge/` | knowledge | ✓ |  | List knowledge bases |

> ⚡ = supports streaming response &nbsp;|&nbsp; ✓ = JWT required &nbsp;|&nbsp; public = no auth needed

---

## Authentication Guide

### Getting a JWT Token

Send a `POST` request to `/api/v1/auths/signin`:

```bash
curl -X POST http://localhost:3000/api/v1/auths/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

A successful response returns:

```json
{
  "token": "eyJ...",
  "token_type": "Bearer",
  "expires_at": 1700000000,
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

See [02_auths.md](02_auths.md) for full details including LDAP authentication and API key generation.

### Including the Token in Requests

Add the `Authorization` header to every authenticated request:

```
Authorization: Bearer <token>
```

Example:

```bash
curl http://localhost:3000/api/v1/chats/ \
  -H "Authorization: Bearer eyJ..."
```

Alternatively, use an **API key** (generated via `POST /api/v1/auths/api_key`) instead of a JWT — it is passed the same way.

### Token Expiry

- `expires_at` in the sign-in response is a Unix epoch timestamp (integer) or `null` (never expires, depending on server config).
- On expiry the server returns **HTTP 401**. Re-authenticate to obtain a fresh token.
- Admins can configure token lifetime via `POST /api/v1/auths/admin/config`.

---

## Common Patterns

### Pagination

Many list endpoints accept `skip` and `limit` query parameters:

```
GET /api/v1/chats/?skip=0&limit=50
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of records to skip |
| `limit` | integer | varies | Max records to return (often 50 or 100) |

### Error Response Shape

All error responses follow this JSON structure:

```json
{
  "detail": "Human-readable error message"
}
```

Common HTTP status codes:

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 401 | Missing or invalid authentication |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 422 | Request body validation failed (FastAPI) |
| 500 | Internal server error |

### Streaming Responses

Endpoints marked ⚡ support **Server-Sent Events (SSE)** or **NDJSON** streaming.
Pass `"stream": true` in the JSON body (where supported) to receive incremental tokens:

```bash
curl -X POST http://localhost:3000/ollama/api/chat \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3", "messages": [...], "stream": true}'
```

The response is a series of newline-delimited JSON objects; the final object contains `"done": true`.

### Rate Limiting

Rate limiting is not enforced at the API layer by default. Upstream provider limits (Ollama, OpenAI) apply to proxy endpoints.

---

## Machine-Readable Summary

A full OpenAPI-style JSON summary of all routes is available at:

[openwebui_api.json](openwebui_api.json)

```json
{
  "meta": {
    "generated_date": "2026-03-01",
    "total_routes": 394,
    "modules": ["analytics", "audio", "..."]
  },
  "routes": [ ... ]
}
```
