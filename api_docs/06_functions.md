# Functions API

Base path: `/api/v1/functions`

Functions are admin-managed Python plugins that extend the Open WebUI pipeline. They are compiled and loaded server-side. There are three types:

- **`filter`** – Intercept and transform request/response messages (inlet/outlet hooks). Filters with a `toggle` attribute can be enabled/disabled per-chat.
- **`action`** – Add custom action buttons to chat messages.
- **`pipe`** – Register a custom model endpoint that behaves like an LLM.

> ⚠️ **Security note:** Function content is executed as Python code server-side. Only administrators should be able to create or update functions.

---

## Schema

### FunctionMeta

```json
{
  "description": "Filters profanity from messages",
  "manifest": {
    "title": "Profanity Filter",
    "author": "admin@example.com",
    "version": "1.0.0",
    "license": "MIT",
    "requirements": ""
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| description | string \| null | Human-readable description |
| manifest | object | Frontmatter extracted from the `# ---` YAML block in source |

### FunctionModel

```json
{
  "id": "profanity_filter",
  "user_id": "user-uuid",
  "name": "Profanity Filter",
  "type": "filter",
  "content": "class Filter:\n    ...",
  "meta": {
    "description": "Filters profanity",
    "manifest": {}
  },
  "is_active": true,
  "is_global": false,
  "updated_at": 1700000000,
  "created_at": 1700000000
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier (alphanumeric + underscores, lowercase) |
| user_id | string | Creating admin's user ID |
| name | string | Display name |
| type | `"filter"` \| `"action"` \| `"pipe"` | Function type, auto-detected from source |
| content | string | Python source code |
| meta | FunctionMeta | Metadata |
| is_active | boolean | Whether the function is currently enabled |
| is_global | boolean | Whether the function is applied globally (not just to specific models) |
| updated_at | integer | Last updated Unix timestamp |
| created_at | integer | Created Unix timestamp |

### FunctionWithValvesModel

Extends `FunctionModel` with:

| Field | Type | Description |
|-------|------|-------------|
| valves | object \| null | Current global valve values |

---

## Endpoints

### GET /api/v1/functions/

**Summary:** List all functions (summary view without `content`).

**Auth:** Verified user

**Response `200`**

```json
[
  {
    "id": "profanity_filter",
    "user_id": "user-uuid",
    "type": "filter",
    "name": "Profanity Filter",
    "meta": { "description": "...", "manifest": {} },
    "is_active": true,
    "is_global": false,
    "updated_at": 1700000000,
    "created_at": 1700000000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/functions/list

**Summary:** List all functions with creator user info (admin only).

**Auth:** Admin only

**Response `200`**

```json
[
  {
    "id": "profanity_filter",
    "user_id": "user-uuid",
    "type": "filter",
    "name": "Profanity Filter",
    "meta": { "description": "...", "manifest": {} },
    "is_active": true,
    "is_global": false,
    "updated_at": 1700000000,
    "created_at": 1700000000,
    "user": {
      "id": "user-uuid",
      "name": "Admin",
      "email": "admin@example.com",
      "role": "admin"
    }
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or not admin |

---

### GET /api/v1/functions/export

**Summary:** Export all functions as full model objects, optionally including valve values.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| include_valves | boolean | No | If `true`, includes current valve values (default: `false`) |

**Response `200`**

Array of `FunctionModel` (or `FunctionWithValvesModel` if `include_valves=true`), including the `content` field.

```json
[
  {
    "id": "profanity_filter",
    "user_id": "user-uuid",
    "name": "Profanity Filter",
    "type": "filter",
    "content": "class Filter:\n    async def inlet(self, body, user): ...",
    "meta": { "description": "...", "manifest": {} },
    "is_active": true,
    "is_global": false,
    "updated_at": 1700000000,
    "created_at": 1700000000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or not admin |

---

### POST /api/v1/functions/load/url

**Summary:** Fetch Python function source from a URL or GitHub repository URL (admin only).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | url | string (HttpUrl) | Yes | URL to a `.py` file or a GitHub blob/tree URL |

**Response `200`**

```json
{
  "name": "profanity_filter",
  "content": "class Filter:\n    ..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| name | string | Inferred function name from the URL path |
| content | string | Raw Python source fetched from the URL |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid URL or empty content |
| 401 | Not admin |
| 500 | Error fetching from URL |

---

### POST /api/v1/functions/sync

**Summary:** Bulk sync (upsert + delete) the entire set of functions for the system.

**Auth:** Admin only

> **Note:** This replaces the full function set. Functions not present in the request body are **deleted**.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | functions | FunctionWithValvesModel[] | Yes | Complete list of functions to sync |

Each item in `functions` follows the `FunctionWithValvesModel` schema.

**Response `200`**

Array of `FunctionWithValvesModel` representing the final state after sync.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Compilation or valve validation error |
| 401 | Not admin |

---

### POST /api/v1/functions/create

**Summary:** Create a new function by submitting its Python source code.

**Auth:** Admin only

> ⚠️ The function source is compiled and loaded into the runtime. The `type` field (`filter`, `action`, or `pipe`) is automatically detected from the class name in the source code.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | id | string | Yes | Unique identifier (alphanumeric + underscores, lowercase) |
| Body | name | string | Yes | Display name |
| Body | content | string | Yes | Python source code |
| Body | meta | FunctionMeta | Yes | Metadata |

**Response `200`**

```json
{
  "id": "profanity_filter",
  "user_id": "user-uuid",
  "type": "filter",
  "name": "Profanity Filter",
  "meta": { "description": "...", "manifest": {} },
  "is_active": false,
  "is_global": false,
  "updated_at": 1700000000,
  "created_at": 1700000000
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid ID, ID already taken, or compilation error |
| 401 | Not admin |

---

### GET /api/v1/functions/id/{id}

**Summary:** Retrieve a function by ID including its full source code.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Response `200`**

Full `FunctionModel` including `content` field.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin or not found |

---

### POST /api/v1/functions/id/{id}/toggle

**Summary:** Toggle a function's active state (`is_active` on/off).

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Response `200`**

Updated `FunctionModel` with new `is_active` value.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error updating function |
| 401 | Not admin or not found |

---

### POST /api/v1/functions/id/{id}/toggle/global

**Summary:** Toggle a function's global state (`is_global` on/off).

**Auth:** Admin only

> **Note:** When `is_global` is `true`, filter-type functions are applied to all chats regardless of model assignment.

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Response `200`**

Updated `FunctionModel` with new `is_global` value.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error updating function |
| 401 | Not admin or not found |

---

### POST /api/v1/functions/id/{id}/update

**Summary:** Update an existing function's source code and metadata.

**Auth:** Admin only

> ⚠️ The updated source is re-compiled and loaded server-side. The `type` field is re-detected from the class name.

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | id | string | Yes | Must match path `id` |
| Body | name | string | Yes | Display name |
| Body | content | string | Yes | Updated Python source code |
| Body | meta | FunctionMeta | Yes | Updated metadata |

**Response `200`**

Updated `FunctionModel` including `content` and auto-detected `type`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Compilation error |
| 401 | Not admin |

---

### DELETE /api/v1/functions/id/{id}/delete

**Summary:** Delete a function by ID and remove it from the runtime.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin |

---

### GET /api/v1/functions/id/{id}/valves

**Summary:** Get the current global valve settings for a function.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Response `200`**

```json
{
  "api_key": "sk-...",
  "block_words": ["spam", "scam"]
}
```

Returns `{}` if no valves are configured.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error reading valves |
| 401 | Not admin or not found |

---

### GET /api/v1/functions/id/{id}/valves/spec

**Summary:** Get the JSON Schema specification for a function's `Valves` class.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Response `200`**

```json
{
  "title": "Valves",
  "type": "object",
  "properties": {
    "api_key": {
      "title": "API Key",
      "type": "string",
      "description": "Your API key"
    },
    "block_words": {
      "title": "Block Words",
      "type": "array",
      "items": { "type": "string" },
      "default": []
    }
  }
}
```

Returns `null` if the function has no `Valves` class.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not admin or not found |

---

### POST /api/v1/functions/id/{id}/valves/update

**Summary:** Update global valve settings for a function.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | *(valve fields)* | varies | No | Key-value pairs matching the function's `Valves` schema; `null` values are ignored |

**Response `200`**

Dictionary of saved valve values.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Valve validation error |
| 401 | Not admin or not found |

---

### GET /api/v1/functions/id/{id}/valves/user

**Summary:** Get the current user's personal valve settings for a function.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Response `200`**

```json
{
  "personal_token": "my-token"
}
```

Returns `{}` if no user valves are set.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error reading valves |
| 401 | Not authenticated or not found |

---

### GET /api/v1/functions/id/{id}/valves/user/spec

**Summary:** Get the JSON Schema specification for a function's `UserValves` class.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Response `200`**

JSON Schema object (same structure as `/valves/spec`). Returns `null` if no `UserValves` class.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or not found |

---

### POST /api/v1/functions/id/{id}/valves/user/update

**Summary:** Update the current user's personal valve settings for a function.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Function ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | *(user valve fields)* | varies | No | Key-value pairs matching `UserValves` schema; `null` values are ignored |

**Response `200`**

Dictionary of saved user valve values.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Valve validation error |
| 401 | Not authenticated or not found |

---
