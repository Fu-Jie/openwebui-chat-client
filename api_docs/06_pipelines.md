# Pipelines API

Base path: `/api/v1/pipelines`

Pipelines connect Open WebUI to external pipeline servers that implement the [Pipelines](https://github.com/open-webui/pipelines) protocol. Each pipeline server is registered as an OpenAI-compatible API base URL. All endpoints in this router act as proxies — they forward requests to the target pipeline server identified by `urlIdx` (the index into the configured `OPENAI_API_BASE_URLS` array).

> **All endpoints are admin only.**

---

## Architecture

```
Open WebUI  ──proxy──▶  Pipeline Server (urlIdx=N)
                           └─ /pipelines          ← list
                           └─ /pipelines/add       ← add by URL
                           └─ /pipelines/upload    ← upload .py file
                           └─ /pipelines/delete    ← delete
                           └─ /{pipeline_id}/valves
                           └─ /{pipeline_id}/valves/spec
                           └─ /{pipeline_id}/valves/update
```

The pipeline server processes messages through filter pipelines before and after LLM calls (inlet/outlet hooks). Individual pipelines on a server may be of type `filter` or `pipeline` (model-like).

---

## Endpoints

### GET /api/v1/pipelines/list

**Summary:** List all connected pipeline servers (OpenAI-compatible endpoints with `pipelines` in their response).

**Auth:** Admin only

**Response `200`**

```json
{
  "data": [
    {
      "url": "http://localhost:9099",
      "idx": 0
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| data | object[] | List of detected pipeline server connections |
| data[].url | string | Base URL of the pipeline server |
| data[].idx | integer | Index into the `OPENAI_API_BASE_URLS` configuration array |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |

---

### POST /api/v1/pipelines/upload

**Summary:** Upload a Python pipeline file to a pipeline server.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Form | urlIdx | integer | Yes | Index of the target pipeline server |
| Form | file | file (multipart) | Yes | A `.py` Python file containing the pipeline implementation |

> Only `.py` files are accepted. The file is temporarily saved locally, uploaded to the pipeline server, then deleted.

**Response `200`**

Proxied JSON response from the pipeline server (typically confirms the uploaded pipeline).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | File is not a `.py` file |
| 401 | Not admin |
| 404 | Pipeline server not found or upload failed |

---

### POST /api/v1/pipelines/add

**Summary:** Add a pipeline to a pipeline server by providing the pipeline's source URL.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | url | string | Yes | URL pointing to the pipeline Python file to install on the server |
| Body | urlIdx | integer | Yes | Index of the target pipeline server |

**Response `200`**

Proxied JSON response from the pipeline server confirming the added pipeline.

```json
{
  "id": "my_pipeline",
  "name": "My Pipeline",
  "type": "filter"
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |
| 404 | Pipeline server not reachable or pipeline not found |

---

### DELETE /api/v1/pipelines/delete

**Summary:** Delete (uninstall) a pipeline from a pipeline server.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | id | string | Yes | ID of the pipeline to delete |
| Body | urlIdx | integer | Yes | Index of the target pipeline server |

**Response `200`**

Proxied JSON response from the pipeline server confirming deletion.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |
| 404 | Pipeline not found on server |

---

### GET /api/v1/pipelines/

**Summary:** List all pipelines installed on a specific pipeline server.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| urlIdx | integer | Yes | Index of the target pipeline server |

**Response `200`**

Proxied JSON response from the pipeline server. Typical format:

```json
{
  "data": [
    {
      "id": "my_filter",
      "name": "My Filter",
      "type": "filter",
      "pipelines": ["*"],
      "priority": 0
    },
    {
      "id": "my_pipe",
      "name": "My Pipe",
      "type": "pipeline"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| data | object[] | List of installed pipelines |
| data[].id | string | Pipeline identifier |
| data[].name | string | Display name |
| data[].type | `"filter"` \| `"pipeline"` | Type of pipeline |
| data[].pipelines | string[] | For filters: list of model IDs to apply to, or `["*"]` for all models |
| data[].priority | integer | Filter execution order (lower runs first) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |
| 404 | Pipeline server not reachable |

---

### GET /api/v1/pipelines/{pipeline_id}/valves

**Summary:** Get the current valve settings for a specific pipeline on a pipeline server.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| pipeline_id | string | ID of the pipeline |

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| urlIdx | integer | Yes | Index of the target pipeline server |

**Response `200`**

Proxied JSON from the pipeline server — a free-form dictionary of the pipeline's current valve values:

```json
{
  "openai_api_key": "sk-...",
  "rate_limit": 60
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |
| 404 | Pipeline or server not found |

---

### GET /api/v1/pipelines/{pipeline_id}/valves/spec

**Summary:** Get the JSON Schema specification for a pipeline's valve configuration.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| pipeline_id | string | ID of the pipeline |

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| urlIdx | integer | Yes | Index of the target pipeline server |

**Response `200`**

Proxied JSON Schema from the pipeline server:

```json
{
  "title": "Valves",
  "type": "object",
  "properties": {
    "openai_api_key": {
      "title": "OpenAI API Key",
      "type": "string",
      "description": "Your OpenAI API key"
    },
    "rate_limit": {
      "title": "Rate Limit",
      "type": "integer",
      "default": 60,
      "description": "Max requests per minute"
    }
  },
  "required": ["openai_api_key"]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |
| 404 | Pipeline or server not found |

---

### POST /api/v1/pipelines/{pipeline_id}/valves/update

**Summary:** Update valve settings for a pipeline on a pipeline server.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| pipeline_id | string | ID of the pipeline |

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| urlIdx | integer | Yes | Index of the target pipeline server |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | *(valve fields)* | varies | No | Key-value pairs matching the pipeline's valve schema |

**Response `200`**

Proxied JSON from the pipeline server confirming the updated valve values.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |
| 404 | Pipeline or server not found |

---
