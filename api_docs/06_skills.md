# Skills API

Base path: `/api/v1/skills`

Skills are agent-style Python plugins that users can create and share. Unlike Functions (which are admin-only and applied system-wide), Skills are user-owned and subject to access-control grants. Each skill stores its Python source code in the `content` field, along with metadata and activity state.

> ⚠️ **Security note:** Skill content may be executed as Python code. Only users with the `workspace.skills` permission should be permitted to create skills.

---

## Schema

### SkillMeta

```json
{
  "tags": ["search", "utility"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| tags | string[] | Categorization tags for the skill |

### SkillModel

```json
{
  "id": "web-search",
  "user_id": "user-uuid",
  "name": "Web Search",
  "description": "Search the web using DuckDuckGo",
  "content": "class Skill:\n    ...",
  "meta": {
    "tags": ["search"]
  },
  "is_active": true,
  "access_grants": [
    {
      "principal_type": "user",
      "principal_id": "*",
      "permission": "read"
    }
  ],
  "updated_at": 1700000000,
  "created_at": 1700000000
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier (lowercase, hyphens allowed) |
| user_id | string | Owner's user ID |
| name | string | Display name (unique across all skills) |
| description | string \| null | Optional human-readable description |
| content | string | Python source code |
| meta | SkillMeta | Metadata with tags |
| is_active | boolean | Whether the skill is enabled |
| access_grants | AccessGrant[] | List of access control grants |
| updated_at | integer | Last updated Unix timestamp |
| created_at | integer | Created Unix timestamp |

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

### GET /api/v1/skills/

**Summary:** List all skills accessible to the current user.

**Auth:** Verified user

**Response `200`**

```json
[
  {
    "id": "web-search",
    "user_id": "user-uuid",
    "name": "Web Search",
    "description": "Search the web",
    "meta": { "tags": ["search"] },
    "is_active": true,
    "access_grants": [],
    "updated_at": 1700000000,
    "created_at": 1700000000,
    "user": null
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| *(all SkillModel fields)* | — | See SkillModel schema |
| user | object \| null | Owner user info (if available) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/skills/list

**Summary:** Paginated list of skills accessible to the current user with search, filter, and write-access info.

**Auth:** Verified user

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | No | Search string matched against name, description, ID, owner name/email |
| view_option | string | No | `"created"` = only owned skills; `"shared"` = only skills shared by others |
| page | integer | No | Page number (1-based, default: 1) |

**Response `200`**

```json
{
  "items": [
    {
      "id": "web-search",
      "user_id": "user-uuid",
      "name": "Web Search",
      "description": "Search the web",
      "meta": { "tags": ["search"] },
      "is_active": true,
      "access_grants": [],
      "updated_at": 1700000000,
      "created_at": 1700000000,
      "write_access": true,
      "user": null
    }
  ],
  "total": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| items | SkillAccessResponse[] | Skills for the current page |
| items[].write_access | boolean | Whether the current user can modify this skill |
| total | integer | Total number of matching skills (across all pages) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/skills/export

**Summary:** Export all accessible skills as full model objects including `content`.

**Auth:** Verified user (requires `workspace.skills` permission for non-admins)

**Response `200`**

Array of full `SkillModel` objects (including `content` field).

```json
[
  {
    "id": "web-search",
    "user_id": "user-uuid",
    "name": "Web Search",
    "description": "Search the web",
    "content": "class Skill:\n    ...",
    "meta": { "tags": ["search"] },
    "is_active": true,
    "access_grants": [],
    "updated_at": 1700000000,
    "created_at": 1700000000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or insufficient permissions |

---

### POST /api/v1/skills/create

**Summary:** Create a new skill.

**Auth:** Verified user (requires `workspace.skills` permission for non-admins)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | id | string | Yes | Unique identifier (converted to lowercase with hyphens replacing spaces) |
| Body | name | string | Yes | Display name (must be unique) |
| Body | description | string \| null | No | Optional description |
| Body | content | string | Yes | Python source code |
| Body | meta | SkillMeta | No | Metadata (tags); defaults to `{"tags": []}` |
| Body | is_active | boolean | No | Whether skill is active; defaults to `true` |
| Body | access_grants | AccessGrant[] \| null | No | Initial access grants |

**Response `200`**

```json
{
  "id": "web-search",
  "user_id": "user-uuid",
  "name": "Web Search",
  "description": "Search the web",
  "meta": { "tags": [] },
  "is_active": true,
  "access_grants": [],
  "updated_at": 1700000000,
  "created_at": 1700000000
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | ID already taken or creation error |
| 401 | Not authenticated or insufficient permissions |

---

### GET /api/v1/skills/id/{id}

**Summary:** Retrieve a skill by ID with write-access flag.

**Auth:** Verified user (must have read access to the skill)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Skill ID |

**Response `200`**

```json
{
  "id": "web-search",
  "user_id": "user-uuid",
  "name": "Web Search",
  "description": "Search the web",
  "content": "class Skill:\n    ...",
  "meta": { "tags": [] },
  "is_active": true,
  "access_grants": [],
  "updated_at": 1700000000,
  "created_at": 1700000000,
  "write_access": true,
  "user": null
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or access denied |
| 404 | Skill not found |

---

### POST /api/v1/skills/id/{id}/update

**Summary:** Update an existing skill's content and metadata.

**Auth:** Verified user (must be owner, have write access, or be admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Skill ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | id | string | Yes | Must match path `id` |
| Body | name | string | Yes | Display name |
| Body | description | string \| null | No | Updated description |
| Body | content | string | Yes | Updated Python source code |
| Body | meta | SkillMeta | No | Updated metadata |
| Body | is_active | boolean | No | Updated active state |
| Body | access_grants | AccessGrant[] \| null | No | Updated access grants |

**Response `200`**

Updated `SkillModel` including `content` field.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Update error |
| 401 | Not authenticated or unauthorized |
| 404 | Skill not found |

---

### POST /api/v1/skills/id/{id}/access/update

**Summary:** Update access grants for a skill.

**Auth:** Verified user (must be owner, have write access, or be admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Skill ID |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | access_grants | object[] | Yes | New list of access grant objects |

Each access grant:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| principal_type | `"user"` \| `"group"` | Yes | Type of principal |
| principal_id | string | Yes | User/group ID, or `"*"` for public access |
| permission | `"read"` \| `"write"` | Yes | Permission level |

> **Note:** Public access grants (`principal_id: "*"`) are stripped if the user lacks the `sharing.public_skills` permission.

**Response `200`**

Updated `SkillModel` with new access grants.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or unauthorized |
| 404 | Skill not found |

---

### POST /api/v1/skills/id/{id}/toggle

**Summary:** Toggle the `is_active` state of a skill.

**Auth:** Verified user (must be owner, have write access, or be admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Skill ID |

**Response `200`**

Updated `SkillModel` with the new `is_active` value.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Toggle error |
| 401 | Not authenticated or unauthorized |
| 404 | Skill not found |

---

### DELETE /api/v1/skills/id/{id}/delete

**Summary:** Delete a skill by ID.

**Auth:** Verified user (must be owner, have write access, or be admin)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Skill ID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or unauthorized |
| 404 | Skill not found |

---
