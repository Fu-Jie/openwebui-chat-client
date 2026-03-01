# Tasks API

Base path: `/api/v1/tasks`

The Tasks module handles background LLM-driven processing that powers automatic UI features: chat title generation, tag generation, follow-up suggestions, autocomplete, search query generation, emoji selection, image prompt creation, and mixture-of-agents (MoA) response synthesis.

Each completion endpoint selects the appropriate task model (configured via `TASK_MODEL` / `TASK_MODEL_EXTERNAL`), applies the relevant prompt template to the conversation, and proxies the result through `generate_chat_completion`.

---

## Schema

### TaskConfig

```json
{
  "TASK_MODEL": "llama3.2",
  "TASK_MODEL_EXTERNAL": "gpt-4o-mini",
  "ENABLE_TITLE_GENERATION": true,
  "TITLE_GENERATION_PROMPT_TEMPLATE": "...",
  "IMAGE_PROMPT_GENERATION_PROMPT_TEMPLATE": "...",
  "ENABLE_AUTOCOMPLETE_GENERATION": true,
  "AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH": 1000,
  "TAGS_GENERATION_PROMPT_TEMPLATE": "...",
  "FOLLOW_UP_GENERATION_PROMPT_TEMPLATE": "...",
  "ENABLE_FOLLOW_UP_GENERATION": true,
  "ENABLE_TAGS_GENERATION": true,
  "ENABLE_SEARCH_QUERY_GENERATION": true,
  "ENABLE_RETRIEVAL_QUERY_GENERATION": true,
  "QUERY_GENERATION_PROMPT_TEMPLATE": "...",
  "TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE": "...",
  "VOICE_MODE_PROMPT_TEMPLATE": "..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| TASK_MODEL | string \| null | Local model ID to use for tasks (Ollama-backed) |
| TASK_MODEL_EXTERNAL | string \| null | External model ID to use for tasks (OpenAI-compatible) |
| ENABLE_TITLE_GENERATION | boolean | Enable automatic chat title generation |
| TITLE_GENERATION_PROMPT_TEMPLATE | string | Jinja2/handlebars prompt template for title generation |
| IMAGE_PROMPT_GENERATION_PROMPT_TEMPLATE | string | Prompt template for image prompt generation |
| ENABLE_AUTOCOMPLETE_GENERATION | boolean | Enable message autocomplete suggestions |
| AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH | integer | Max character length for autocomplete input (`-1` = unlimited) |
| TAGS_GENERATION_PROMPT_TEMPLATE | string | Prompt template for tag generation |
| FOLLOW_UP_GENERATION_PROMPT_TEMPLATE | string | Prompt template for follow-up question generation |
| ENABLE_FOLLOW_UP_GENERATION | boolean | Enable automatic follow-up suggestions |
| ENABLE_TAGS_GENERATION | boolean | Enable automatic tag generation |
| ENABLE_SEARCH_QUERY_GENERATION | boolean | Enable web search query generation |
| ENABLE_RETRIEVAL_QUERY_GENERATION | boolean | Enable RAG retrieval query generation |
| QUERY_GENERATION_PROMPT_TEMPLATE | string | Prompt template for query generation (web search and retrieval) |
| TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE | string | System prompt template injected when tools are available |
| VOICE_MODE_PROMPT_TEMPLATE | string \| null | Prompt template appended in voice mode |

---

## Endpoints

### POST /api/v1/tasks/active/chats

**Summary:** Check which of the provided chat IDs currently have active (in-progress) tasks.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | chat_ids | string[] | Yes | List of chat IDs to check |

**Response `200`**

```json
{
  "active_chat_ids": ["chat-uuid-1", "chat-uuid-3"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| active_chat_ids | string[] | Subset of the input chat IDs that have active tasks |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/tasks/config

**Summary:** Retrieve the current task configuration.

**Auth:** Verified user

**Response `200`**

Full `TaskConfig` object (see schema above).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/tasks/config/update

**Summary:** Update the task configuration.

**Auth:** Admin only

**Request**

Full `TaskConfig` object body. All fields required (no partial updates).

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | TASK_MODEL | string \| null | Yes | Local task model ID |
| Body | TASK_MODEL_EXTERNAL | string \| null | Yes | External task model ID |
| Body | ENABLE_TITLE_GENERATION | boolean | Yes | Enable title generation |
| Body | TITLE_GENERATION_PROMPT_TEMPLATE | string | Yes | Title generation prompt template |
| Body | IMAGE_PROMPT_GENERATION_PROMPT_TEMPLATE | string | Yes | Image prompt generation template |
| Body | ENABLE_AUTOCOMPLETE_GENERATION | boolean | Yes | Enable autocomplete |
| Body | AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH | integer | Yes | Max autocomplete input length |
| Body | TAGS_GENERATION_PROMPT_TEMPLATE | string | Yes | Tags generation prompt template |
| Body | FOLLOW_UP_GENERATION_PROMPT_TEMPLATE | string | Yes | Follow-up generation prompt template |
| Body | ENABLE_FOLLOW_UP_GENERATION | boolean | Yes | Enable follow-up generation |
| Body | ENABLE_TAGS_GENERATION | boolean | Yes | Enable tags generation |
| Body | ENABLE_SEARCH_QUERY_GENERATION | boolean | Yes | Enable search query generation |
| Body | ENABLE_RETRIEVAL_QUERY_GENERATION | boolean | Yes | Enable retrieval query generation |
| Body | QUERY_GENERATION_PROMPT_TEMPLATE | string | Yes | Query generation template |
| Body | TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE | string | Yes | Tools function calling template |
| Body | VOICE_MODE_PROMPT_TEMPLATE | string \| null | No | Voice mode prompt template |

**Response `200`**

Updated `TaskConfig` object (same shape as GET response).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |

---

### POST /api/v1/tasks/title/completions

**Summary:** Generate a short title for a chat conversation using the task model.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID used in the chat (used to select the task model) |
| Body | messages | object[] | Yes | Conversation messages (OpenAI chat format) |
| Body | chat_id | string | No | Chat ID for metadata tracking |

**Response `200`**

If title generation is disabled, returns:
```json
{ "detail": "Title generation is disabled" }
```

Otherwise, proxied OpenAI-compatible chat completion response from the task model:

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Understanding Recursion in Python"
      },
      "finish_reason": "stop"
    }
  ]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Internal error during completion |
| 401 | Not authenticated |
| 404 | Model not found |

---

### POST /api/v1/tasks/follow_up/completions

**Summary:** Generate follow-up questions for a chat conversation.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID used in the chat |
| Body | messages | object[] | Yes | Conversation messages |
| Body | chat_id | string | No | Chat ID for metadata tracking |

**Response `200`**

If follow-up generation is disabled, returns:
```json
{ "detail": "Follow-up generation is disabled" }
```

Otherwise, proxied OpenAI-compatible chat completion with suggested follow-up questions in the `choices[0].message.content` field.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Internal error |
| 401 | Not authenticated |
| 404 | Model not found |

---

### POST /api/v1/tasks/tags/completions

**Summary:** Generate tags/keywords for a chat conversation.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID used in the chat |
| Body | messages | object[] | Yes | Conversation messages |
| Body | chat_id | string | No | Chat ID for metadata tracking |

**Response `200`**

If tags generation is disabled, returns:
```json
{ "detail": "Tags generation is disabled" }
```

Otherwise, proxied OpenAI-compatible chat completion. The assistant message content contains a comma-separated or JSON list of tags.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 404 | Model not found |
| 500 | Internal error |

---

### POST /api/v1/tasks/image_prompt/completions

**Summary:** Generate an image generation prompt from a chat conversation.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID used in the chat |
| Body | messages | object[] | Yes | Conversation messages |
| Body | chat_id | string | No | Chat ID for metadata tracking |

**Response `200`**

Proxied OpenAI-compatible chat completion. The assistant message content is a detailed image generation prompt string.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Internal error |
| 401 | Not authenticated |
| 404 | Model not found |

---

### POST /api/v1/tasks/queries/completions

**Summary:** Generate a search or retrieval query string from a chat conversation.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID used in the chat |
| Body | messages | object[] | Yes | Conversation messages |
| Body | type | string | Yes | `"web_search"` or `"retrieval"` — controls which feature-flag is checked |
| Body | chat_id | string | No | Chat ID for metadata tracking |

**Response `200`**

Proxied OpenAI-compatible chat completion. The assistant message content is the generated query string.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Query generation disabled for the requested type |
| 401 | Not authenticated |
| 404 | Model not found |

---

### POST /api/v1/tasks/auto/completions

**Summary:** Generate autocomplete suggestions for a partial user message.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID used in the chat |
| Body | prompt | string | Yes | Partial text to autocomplete |
| Body | messages | object[] | No | Prior conversation messages for context |
| Body | type | string | No | Autocomplete mode hint (e.g. `"message"`) |
| Body | chat_id | string | No | Chat ID for metadata tracking |

**Response `200`**

Proxied OpenAI-compatible chat completion containing the autocomplete suggestion.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Autocomplete disabled or prompt exceeds max length |
| 401 | Not authenticated |
| 404 | Model not found |

---

### POST /api/v1/tasks/emoji/completions

**Summary:** Generate a single emoji representing the sentiment or topic of a message.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID used in the chat |
| Body | prompt | string | Yes | Text to derive an emoji for |
| Body | chat_id | string | No | Chat ID for metadata tracking |

**Response `200`**

Proxied OpenAI-compatible chat completion. The response is limited to 4 tokens; the assistant message content is a single emoji character.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Internal error |
| 401 | Not authenticated |
| 404 | Model not found |

---

### POST /api/v1/tasks/moa/completions

**Summary:** Generate a synthesized Mixture-of-Agents (MoA) response from multiple model outputs.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | model | string | Yes | Model ID to use for synthesis |
| Body | prompt | string | Yes | Original user prompt |
| Body | responses | string[] | Yes | List of individual model responses to synthesize |
| Body | stream | boolean | No | Whether to stream the response (default: `false`) |
| Body | chat_id | string | No | Chat ID for metadata tracking |

**Response `200`**

Proxied OpenAI-compatible chat completion (or streaming response if `stream: true`). The assistant message synthesizes all provided responses into a single coherent answer.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Internal error |
| 401 | Not authenticated |
| 404 | Model not found |

---
