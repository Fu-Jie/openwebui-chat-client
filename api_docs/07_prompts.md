# Prompts API

Base path: `/api/v1/prompts`

System prompts stored by users, triggered via slash commands (e.g. `/summarize`).

---

### GET /api/v1/prompts/

**Summary:** Return all prompts the current user can read.

**Auth:** Verified user

**Request** — no parameters.

**Response `200`**

```json
[
  {
    "id": "3f8a1e2b-...",
    "command": "summarize",
    "user_id": "user-123",
    "name": "Summarize",
    "content": "Please summarize the following text:\n\n{{input}}",
    "data": {},
    "meta": {},
    "tags": ["writing"],
    "is_active": true,
    "version_id": "hist-456",
    "created_at": 1710000000,
    "updated_at": 1710000001,
    "access_grants": []
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | UUID of the prompt |
| command | string | Slash command trigger (without `/`) |
| user_id | string | Owner's user ID |
| name | string | Human-readable title |
| content | string | Prompt body text |
| data | object | Extra structured data |
| meta | object | UI metadata |
| tags | array[string] | Classification tags |
| is_active | boolean | Whether the prompt is active |
| version_id | string | ID of the active history entry (production version) |
| created_at | integer | Unix epoch creation timestamp |
| updated_at | integer | Unix epoch last-updated timestamp |
| access_grants | array | Access control grants (see below) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/prompts/tags

**Summary:** Return the distinct set of tags across all accessible prompts.

**Auth:** Verified user

**Response `200`**

```json
["coding", "summarize", "writing"]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/prompts/list

**Summary:** Paginated, filterable list of prompts with write-access flags.

**Auth:** Verified user

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | No | Full-text search across name, command, content, user name/email |
| view_option | string | No | `created` (own prompts) or `shared` (others') |
| tag | string | No | Filter by tag |
| order_by | string | No | Sort field: `name`, `created_at`, `updated_at` |
| direction | string | No | `asc` or `desc` |
| page | integer | No | Page number (default: 1, page size: 30) |

**Response `200`**

```json
{
  "items": [
    {
      "id": "3f8a1e2b-...",
      "command": "summarize",
      "write_access": true,
      "...": "..."
    }
  ],
  "total": 42
}
```

| Field | Type | Description |
|-------|------|-------------|
| items | array | List of PromptAccessResponse objects |
| items[].write_access | boolean | Whether the current user can edit this prompt |
| total | integer | Total matching records (for pagination) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/prompts/create

**Summary:** Create a new prompt. Requires `workspace.prompts` or `workspace.prompts_import` permission.

**Auth:** Verified user (with permission)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | command | string | Yes | Slash command trigger (must be unique, without `/`) |
| Body | name | string | Yes | Human-readable title |
| Body | content | string | Yes | Prompt body text |
| Body | data | object | No | Extra structured data |
| Body | meta | object | No | UI metadata |
| Body | tags | array[string] | No | Classification tags |
| Body | access_grants | array[object] | No | Initial access control grants |
| Body | commit_message | string | No | Description of this version (stored in history) |
| Body | is_production | boolean | No | Set this version as production (default: true) |

**Response `200`** — PromptModel object (same as item in GET `/prompts/` response).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Command already in use |
| 401 | Not authenticated / insufficient permission |
| 422 | Validation error |

---

### GET /api/v1/prompts/command/{command}

**Summary:** Get a prompt by its slash command trigger.

**Auth:** Verified user (must have read access to the prompt)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| command | string | Slash command trigger (without `/`) |

**Response `200`** — PromptAccessResponse (includes `write_access` boolean).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 404 | Prompt not found or no read access |

---

### GET /api/v1/prompts/id/{prompt_id}

**Summary:** Get a prompt by its UUID.

**Auth:** Verified user (must have read access)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Response `200`** — PromptAccessResponse (same as command lookup).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 404 | Prompt not found or no read access |

---

### POST /api/v1/prompts/id/{prompt_id}/update

**Summary:** Update a prompt (creates a new history entry if content changes).

**Auth:** Verified user (owner, write-access grant, or admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Request** — same body schema as `POST /prompts/create`.

**Response `200`** — updated PromptModel.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Command collision or update failed |
| 401 | Not authenticated / no write access |
| 404 | Prompt not found |

---

### POST /api/v1/prompts/id/{prompt_id}/update/meta

**Summary:** Update only name, command, and tags without creating a history entry.

**Auth:** Verified user (owner, write-access grant, or admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | name | string | Yes | New display name |
| Body | command | string | Yes | New slash command trigger |
| Body | tags | array[string] | No | Updated tags |

**Response `200`** — updated PromptModel.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Command collision |
| 401 | Not authenticated / no write access |
| 404 | Prompt not found |

---

### POST /api/v1/prompts/id/{prompt_id}/update/version

**Summary:** Set the active production version of a prompt from its history.

**Auth:** Verified user (owner, write-access grant, or admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | version_id | string | Yes | History entry ID to activate |

**Response `200`** — updated PromptModel (content restored from the chosen history snapshot).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Update failed |
| 401 | Not authenticated / no write access |
| 404 | Prompt or history entry not found |

---

### POST /api/v1/prompts/id/{prompt_id}/access/update

**Summary:** Replace the access grant list for a prompt.

**Auth:** Verified user (owner, write-access grant, or admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | access_grants | array[object] | Yes | Full replacement list of access grant objects |

**Access Grant Object**

```json
{
  "principal_type": "user",
  "principal_id": "user-abc",
  "permission": "read"
}
```

| Field | Type | Description |
|-------|------|-------------|
| principal_type | string | `user` or `group`. Use `principal_id: "*"` for public. |
| principal_id | string | User ID, group ID, or `*` for public |
| permission | string | `read` or `write` |

**Response `200`** — PromptModel with updated `access_grants`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / no write access / no public-sharing permission |
| 404 | Prompt not found |

---

### POST /api/v1/prompts/id/{prompt_id}/toggle

**Summary:** Toggle the `is_active` flag on a prompt.

**Auth:** Verified user (owner, write-access grant, or admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Response `200`** — updated PromptModel with toggled `is_active`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Toggle failed |
| 401 | Not authenticated / no write access |
| 404 | Prompt not found |

---

### DELETE /api/v1/prompts/id/{prompt_id}/delete

**Summary:** Permanently delete a prompt and all its history.

**Auth:** Verified user (owner, write-access grant, or admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / no write access |
| 404 | Prompt not found |

---

### GET /api/v1/prompts/id/{prompt_id}/history

**Summary:** Get the version history of a prompt (paginated, 20 per page).

**Auth:** Verified user (must have read access)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| page | integer | No | Page offset (0-indexed, default: 0) |

**Response `200`**

```json
[
  {
    "id": "hist-456",
    "prompt_id": "3f8a1e2b-...",
    "snapshot": {
      "name": "Summarize",
      "content": "...",
      "command": "summarize",
      "data": {},
      "meta": {},
      "tags": [],
      "access_grants": []
    },
    "user_id": "user-123",
    "parent_id": null,
    "commit_message": "Initial version",
    "created_at": 1710000000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | History entry UUID |
| prompt_id | string | Parent prompt UUID |
| snapshot | object | Full state at the time of this version |
| user_id | string | User who created this version |
| parent_id | string\|null | Previous history entry ID (for lineage) |
| commit_message | string | Description of changes |
| created_at | integer | Unix epoch creation timestamp |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / no read access |
| 404 | Prompt not found |

---

### GET /api/v1/prompts/id/{prompt_id}/history/{history_id}

**Summary:** Get a specific history entry by its ID.

**Auth:** Verified user (must have read access)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |
| history_id | string | History entry UUID |

**Response `200`** — single PromptHistoryModel (same schema as array item above).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / no read access |
| 404 | Prompt or history entry not found |

---

### DELETE /api/v1/prompts/id/{prompt_id}/history/{history_id}

**Summary:** Delete a history entry (cannot delete the active production version).

**Auth:** Verified user (owner, write-access grant, or admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |
| history_id | string | History entry UUID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Cannot delete active production version |
| 401 | Not authenticated / no write access |
| 404 | Prompt or history entry not found |

---

### GET /api/v1/prompts/id/{prompt_id}/history/diff

**Summary:** Compute a diff between two history versions.

**Auth:** Verified user (must have read access)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| prompt_id | string | Prompt UUID |

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| from_id | string | Yes | Source history entry ID |
| to_id | string | Yes | Target history entry ID |

**Response `200`**

```json
{
  "from": { "content": "old text", "...": "..." },
  "to": { "content": "new text", "...": "..." },
  "changes": [ ... ]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / no read access |
| 404 | Prompt or one of the history entries not found |
