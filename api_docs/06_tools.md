# Tools API

Base path: `/api/v1/tools`

Tools are user-created Python modules that expose callable functions to the LLM. Each tool is stored as Python source code and loaded at runtime. The functions defined in the tool class are automatically extracted as OpenAI-compatible function-call specs and made available during chat completions.

> ⚠️ **Security note:** Tool content is executed as Python code server-side. Only trusted users with the `workspace.tools` permission should be allowed to create or update tools.

---

## Schema

### ToolMeta

```json
{
  "description": "Optional description of the tool",
  "manifest": {
    "title": "My Tool",
    "author": "user@example.com",
    "version": "1.0.0",
    "license": "MIT",
    "requirements": "requests"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| description | string \| null | Human-readable description of the tool |
| manifest | object | Frontmatter extracted from the tool's Python source (`# ---` YAML block) |

### ToolSpec (OpenAI function-call spec)

```json
{
  "name": "search_web",
  "description": "Search the web for information",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query"
      }
    },
    "required": ["query"]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| name | string | Function name (matches the Python method name) |
| description | string | Description shown to the LLM |
| parameters | object | JSON Schema describing the function parameters |

### AccessGrant

```json
{
  "principal_type": "user",
  "principal_id": "user-uuid",
  "permission": "read"
}
```

| Field | Type | Description |
|-------|------|-------------|
| principal_type | `"user"` \| `"group"` | Type of principal |
| principal_id | string | User/group ID, or `"*"` for public |
| permission | `"read"` \| `"write"` | Permission level |

---

## Endpoints

### GET /api/v1/tools/

**Summary:** List all tools accessible to the current user, including local tools and connected tool servers (OpenAPI and MCP).

**Auth:** Verified user

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| *(none)* | — | — | — |

**Response `200`**

```json
[
  {
    "id": "my_tool",
    "user_id": "user-uuid",
    "name": "My Tool",
    "meta": {
      "description": "Does something useful"
    },
    "access_grants": [
      {
        "principal_type": "user",
        "principal_id": "*",
        "permission": "read"
      }
    ],
    "updated_at": 1700000000,
    "created_at": 1700000000,
    "has_user_valves": true,
    "user": null
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool identifier (alphanumeric + underscores; or `server:<id>` / `server:mcp:<id>` for remote servers) |
| user_id | string | Owner's user ID |
| name | string | Display name |
| meta | ToolMeta | Metadata including description and manifest |
| access_grants | AccessGrant[] | List of access grants |
| updated_at | integer | Last updated Unix timestamp |
| created_at | integer | Created Unix timestamp |
| has_user_valves | boolean | Whether the tool defines a `UserValves` class |
| user | object \| null | Owner user info (if available) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/tools/list

**Summary:** List tools accessible to the current user with explicit write-access flags.

**Auth:** Verified user

**Response `200`**

```json
[
  {
    "id": "my_tool",
    "user_id": "user-uuid",
    "name": "My Tool",
    "meta": { "description": "..." },
    "access_grants": [],
    "updated_at": 1700000000,
    "created_at": 1700000000,
    "write_access": true,
    "has_user_valves": false,
    "user": null
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| *(all fields from GET /)* | — | Same as list endpoint |
| write_access | boolean | Whether the current user can modify this tool |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/tools/export

**Summary:** Export all tools accessible to the current user as full model objects (including `content` and `specs`).

**Auth:** Verified user (requires `workspace.tools_export` permission for non-admins)

**Response `200`**

```json
[
  {
    "id": "my_tool",
    "user_id": "user-uuid",
    "name": "My Tool",
    "content": "class Tools:\n    def search(self, query: str) -> str:\n        ...",
    "specs": [
      {
        "name": "search",
        "description": "Search for something",
        "parameters": {
          "type": "object",
          "properties": {
            "query": { "type": "string", "description": "Search query" }
          },
          "required": ["query"]
        }
      }
    ],
    "meta": { "description": "My tool", "manifest": {} },
    "access_grants": [],
    "updated_at": 1700000000,
    "created_at": 1700000000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |
| user_id | string | Owner ID |
| name | string | Display name |
| content | string | Full Python source code |
| specs | ToolSpec[] | Auto-extracted OpenAI function-call specs |
| meta | ToolMeta | Metadata |
| access_grants | AccessGrant[] | Access grants |
| updated_at | integer | Unix timestamp |
| created_at | integer | Unix timestamp |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or unauthorized |

---

### POST /api/v1/tools/load/url

**Summary:** Fetch Python tool source from a URL or GitHub repository URL (admin only).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | url | string (HttpUrl) | Yes | URL to a `.py` file or a GitHub blob/tree URL |

**Response `200`**

```json
{
  "name": "my_tool",
  "content": "class Tools:\n    ..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| name | string | Inferred tool name from the URL path |
| content | string | Raw Python source fetched from the URL |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid URL or empty content |
| 401 | Not an admin |
| 500 | Error fetching from URL |

---

### POST /api/v1/tools/create

**Summary:** Create a new tool by submitting its Python source code.

**Auth:** Verified user (requires `workspace.tools` or `workspace.tools_import` permission for non-admins)

> ⚠️ The tool's Python source is executed server-side. The `content` field is compiled and loaded into the runtime.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | id | string | Yes | Unique identifier (alphanumeric + underscores, lowercase) |
| Body | name | string | Yes | Display name |
| Body | content | string | Yes | Python source code containing a `Tools` class |
| Body | meta | ToolMeta | Yes | Metadata (description, manifest) |
| Body | access_grants | AccessGrant[] \| null | No | Initial access grants |

**Response `200`**

```json
{
  "id": "my_tool",
  "user_id": "user-uuid",
  "name": "My Tool",
  "meta": { "description": "Does something", "manifest": {} },
  "access_grants": [],
  "updated_at": 1700000000,
  "created_at": 1700000000
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid ID format, ID already taken, or Python compilation error |
| 401 | Not authenticated or insufficient permissions |

---

### GET /api/v1/tools/id/{id}

**Summary:** Retrieve a tool by ID with write-access flag.

**Auth:** Verified user (must have read access to the tool)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Response `200`**

```json
{
  "id": "my_tool",
  "user_id": "user-uuid",
  "name": "My Tool",
  "meta": { "description": "...", "manifest": {} },
  "access_grants": [],
  "updated_at": 1700000000,
  "created_at": 1700000000,
  "write_access": true,
  "has_user_valves": false,
  "user": null
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or access denied |
| 404 | Tool not found |

---

### POST /api/v1/tools/id/{id}/update

**Summary:** Update an existing tool's source code and metadata.

**Auth:** Verified user (must be owner, have write access, or be admin)

> ⚠️ The updated Python source is re-compiled and loaded server-side. Function specs are re-extracted automatically.

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | id | string | Yes | Must match path `id` |
| Body | name | string | Yes | Display name |
| Body | content | string | Yes | Updated Python source code |
| Body | meta | ToolMeta | Yes | Updated metadata |
| Body | access_grants | AccessGrant[] \| null | No | Updated access grants |

**Response `200`**

Full `ToolModel` (same shape as export, including `content` and `specs`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Python compilation error |
| 401 | Not authenticated, not found, or unauthorized |

---

### POST /api/v1/tools/id/{id}/access/update

**Summary:** Update access grants for a tool.

**Auth:** Verified user (must be owner, have write access, or be admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | access_grants | object[] | Yes | New list of access grant objects |

Each access grant object:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| principal_type | `"user"` \| `"group"` | Yes | Type of principal |
| principal_id | string | Yes | User/group ID, or `"*"` for public access |
| permission | `"read"` \| `"write"` | Yes | Permission level |

> **Note:** Public access grants (`principal_id: "*"`) are stripped if the user lacks the `sharing.public_tools` permission.

**Response `200`**

Full `ToolModel` with updated access grants.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or unauthorized |
| 404 | Tool not found |

---

### DELETE /api/v1/tools/id/{id}/delete

**Summary:** Delete a tool by ID.

**Auth:** Verified user (must be owner, have write access, or be admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or unauthorized |

---

### GET /api/v1/tools/id/{id}/valves

**Summary:** Get the current global valve settings for a tool.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Response `200`**

```json
{
  "api_key": "sk-...",
  "max_results": 10
}
```

A free-form dictionary containing the current values of the tool's `Valves` fields. Returns `{}` if no valves are set.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error reading valves |
| 401 | Not authenticated or tool not found |

---

### GET /api/v1/tools/id/{id}/valves/spec

**Summary:** Get the JSON Schema specification for a tool's `Valves` configuration class.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

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
    "max_results": {
      "title": "Max Results",
      "type": "integer",
      "default": 10
    }
  },
  "required": ["api_key"]
}
```

Returns `null` if the tool has no `Valves` class.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or tool not found |

---

### POST /api/v1/tools/id/{id}/valves/update

**Summary:** Update global valve settings for a tool (shared across all users).

**Auth:** Verified user (must be owner, have write access, or be admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | *(valve fields)* | varies | No | Key-value pairs matching the tool's `Valves` schema; `null` values are ignored |

**Response `200`**

```json
{
  "api_key": "sk-...",
  "max_results": 5
}
```

Dictionary of the saved valve values.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Valve validation error or access denied |
| 401 | Not authenticated or tool not found |

---

### GET /api/v1/tools/id/{id}/valves/user

**Summary:** Get the current user's personal valve settings for a tool.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Response `200`**

```json
{
  "personal_api_key": "my-key"
}
```

Returns `{}` if no user valves are set. These values override global valves for the current user.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error reading user valves |
| 401 | Not authenticated or tool not found |

---

### GET /api/v1/tools/id/{id}/valves/user/spec

**Summary:** Get the JSON Schema specification for a tool's `UserValves` class.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Response `200`**

JSON Schema object (same structure as `/valves/spec`). Returns `null` if the tool has no `UserValves` class.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or tool not found |

---

### POST /api/v1/tools/id/{id}/valves/user/update

**Summary:** Update the current user's personal valve settings for a tool.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tool ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | *(user valve fields)* | varies | No | Key-value pairs matching the tool's `UserValves` schema; `null` values are ignored |

**Response `200`**

Dictionary of the saved user valve values.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Valve validation error |
| 401 | Not authenticated or tool not found |

---
