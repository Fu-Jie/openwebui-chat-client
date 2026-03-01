# Notes API Reference

Base path: `/api/v1/notes`

All endpoints require the user to have the `features.notes` permission (or be admin).

---

## Note Object Schemas

### `NoteModel`

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique note ID (UUID) |
| user_id | string | Owner user ID |
| title | string | Note title |
| data | object \| null | Note content and related data; contains `{"content": {"md": "..."}}` for Markdown |
| meta | object \| null | Note metadata |
| access_grants | array | List of `AccessGrantModel` objects controlling read/write access |
| created_at | integer | Creation timestamp (nanosecond epoch) |
| updated_at | integer | Last update timestamp (nanosecond epoch) |

### `AccessGrantModel`

| Field | Type | Description |
|-------|------|-------------|
| principal_type | string | `"user"` or `"group"` |
| principal_id | string | User/group ID, or `"*"` for public read access |
| permission | string | `"read"` or `"write"` |

### Note data structure

The `data` field stores the note's content:

```json
{
  "content": {
    "md": "# My Note\n\nThis is the markdown content."
  }
}
```

### `NoteResponse` (extends `NoteModel`)

| Field | Type | Description |
|-------|------|-------------|
| (all NoteModel fields) | — | See NoteModel schema |
| write_access | boolean | Whether the current user can edit this note |

### `NoteUserResponse` (extends `NoteModel`)

| Field | Type | Description |
|-------|------|-------------|
| (all NoteModel fields) | — | See NoteModel schema |
| user | object \| null | Note owner's user info (`id`, `name`, `email`, `profile_image_url`, `role`) |

### `NoteListResponse`

| Field | Type | Description |
|-------|------|-------------|
| items | array | Array of `NoteUserResponse` objects |
| total | integer | Total number of matching notes |

---

### GET `/api/v1/notes/`

**Summary:** Get a list of notes accessible to the current user, truncated to 1000 characters of Markdown content.

**Auth:** Verified user with `features.notes` permission

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | page | integer | No | Page number (60 items/page). Omit for all. |

**Response `200`**

```json
[
  {
    "id": "note-uuid",
    "user_id": "user-uuid",
    "title": "Meeting Notes",
    "data": {
      "content": {
        "md": "# Meeting Notes\n\n- Item 1\n- Item 2"
      }
    },
    "updated_at": 1700000000000000000,
    "created_at": 1699999000000000000,
    "user": {
      "id": "user-uuid",
      "name": "Alice",
      "email": "alice@example.com",
      "profile_image_url": "/user.png",
      "role": "user"
    }
  }
]
```

**Note:** The `data.content.md` field is truncated to 1000 characters in list responses to reduce payload size. Fetch the full note via `GET /api/v1/notes/{id}` for complete content.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Note UUID |
| user_id | string | Owner user ID |
| title | string | Note title |
| data | object \| null | Truncated note content |
| updated_at | integer | Last update timestamp (nanosecond epoch) |
| created_at | integer | Creation timestamp (nanosecond epoch) |
| user | object \| null | Note owner info |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or `features.notes` permission denied |

---

### GET `/api/v1/notes/search`

**Summary:** Search and filter notes with pagination; respects access-control grants.

**Auth:** Verified user with `features.notes` permission

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | query | string | No | Text search query (searches title and content) |
| Query | view_option | string | No | Filter view: e.g., `"mine"`, `"shared"` |
| Query | permission | string | No | Filter by permission type: `"read"` or `"write"` |
| Query | order_by | string | No | Sort field (e.g., `updated_at`, `title`) |
| Query | direction | string | No | Sort direction: `asc` or `desc` |
| Query | page | integer | No | Page number (default: 1, 60 items/page) |

**Response `200`**

```json
{
  "items": [
    {
      "id": "note-uuid",
      "user_id": "user-uuid",
      "title": "Meeting Notes",
      "data": { "content": { "md": "# Meeting Notes..." } },
      "meta": null,
      "access_grants": [],
      "created_at": 1699999000000000000,
      "updated_at": 1700000000000000000,
      "user": {
        "id": "user-uuid",
        "name": "Alice",
        "email": "alice@example.com",
        "profile_image_url": "/user.png",
        "role": "user"
      }
    }
  ],
  "total": 25
}
```

**Note:** Non-admin users only see notes they own or have explicit access grants to (via user-level or group-level grants). Admin users with `BYPASS_ADMIN_ACCESS_CONTROL=true` see all notes. The `data.content.md` field is truncated to 1000 characters.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or `features.notes` permission denied |

---

### POST `/api/v1/notes/create`

**Summary:** Create a new note for the current user.

**Auth:** Verified user with `features.notes` permission

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | title | string | Yes | Note title |
| Body | data | object | No | Note content: `{"content": {"md": "..."}}` |
| Body | meta | object | No | Note metadata |
| Body | access_grants | array | No | Initial access grants for the note |

```json
{
  "title": "Project Kickoff",
  "data": {
    "content": {
      "md": "# Project Kickoff\n\n## Goals\n- Define scope\n- Assign tasks"
    }
  },
  "meta": null,
  "access_grants": [
    { "principal_type": "group", "principal_id": "team-group-uuid", "permission": "read" }
  ]
}
```

**Response `200`**

`NoteModel` object for the created note:

```json
{
  "id": "new-note-uuid",
  "user_id": "user-uuid",
  "title": "Project Kickoff",
  "data": { "content": { "md": "# Project Kickoff\n..." } },
  "meta": null,
  "access_grants": [
    { "principal_type": "group", "principal_id": "team-group-uuid", "permission": "read" }
  ],
  "created_at": 1700000000000000000,
  "updated_at": 1700000000000000000
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated or `features.notes` permission denied |

---

### GET `/api/v1/notes/{id}`

**Summary:** Get a specific note by ID with full content and the current user's write-access flag.

**Auth:** Verified user with `features.notes` permission; must have read access (owner, explicit grant, or public read access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Note UUID |

**Response `200`**

```json
{
  "id": "note-uuid",
  "user_id": "user-uuid",
  "title": "Project Kickoff",
  "data": {
    "content": {
      "md": "# Project Kickoff\n\n## Goals\n- Define scope\n- Assign tasks"
    }
  },
  "meta": null,
  "access_grants": [
    { "principal_type": "group", "principal_id": "team-group-uuid", "permission": "read" }
  ],
  "created_at": 1699999000000000000,
  "updated_at": 1700000000000000000,
  "write_access": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| (all NoteModel fields) | — | See NoteModel schema |
| write_access | boolean | `true` if the current user can edit the note (is owner, admin, has write grant, or note is publicly readable) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or `features.notes` permission denied |
| 403 | No read access |
| 404 | Note not found |

---

### POST `/api/v1/notes/{id}/update`

**Summary:** Update a note's title, content, metadata, and access grants.

**Auth:** Verified user with `features.notes` permission; must be owner, admin, or have write access

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Note UUID |
| Body | title | string | Yes | Updated title |
| Body | data | object | No | Updated note content: `{"content": {"md": "..."}}` |
| Body | meta | object | No | Updated metadata |
| Body | access_grants | array | No | Updated access grants (replaces existing). Public sharing requires `sharing.public_notes` permission. |

```json
{
  "title": "Project Kickoff — Updated",
  "data": {
    "content": {
      "md": "# Updated Notes\n\nAll tasks assigned."
    }
  },
  "access_grants": [
    { "principal_type": "user", "principal_id": "*", "permission": "read" }
  ]
}
```

**Response `200`**

Updated `NoteModel` object. Also emits a `note-events` Socket.IO event to the room `note:{id}`.

**Note:** If the user lacks the `sharing.public_notes` permission and attempts to add a public read grant (`principal_id: "*"`), the public grant is silently stripped.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated or `features.notes` permission denied |
| 403 | No write access |
| 404 | Note not found |

---

### POST `/api/v1/notes/{id}/access/update`

**Summary:** Update only the access grants for a note without modifying its content.

**Auth:** Verified user with `features.notes` permission; must be owner, admin, or have write access

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Note UUID |
| Body | access_grants | array | Yes | New access grants list (replaces all existing grants) |

```json
{
  "access_grants": [
    { "principal_type": "group", "principal_id": "eng-group-uuid", "permission": "read" },
    { "principal_type": "group", "principal_id": "eng-group-uuid", "permission": "write" },
    { "principal_type": "user", "principal_id": "specific-user-uuid", "permission": "read" }
  ]
}
```

**Response `200`**

Updated `NoteModel` object with new `access_grants`.

**Note:** Public grants (`principal_id: "*"`) are silently removed if the user lacks the `sharing.public_notes` permission.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or `features.notes` permission denied |
| 403 | No write access |
| 404 | Note not found |

---

### DELETE `/api/v1/notes/{id}/delete`

**Summary:** Delete a note permanently.

**Auth:** Verified user with `features.notes` permission; must be owner, admin, or have write access

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Note UUID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Deletion failed |
| 401 | Not authenticated or `features.notes` permission denied |
| 403 | No write access |
| 404 | Note not found |

---

## Complex Schema: Access Grants

The `access_grants` array controls who can read and write a note. Each grant specifies a principal and a permission level:

| Scenario | Example grant |
|----------|--------------|
| Public read (anyone) | `{"principal_type": "user", "principal_id": "*", "permission": "read"}` |
| Specific user read | `{"principal_type": "user", "principal_id": "user-uuid", "permission": "read"}` |
| Specific user write | `{"principal_type": "user", "principal_id": "user-uuid", "permission": "write"}` |
| Group read | `{"principal_type": "group", "principal_id": "group-uuid", "permission": "read"}` |
| Group write | `{"principal_type": "group", "principal_id": "group-uuid", "permission": "write"}` |

The note owner and admins always have full access regardless of grants.

---

*Total endpoints documented: 7*
