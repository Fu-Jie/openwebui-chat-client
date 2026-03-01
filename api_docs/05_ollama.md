# Ollama API Reference

> **Base path prefix:** `/ollama`
>
> All routes proxy requests to one or more configured Ollama backends.
> Routes that accept an optional `{url_idx}` path parameter target a specific Ollama node; omitting `url_idx` lets the server pick a node automatically (load-balanced or lowest-version, depending on the endpoint).

---

### GET /ollama/

**Summary:** Returns a liveness status object confirming the Ollama router is reachable.

**Auth:** Public

**Request**

_No parameters._

**Response `200`**

```json
{ "status": true }
```

| Field | Type | Description |
|-------|------|-------------|
| status | boolean | Always `true` when the router is alive |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 503 | Ollama API is disabled |

---

### POST /ollama/verify

**Summary:** Verify that a given Ollama base URL is reachable and returns a valid version response.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | url | string | Yes | Ollama base URL to test (e.g. `http://localhost:11434`) |
| Body | key | string | No | Bearer token for the remote Ollama instance |

**Response `200`**

```json
{ "version": "0.3.6" }
```

| Field | Type | Description |
|-------|------|-------------|
| version | string | Ollama version string returned by the remote node |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 500 | Could not connect to the target URL |

---

### GET /ollama/config

**Summary:** Retrieve the current Ollama connection configuration.

**Auth:** Admin only

**Request**

_No parameters._

**Response `200`**

```json
{
  "ENABLE_OLLAMA_API": true,
  "OLLAMA_BASE_URLS": ["http://localhost:11434"],
  "OLLAMA_API_CONFIGS": {
    "0": { "enable": true, "key": null, "prefix_id": null, "tags": [], "model_ids": [] }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| ENABLE_OLLAMA_API | boolean | Whether the Ollama API integration is active |
| OLLAMA_BASE_URLS | string[] | Ordered list of Ollama backend URLs |
| OLLAMA_API_CONFIGS | object | Per-index API configuration map (key = string index) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /ollama/config/update

**Summary:** Persist updated Ollama connection settings; API configs for removed URLs are automatically pruned.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | ENABLE_OLLAMA_API | boolean | No | Enable or disable Ollama integration |
| Body | OLLAMA_BASE_URLS | string[] | Yes | Full list of Ollama backend base URLs |
| Body | OLLAMA_API_CONFIGS | object | Yes | Per-index config map (see GET /ollama/config for shape) |

**Response `200`**

Same shape as `GET /ollama/config`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /ollama/api/tags
### GET /ollama/api/tags/{url_idx}

**Summary:** List all models available from Ollama backends; filtered by access-control for regular users.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target a specific Ollama node (0-based); omit to aggregate all nodes |

**Response `200`**

```json
{
  "models": [
    {
      "model": "llama3:latest",
      "name": "llama3:latest",
      "modified_at": "2024-01-01T00:00:00Z",
      "size": 4661211328,
      "digest": "sha256:...",
      "details": { "format": "gguf", "family": "llama", "parameter_size": "8B", "quantization_level": "Q4_0" },
      "urls": [0],
      "expires_at": 1700000000
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| models | object[] | List of model objects |
| models[].model | string | Model identifier (may be prefixed) |
| models[].urls | integer[] | Node indices that host this model |
| models[].expires_at | integer | Unix timestamp when the model will be evicted from memory (if loaded) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 503 | Ollama API is disabled |

---

### GET /ollama/api/ps

**Summary:** List models currently loaded into Ollama GPU/CPU memory across all nodes.

**Auth:** Admin only

**Request**

_No parameters._

**Response `200`**

```json
{
  "models": [
    {
      "model": "llama3:latest",
      "size": 4661211328,
      "digest": "sha256:...",
      "expires_at": "2024-06-01T12:00:00Z",
      "urls": [0]
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| models | object[] | Currently loaded model entries aggregated across nodes |
| models[].model | string | Model identifier |
| models[].expires_at | string | ISO-8601 expiry time in Ollama memory |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /ollama/api/version
### GET /ollama/api/version/{url_idx}

**Summary:** Return Ollama version; returns the lowest version across all nodes when no index is given.

**Auth:** Public

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Query a specific node |

**Response `200`**

```json
{ "version": "0.3.6" }
```

| Field | Type | Description |
|-------|------|-------------|
| version | string \| false | Ollama version string, or `false` when API is disabled |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 500 | No Ollama nodes reachable |

---

### POST /ollama/api/unload

**Summary:** Unload a named model from Ollama memory on all nodes that host it.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Name of the model to unload |

**Response `200`**

```json
{ "status": true }
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Model name missing or model not found |
| 401 | Not authenticated / not admin |
| 500 | Failed to unload on one or more nodes |

---

### POST /ollama/api/pull
### POST /ollama/api/pull/{url_idx}

**Summary:** Pull (download) a model from Ollama Hub onto the specified node (defaults to node 0).

**Auth:** Admin only

**Streaming:** Yes — Ollama streams NDJSON progress events during the pull.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node index (default: 0) |
| Body | model | string | Yes | Model name to pull (e.g. `llama3:latest`) |
| Body | insecure | boolean | No | Allow insecure registry connections (forced `true` server-side) |

**Response `200` (streaming NDJSON)**

Each line is a JSON object:
```json
{ "status": "pulling manifest" }
{ "status": "pulling weights", "digest": "sha256:...", "total": 4661211328, "completed": 1000000 }
{ "status": "success" }
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 503 | Ollama API is disabled |

---

### DELETE /ollama/api/push
### DELETE /ollama/api/push/{url_idx}

**Summary:** Push a local model to the Ollama Hub registry.

**Auth:** Admin only

**Streaming:** Yes — Ollama streams NDJSON progress events during the push.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Source node index (auto-resolved from model name if omitted) |
| Body | model | string | Yes | Model name to push |
| Body | insecure | boolean | No | Allow insecure registry |
| Body | stream | boolean | No | Whether to stream the response |

**Response `200` (streaming NDJSON)**

Same progress stream format as `/api/pull`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Model not found on any node |
| 401 | Not authenticated / not admin |
| 503 | Ollama API is disabled |

---

### POST /ollama/api/create
### POST /ollama/api/create/{url_idx}

**Summary:** Create a new model in Ollama (Modelfile-based) on the specified node.

**Auth:** Admin only

**Streaming:** Yes — Ollama streams NDJSON progress events during creation.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node index (default: 0) |
| Body | model | string | No | Name for the new model |
| Body | stream | boolean | No | Whether to stream the response |
| Body | path | string | No | Path to Modelfile on the Ollama server |
| Body | * | any | No | Additional fields passed through to Ollama's `/api/create` |

**Response `200` (streaming NDJSON)**

```json
{ "status": "reading model metadata" }
{ "status": "success" }
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 503 | Ollama API is disabled |

---

### POST /ollama/api/copy
### POST /ollama/api/copy/{url_idx}

**Summary:** Copy (duplicate) an existing model to a new name on the same Ollama node.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node (auto-resolved from source model if omitted) |
| Body | source | string | Yes | Name of the source model |
| Body | destination | string | Yes | Name for the copy |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Source model not found |
| 401 | Not authenticated / not admin |
| 503 | Ollama API is disabled |

---

### DELETE /ollama/api/delete
### DELETE /ollama/api/delete/{url_idx}

**Summary:** Delete a model from the specified Ollama node.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node (auto-resolved from model name if omitted) |
| Body | model | string | Yes | Name of the model to delete |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Model not found |
| 401 | Not authenticated / not admin |
| 503 | Ollama API is disabled |

---

### POST /ollama/api/show

**Summary:** Retrieve detailed metadata (Modelfile, parameters, template, system prompt) for a model.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model name |

**Response `200`**

```json
{
  "modelfile": "FROM llama3\n...",
  "parameters": "stop \"<|eot_id|>\"",
  "template": "...",
  "details": { "format": "gguf", "family": "llama", "parameter_size": "8B", "quantization_level": "Q4_0" }
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Model not found |
| 401 | Not authenticated |
| 503 | Ollama API is disabled |

---

### POST /ollama/api/embed
### POST /ollama/api/embed/{url_idx}

**Summary:** Generate batch embeddings for one or more input strings (Ollama `/api/embed`).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node |
| Body | model | string | Yes | Embedding model name |
| Body | input | string \| string[] | Yes | Text or list of texts to embed |
| Body | truncate | boolean | No | Whether to truncate input |
| Body | options | object | No | Additional Ollama model options |
| Body | keep_alive | integer \| string | No | Duration to keep model in memory |

**Response `200`**

```json
{
  "model": "nomic-embed-text",
  "embeddings": [[0.1, 0.2, ...]],
  "total_duration": 14143917,
  "load_duration": 1019109,
  "prompt_eval_count": 8
}
```

| Field | Type | Description |
|-------|------|-------------|
| model | string | Model used |
| embeddings | number[][] | Embedding vectors (one per input) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Model not found |
| 401 | Not authenticated |
| 503 | Ollama API is disabled |

---

### POST /ollama/api/embeddings
### POST /ollama/api/embeddings/{url_idx}

**Summary:** Generate a single embedding for a prompt (legacy Ollama `/api/embeddings` format).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node |
| Body | model | string | Yes | Embedding model name |
| Body | prompt | string | Yes | Text to embed |
| Body | options | object | No | Additional Ollama model options |
| Body | keep_alive | integer \| string | No | Duration to keep model in memory |

**Response `200`**

```json
{
  "model": "nomic-embed-text",
  "embedding": [0.1, 0.2, 0.3]
}
```

| Field | Type | Description |
|-------|------|-------------|
| model | string | Model used |
| embedding | number[] | Single embedding vector |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Model not found |
| 401 | Not authenticated |
| 503 | Ollama API is disabled |

---

### POST /ollama/api/generate
### POST /ollama/api/generate/{url_idx}

**Summary:** Generate a raw text completion from a prompt using Ollama's native API.

**Auth:** Verified user

**Streaming:** Yes — Supports SSE streaming via `"stream": true` (default). Each event is a JSON object on its own line; the final object has `"done": true`.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node |
| Body | model | string | Yes | Model name |
| Body | prompt | string | Yes | The prompt to complete |
| Body | suffix | string | No | Text to append after the completion |
| Body | images | string[] | No | Base64-encoded images for multimodal models |
| Body | format | string \| object | No | Response format (`"json"` or JSON schema) |
| Body | options | object | No | Ollama model parameters (temperature, top_p, etc.) |
| Body | system | string | No | System message override |
| Body | template | string | No | Prompt template override |
| Body | context | integer[] | No | Context from a prior response |
| Body | stream | boolean | No | Stream incremental tokens (default: `true`) |
| Body | raw | boolean | No | Bypass prompt template processing |
| Body | keep_alive | integer \| string | No | How long to keep the model loaded |

**Response `200` (non-streaming)**

```json
{
  "model": "llama3",
  "created_at": "2024-01-01T00:00:00.000Z",
  "response": "The capital of France is Paris.",
  "done": true,
  "context": [1, 2, 3],
  "total_duration": 5589157167,
  "load_duration": 3013701500,
  "prompt_eval_count": 46,
  "eval_count": 113,
  "eval_duration": 2435010000
}
```

**Response `200` (streaming — each NDJSON line)**

```json
{ "model": "llama3", "created_at": "...", "response": "The", "done": false }
{ "model": "llama3", "created_at": "...", "response": "", "done": true, "total_duration": 5589157167 }
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Model not found |
| 401 | Not authenticated |
| 503 | Ollama API is disabled |

---

### POST /ollama/api/chat
### POST /ollama/api/chat/{url_idx}

**Summary:** Generate a chat response using Ollama's native chat API; applies model params and system prompts from model configuration.

**Auth:** Verified user

**Streaming:** Yes — Supports SSE streaming via `"stream": true` (default). Each event is a JSON object; final object has `"done": true`.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node |
| Body | model | string | Yes | Model name |
| Body | messages | object[] | Yes | Conversation history (`role`, `content`, optional `images`, `tool_calls`) |
| Body | format | string \| object | No | Response format (`"json"` or JSON schema) |
| Body | options | object | No | Ollama model parameters |
| Body | template | string | No | Prompt template override |
| Body | stream | boolean | No | Stream incremental tokens (default: `true`) |
| Body | keep_alive | integer \| string | No | How long to keep model in memory |
| Body | tools | object[] | No | Tool definitions for function-calling |
| Body | metadata | object | No | OpenWebUI metadata (chat_id, etc.) — stripped before forwarding |

**Response `200` (non-streaming)**

```json
{
  "model": "llama3",
  "created_at": "2024-01-01T00:00:00.000Z",
  "message": { "role": "assistant", "content": "Hello, how can I help?" },
  "done": true,
  "total_duration": 5589157167,
  "eval_count": 42
}
```

**Response `200` (streaming — each NDJSON line)**

```json
{ "model": "llama3", "created_at": "...", "message": { "role": "assistant", "content": "Hello" }, "done": false }
{ "model": "llama3", "created_at": "...", "message": { "role": "assistant", "content": "" }, "done": true }
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid request body |
| 401 | Not authenticated |
| 403 | User does not have access to this model |
| 503 | Ollama API is disabled |

---

### POST /ollama/v1/completions
### POST /ollama/v1/completions/{url_idx}

**Summary:** OpenAI-compatible text completion endpoint proxied through Ollama's `/v1/completions`.

**Auth:** Verified user

**Streaming:** Yes — pass `"stream": true` in the request body; responses follow the OpenAI SSE format (`data: {...}\n\n`).

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node |
| Body | model | string | Yes | Model name |
| Body | prompt | string | Yes | Prompt text |
| Body | stream | boolean | No | Stream tokens (default: `false`) |
| Body | * | any | No | Additional OpenAI completion parameters passed through |

**Response `200`**

Standard OpenAI `text_completion` object:
```json
{
  "id": "cmpl-...",
  "object": "text_completion",
  "created": 1700000000,
  "model": "llama3",
  "choices": [{ "text": "Hello!", "index": 0, "finish_reason": "stop" }]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid payload |
| 401 | Not authenticated |
| 403 | Access denied to model |

---

### POST /ollama/v1/chat/completions
### POST /ollama/v1/chat/completions/{url_idx}

**Summary:** OpenAI-compatible chat completion endpoint proxied through Ollama's `/v1/chat/completions`.

**Auth:** Verified user

**Streaming:** Yes — pass `"stream": true`; responses follow the OpenAI SSE format (`data: {...}\n\n`).

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target node |
| Body | model | string | Yes | Model name |
| Body | messages | object[] | Yes | Chat messages (role + content) |
| Body | stream | boolean | No | Stream tokens (default: `false`) |
| Body | * | any | No | Additional OpenAI chat parameters passed through |

**Response `200`**

Standard OpenAI `chat.completion` object:
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "llama3",
  "choices": [{ "index": 0, "message": { "role": "assistant", "content": "Hi!" }, "finish_reason": "stop" }]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid payload |
| 401 | Not authenticated |
| 403 | Access denied to model |

---

### GET /ollama/v1/models
### GET /ollama/v1/models/{url_idx}

**Summary:** Return available Ollama models in OpenAI model-list format.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target a specific node |

**Response `200`**

```json
{
  "object": "list",
  "data": [
    { "id": "llama3:latest", "object": "model", "created": 1700000000, "owned_by": "openai" }
  ]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 500 | Connection error |

---

### POST /ollama/models/download
### POST /ollama/models/download/{url_idx}

**Summary:** Download a GGUF model file from HuggingFace or GitHub and register it in Ollama via blob upload.

**Auth:** Admin only

**Streaming:** Yes — SSE progress stream (`data: {...}\n\n`). Events report download progress and final blob info.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target Ollama node (default: 0) |
| Body | url | string | Yes | Download URL — must start with `https://huggingface.co/` or `https://github.com/` |

**Response `200` (SSE stream)**

```
data: {"progress": 12.5, "completed": 131072, "total": 1048576}

data: {"progress": 100.0, "completed": 1048576, "total": 1048576}

data: {"done": true, "blob": "sha256:abc123", "name": "model.gguf"}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | URL not from an allowed host |
| 401 | Not authenticated / not admin |

---

### POST /ollama/models/upload
### POST /ollama/models/upload/{url_idx}

**Summary:** Upload a local GGUF model file to an Ollama node via multipart form upload; streams SHA-256 computation and blob-upload progress.

**Auth:** Admin only

**Streaming:** Yes — SSE progress stream reporting upload and blob registration progress.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Target Ollama node (default: 0) |
| Body (multipart) | file | file | Yes | GGUF model file to upload |

**Response `200` (SSE stream)**

```
data: {"progress": 50.0, "total": 2097152, "completed": 1048576}

data: {"done": true, "blob": "sha256:abc123", "name": "model.gguf", "model_created": "model"}
```

| Field | Type | Description |
|-------|------|-------------|
| done | boolean | True when upload and model creation are complete |
| blob | string | SHA-256 digest of the uploaded file |
| name | string | Filename as stored |
| model_created | string | Name of the newly created Ollama model |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 500 | Blob upload or model creation failed (error object in SSE stream) |
