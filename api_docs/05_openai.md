# OpenAI-Compatible API Reference

> **Base path prefix:** `/openai`
>
> These endpoints proxy requests to one or more configured OpenAI-compatible backends (OpenAI, Azure OpenAI, Anthropic, local providers). The server selects the appropriate backend based on the model requested. Multiple connections are managed through indexed URL/key pairs.

---

### GET /openai/config

**Summary:** Retrieve the current OpenAI-compatible connection configuration including all backend URLs, API keys, and per-connection options.

**Auth:** Admin only

**Request**

_No parameters._

**Response `200`**

```json
{
  "ENABLE_OPENAI_API": true,
  "OPENAI_API_BASE_URLS": ["https://api.openai.com/v1"],
  "OPENAI_API_KEYS": ["sk-..."],
  "OPENAI_API_CONFIGS": {
    "0": {
      "enable": true,
      "prefix_id": null,
      "tags": [],
      "model_ids": [],
      "connection_type": "external",
      "azure": false,
      "api_version": null,
      "api_type": null
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| ENABLE_OPENAI_API | boolean | Whether the OpenAI API integration is active |
| OPENAI_API_BASE_URLS | string[] | Ordered list of backend base URLs |
| OPENAI_API_KEYS | string[] | API keys aligned with `OPENAI_API_BASE_URLS` |
| OPENAI_API_CONFIGS | object | Per-index configuration map (string index → config object) |
| OPENAI_API_CONFIGS[i].azure | boolean | Whether the connection is Azure OpenAI |
| OPENAI_API_CONFIGS[i].api_version | string | Azure API version (e.g. `2024-02-01`) |
| OPENAI_API_CONFIGS[i].api_type | string | `"responses"` to use the Responses API instead of Chat Completions |
| OPENAI_API_CONFIGS[i].model_ids | string[] | Restrict to these model IDs (empty = all) |
| OPENAI_API_CONFIGS[i].prefix_id | string | Prefix prepended to model IDs |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /openai/config/update

**Summary:** Persist updated OpenAI-compatible backend settings; key/URL arrays are automatically length-matched.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | ENABLE_OPENAI_API | boolean | No | Enable or disable OpenAI integration |
| Body | OPENAI_API_BASE_URLS | string[] | Yes | Full list of backend base URLs |
| Body | OPENAI_API_KEYS | string[] | Yes | API keys (matched by position to URLs; padded/trimmed automatically) |
| Body | OPENAI_API_CONFIGS | object | Yes | Per-index config map (see GET /openai/config for shape) |

**Response `200`**

Same shape as `GET /openai/config`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /openai/verify

**Summary:** Verify connectivity to a specific OpenAI-compatible backend URL; supports standard, Azure, and Anthropic providers.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | url | string | Yes | Backend base URL to test |
| Body | key | string | Yes | API key for the backend |
| Body | config | object | No | Optional per-connection config (same shape as `OPENAI_API_CONFIGS[i]`) |

**Response `200`**

Proxies the raw response from the backend's `/models` endpoint (or Azure's `openai/models` endpoint). Shape depends on provider:
```json
{
  "object": "list",
  "data": [{ "id": "gpt-4o", "object": "model", "owned_by": "openai" }]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 500 | Could not connect to backend or upstream returned an error |

---

### POST /openai/audio/speech

**Summary:** Proxy a text-to-speech synthesis request to the configured OpenAI backend; responses are cached by content hash.

**Auth:** Verified user

> **Note:** This endpoint requires that `https://api.openai.com/v1` is configured as one of the OpenAI API base URLs. Use `/api/v1/audio/speech` for engine-agnostic TTS with configurable backends.

**Request**

Raw JSON body forwarded to OpenAI's `/audio/speech`:
```json
{
  "model": "tts-1",
  "input": "Hello, world!",
  "voice": "alloy"
}
```

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | TTS model (e.g. `tts-1`, `tts-1-hd`) |
| Body | input | string | Yes | Text to synthesize |
| Body | voice | string | Yes | Voice ID (e.g. `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`) |

**Response `200`**

Audio file (MP3) as a file response. The file is cached on disk and served directly on subsequent identical requests.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | OpenAI URL not found in configured backends |
| 500 | Upstream TTS error |

---

### GET /openai/models
### GET /openai/models/{url_idx}

**Summary:** Return available models from all configured OpenAI-compatible backends merged into a single list; filtered by access-control for regular users.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | url_idx | integer | No | Query a specific backend by index; omit to aggregate all backends |

**Response `200`**

```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-4o",
      "object": "model",
      "owned_by": "openai",
      "name": "gpt-4o",
      "openai": { "id": "gpt-4o" },
      "connection_type": "external",
      "urlIdx": 0,
      "tags": []
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| data | object[] | Merged model list from all active backends |
| data[].id | string | Model identifier (may be prefixed per connection config) |
| data[].urlIdx | integer | Index of the backend that serves this model |
| data[].connection_type | string | `"external"` or `"local"` |
| data[].tags | string[] | Tags configured for this connection |

> **Note:** Models with names matching `babbage`, `dall-e`, `davinci`, `embedding`, `tts`, or `whisper` are filtered out when the backend URL is `api.openai.com`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 503 | OpenAI API is disabled |

---

### POST /openai/chat/completions

**Summary:** Route a chat completion request to the appropriate configured OpenAI-compatible backend based on the model; applies model configuration overrides (system prompt, parameters) and supports Azure OpenAI, Responses API, and reasoning model handling.

**Auth:** Verified user

**Streaming:** Yes — if the upstream returns `Content-Type: text/event-stream`, the response is forwarded as SSE. Pass `"stream": true` in the request body.

**Request**

OpenAI-compatible chat completion payload:

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID as returned by `/openai/models` |
| Body | messages | object[] | Yes | Chat history (`role` + `content`) |
| Body | stream | boolean | No | Stream tokens via SSE (default: `false`) |
| Body | temperature | number | No | Sampling temperature |
| Body | max_tokens | integer | No | Maximum tokens to generate |
| Body | tools | object[] | No | Function/tool definitions |
| Body | tool_choice | string \| object | No | Tool selection mode |
| Body | response_format | object | No | Structured output format |
| Body | metadata | object | No | OpenWebUI metadata (chat_id, message_id, etc.) — stripped before forwarding |
| Body | * | any | No | Any other OpenAI chat completion parameter is passed through |

> **Azure:** When the connection is Azure OpenAI, the payload is filtered to allowed Azure parameters and routed to the deployment endpoint. `max_tokens` is converted to `max_completion_tokens` for o-series models.
>
> **Responses API:** When `api_type: "responses"` is configured, the payload is translated to Responses API format (messages → `input`, system → `instructions`).

**Response `200` (non-streaming)**

Standard OpenAI `chat.completion` object:
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": { "role": "assistant", "content": "Hello!" },
      "finish_reason": "stop"
    }
  ],
  "usage": { "prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15 }
}
```

**Response `200` (streaming — SSE)**

```
data: {"id":"chatcmpl-...","object":"chat.completion.chunk","choices":[{"delta":{"content":"Hello"},"index":0}]}

data: [DONE]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | User does not have access to this model |
| 404 | Model not found in any configured backend |
| 500 | Upstream connection error |

---

### POST /openai/responses

**Summary:** Forward a request directly to the OpenAI Responses API endpoint, routed to the correct backend by model; supports Azure OpenAI with deployment-based routing.

**Auth:** Verified user

**Streaming:** Yes — if the upstream returns `Content-Type: text/event-stream`, the response is forwarded as SSE. Pass `"stream": true` in the request body.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID |
| Body | input | string \| object[] | No | Input messages in Responses API format |
| Body | instructions | string | No | System-level instructions |
| Body | stream | boolean | No | Stream the response |
| Body | temperature | number | No | Sampling temperature |
| Body | max_output_tokens | integer | No | Maximum output tokens |
| Body | top_p | number | No | Top-p sampling |
| Body | tools | object[] | No | Tool definitions |
| Body | tool_choice | string \| object | No | Tool selection mode |
| Body | text | object | No | Text output configuration |
| Body | truncation | string | No | Context truncation strategy |
| Body | store | boolean | No | Whether to store the response |
| Body | reasoning | object | No | Reasoning configuration |
| Body | previous_response_id | string | No | ID of a prior response for multi-turn continuity |
| Body | metadata | object | No | Request metadata |
| Body | * | any | No | Additional parameters passed through |

**Response `200` (non-streaming)**

Raw Responses API response from the upstream provider, with an added `"done": true` field.

**Response `200` (streaming — SSE)**

SSE stream forwarded directly from the upstream provider.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 500 | Upstream connection error |
