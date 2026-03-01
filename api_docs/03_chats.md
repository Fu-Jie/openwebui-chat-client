# Chats API Reference

Base path: `/api/v1/chats`

All endpoints require authentication (verified user) unless otherwise noted.

---

## Chat Object Schema

### `ChatResponse`

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique chat ID (UUID) |
| user_id | string | Owner user ID |
| title | string | Chat title |
| chat | object | Full chat JSON (see Chat Body below) |
| updated_at | integer | Last update timestamp (epoch seconds) |
| created_at | integer | Creation timestamp (epoch seconds) |
| share_id | string \| null | Share ID if shared publicly |
| archived | boolean | Whether the chat is archived |
| pinned | boolean | Whether the chat is pinned |
| meta | object | Metadata (includes `tags` array) |
| folder_id | string \| null | Folder the chat belongs to |

### `ChatTitleIdResponse`

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique chat ID |
| title | string | Chat title |
| updated_at | integer | Last update timestamp (epoch seconds) |
| created_at | integer | Creation timestamp (epoch seconds) |

### Chat Body — `history` structure

The `chat` field in `ChatResponse` contains the full chat JSON. The critical sub-structure is:

```json
{
  "title": "My Chat",
  "history": {
    "currentId": "msg-uuid-latest",
    "messages": {
      "msg-uuid-1": {
        "id": "msg-uuid-1",
        "parentId": null,
        "childrenIds": ["msg-uuid-2"],
        "role": "user",
        "content": "Hello!",
        "timestamp": 1700000000,
        "model": null
      },
      "msg-uuid-2": {
        "id": "msg-uuid-2",
        "parentId": "msg-uuid-1",
        "childrenIds": [],
        "role": "assistant",
        "content": "Hi there!",
        "timestamp": 1700000005,
        "model": "gpt-4o",
        "annotation": {
          "rating": 1,
          "tags": ["helpful"]
        }
      }
    }
  }
}
```

`history.messages` is a **dict keyed by message ID** (not an array). `history.currentId` points to the leaf message of the current conversation branch.

---

### GET `/api/v1/chats/`

**Summary:** List the current user's chats (title + ID) with optional pagination.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | page | integer | No | Page number (60 items/page). Omit for all. |
| Query | include_pinned | boolean | No | Include pinned chats (default: false) |
| Query | include_folders | boolean | No | Include folder-organized chats (default: false) |

**Response `200`**

```json
[
  {
    "id": "abc123",
    "title": "My First Chat",
    "updated_at": 1700000000,
    "created_at": 1699999000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Chat ID |
| title | string | Chat title |
| updated_at | integer | Last update timestamp |
| created_at | integer | Creation timestamp |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |

---

### GET `/api/v1/chats/list`

**Summary:** Alias for `GET /api/v1/chats/` — same parameters and response.

**Auth:** Verified user

**Request**

Same as `GET /api/v1/chats/`.

**Response `200`**

Same as `GET /api/v1/chats/`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |

---

### GET `/api/v1/chats/stats/usage`

**Summary:** Return paginated usage statistics for the current user's chats (EXPERIMENTAL).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | items_per_page | integer | No | Items per page (default: 50) |
| Query | page | integer | No | Page number (default: 1) |

**Response `200`**

```json
{
  "items": [
    {
      "id": "chat-uuid",
      "models": {"gpt-4o": 3},
      "message_count": 6,
      "history_models": {"gpt-4o": 4},
      "history_message_count": 8,
      "history_user_message_count": 4,
      "history_assistant_message_count": 4,
      "average_response_time": 2.5,
      "average_user_message_content_length": 45.0,
      "average_assistant_message_content_length": 120.0,
      "tags": ["work"],
      "last_message_at": 1700000005,
      "updated_at": 1700000005,
      "created_at": 1699999000
    }
  ],
  "total": 42
}
```

| Field | Type | Description |
|-------|------|-------------|
| items | array | Array of chat usage stat objects |
| items[].id | string | Chat ID |
| items[].models | object | Models used in the active branch, keyed by model ID with usage counts |
| items[].message_count | integer | Number of messages in the active branch |
| items[].history_models | object | Models used across all history messages |
| items[].history_message_count | integer | Total messages in `history.messages` dict |
| items[].history_user_message_count | integer | User messages in history |
| items[].history_assistant_message_count | integer | Assistant messages in history |
| items[].average_response_time | float | Avg seconds between user send and assistant reply |
| items[].average_user_message_content_length | float | Avg character count of user messages |
| items[].average_assistant_message_content_length | float | Avg character count of assistant messages |
| items[].tags | array[string] | Tags on the chat |
| items[].last_message_at | integer | Timestamp of last message |
| items[].updated_at | integer | Chat last-updated timestamp |
| items[].created_at | integer | Chat creation timestamp |
| total | integer | Total number of chats for the user |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |

---

### GET `/api/v1/chats/stats/export`

**Summary:** Export detailed statistics for all the current user's chats; supports streaming (NDJSON) or paginated JSON.

**Auth:** Verified user (must have `ENABLE_COMMUNITY_SHARING` enabled, or be admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | updated_at | integer | No | Filter chats updated at or after this epoch timestamp |
| Query | page | integer | No | Page number for paginated mode (default: 1, 10 items/page) |
| Query | stream | boolean | No | If `true`, stream NDJSON response instead of paginated JSON |

**Response `200` — Paginated (default)**

```json
{
  "type": "chats",
  "items": [
    {
      "id": "chat-uuid",
      "user_id": "user-uuid",
      "created_at": 1699999000,
      "updated_at": 1700000000,
      "tags": ["work"],
      "stats": {
        "average_response_time": 2.5,
        "average_user_message_content_length": 45.0,
        "average_assistant_message_content_length": 120.0,
        "models": {"gpt-4o": 2},
        "message_count": 4,
        "history_models": {"gpt-4o": 3},
        "history_message_count": 6,
        "history_user_message_count": 3,
        "history_assistant_message_count": 3
      },
      "chat": {
        "history": {
          "messages": {
            "msg-uuid": {
              "id": "msg-uuid",
              "role": "user",
              "model": null,
              "content_length": 45,
              "token_count": null,
              "timestamp": 1700000000,
              "rating": null,
              "tags": null
            }
          },
          "currentId": "msg-uuid"
        }
      }
    }
  ],
  "total": 100,
  "page": 1
}
```

**Response `200` — Streaming (when `stream=true`)**

Content-Type: `application/x-ndjson`  
Each line is a JSON-serialized `ChatStatsExport` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request or processing error |
| 401 | Not authenticated or insufficient permissions |

---

### GET `/api/v1/chats/stats/export/{chat_id}`

**Summary:** Export detailed statistics for a single chat by ID.

**Auth:** Verified user (must own the chat, or be admin with `ENABLE_COMMUNITY_SHARING`)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | chat_id | string | Yes | Chat UUID |

**Response `200`**

```json
{
  "id": "chat-uuid",
  "user_id": "user-uuid",
  "created_at": 1699999000,
  "updated_at": 1700000000,
  "tags": ["work"],
  "stats": {
    "average_response_time": 2.5,
    "average_user_message_content_length": 45.0,
    "average_assistant_message_content_length": 120.0,
    "models": {"gpt-4o": 2},
    "message_count": 4,
    "history_models": {"gpt-4o": 3},
    "history_message_count": 6,
    "history_user_message_count": 3,
    "history_assistant_message_count": 3
  },
  "chat": {
    "history": {
      "messages": {},
      "currentId": null
    }
  }
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Processing error |
| 401 | Not authenticated or no permission |
| 404 | Chat not found |

---

### DELETE `/api/v1/chats/`

**Summary:** Delete all chats belonging to the current user.

**Auth:** Verified user (requires `chat.delete` permission for non-admin users)

**Request**

No additional parameters.

**Response `200`**

```json
true
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | boolean | `true` on success |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or insufficient permissions |

---

### GET `/api/v1/chats/list/user/{user_id}`

**Summary:** Admin endpoint to list chats for any user by user ID, including archived.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | user_id | string | Yes | Target user UUID |
| Query | page | integer | No | Page number (default: 1, 60 items/page) |
| Query | query | string | No | Search query to filter by title |
| Query | order_by | string | No | Sort field (e.g., `updated_at`) |
| Query | direction | string | No | Sort direction: `asc` or `desc` |

**Response `200`**

```json
[
  {
    "id": "chat-uuid",
    "title": "Chat Title",
    "updated_at": 1700000000,
    "created_at": 1699999000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or `ENABLE_ADMIN_CHAT_ACCESS` disabled |
| 403 | Not admin |

---

### POST `/api/v1/chats/new`

**Summary:** Create a new chat for the current user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | chat | object | Yes | Chat JSON body (must contain at minimum `{"title": "..."}`) |
| Body | folder_id | string | No | Folder to place the chat in |

```json
{
  "chat": {
    "title": "My New Chat",
    "history": {
      "currentId": null,
      "messages": {}
    }
  },
  "folder_id": null
}
```

**Response `200`**

Returns a `ChatResponse` object (see Chat Object Schema).

```json
{
  "id": "new-chat-uuid",
  "user_id": "user-uuid",
  "title": "My New Chat",
  "chat": { "title": "My New Chat", "history": { "currentId": null, "messages": {} } },
  "updated_at": 1700000000,
  "created_at": 1700000000,
  "share_id": null,
  "archived": false,
  "pinned": false,
  "meta": {},
  "folder_id": null
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |

---

### POST `/api/v1/chats/import`

**Summary:** Bulk import chats for the current user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | chats | array | Yes | Array of `ChatImportForm` objects |

Each item in `chats`:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| chat | object | Yes | Full chat JSON body |
| folder_id | string | No | Folder ID |
| meta | object | No | Metadata (tags, etc.) |
| pinned | boolean | No | Pin state (default: false) |
| created_at | integer | No | Override creation timestamp |
| updated_at | integer | No | Override update timestamp |

```json
{
  "chats": [
    {
      "chat": { "title": "Imported Chat", "history": { "currentId": null, "messages": {} } },
      "meta": { "tags": ["imported"] },
      "pinned": false
    }
  ]
}
```

**Response `200`**

```json
[
  {
    "id": "new-uuid",
    "user_id": "user-uuid",
    "title": "Imported Chat",
    "chat": {},
    "updated_at": 1700000000,
    "created_at": 1700000000,
    "share_id": null,
    "archived": false,
    "pinned": false,
    "meta": {},
    "folder_id": null
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |

---

### GET `/api/v1/chats/search`

**Summary:** Search the current user's chats by text (title or content); also supports `tag:<name>` queries.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | text | string | Yes | Search text; use `tag:<name>` to filter by tag |
| Query | page | integer | No | Page number (default: 1, 60 items/page) |

**Response `200`**

```json
[
  {
    "id": "chat-uuid",
    "title": "My Chat",
    "updated_at": 1700000000,
    "created_at": 1699999000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/chats/folder/{folder_id}`

**Summary:** Get all chats (full `ChatResponse`) within a folder, including chats in child folders.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | folder_id | string | Yes | Folder UUID |

**Response `200`**

Array of `ChatResponse` objects (see Chat Object Schema).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/chats/folder/{folder_id}/list`

**Summary:** Get a paginated lightweight list (title, id, updated_at) of chats in a folder.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | folder_id | string | Yes | Folder UUID |
| Query | page | integer | No | Page number (default: 1, 10 items/page) |

**Response `200`**

```json
[
  {
    "id": "chat-uuid",
    "title": "My Chat",
    "updated_at": 1700000000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |

---

### GET `/api/v1/chats/pinned`

**Summary:** Get the current user's pinned chats (title + ID list).

**Auth:** Verified user

**Request**

No additional parameters.

**Response `200`**

Array of `ChatTitleIdResponse` objects.

```json
[
  {
    "id": "chat-uuid",
    "title": "Important Chat",
    "updated_at": 1700000000,
    "created_at": 1699999000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/chats/all`

**Summary:** Get all chats (full `ChatResponse`) belonging to the current user.

**Auth:** Verified user

**Request**

No additional parameters.

**Response `200`**

Array of `ChatResponse` objects (see Chat Object Schema).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/chats/all/archived`

**Summary:** Get all archived chats (full `ChatResponse`) for the current user.

**Auth:** Verified user

**Request**

No additional parameters.

**Response `200`**

Array of `ChatResponse` objects.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/chats/all/tags`

**Summary:** Get all tags used by the current user across their chats.

**Auth:** Verified user

**Request**

No additional parameters.

**Response `200`**

```json
[
  {
    "id": "work",
    "name": "work",
    "user_id": "user-uuid",
    "meta": {},
    "created_at": 1699999000,
    "updated_at": 1700000000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Tag ID (lowercased name with underscores) |
| name | string | Human-readable tag name |
| user_id | string | Owner user ID |
| meta | object | Tag metadata |
| created_at | integer | Creation timestamp |
| updated_at | integer | Last update timestamp |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |

---

### GET `/api/v1/chats/all/db`

**Summary:** Admin endpoint to export all chats from the entire database.

**Auth:** Admin only (requires `ENABLE_ADMIN_EXPORT=true`)

**Request**

No additional parameters.

**Response `200`**

Array of all `ChatResponse` objects across all users.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or `ENABLE_ADMIN_EXPORT` disabled |
| 403 | Not admin |

---

### GET `/api/v1/chats/archived`

**Summary:** Get the current user's archived chats (title + ID) with optional pagination and filtering.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | page | integer | No | Page number (default: 1, 60 items/page) |
| Query | query | string | No | Text search filter |
| Query | order_by | string | No | Sort field |
| Query | direction | string | No | `asc` or `desc` |

**Response `200`**

Array of `ChatTitleIdResponse` objects.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST `/api/v1/chats/archive/all`

**Summary:** Archive all non-archived chats for the current user.

**Auth:** Verified user

**Request**

No additional parameters.

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST `/api/v1/chats/unarchive/all`

**Summary:** Unarchive all archived chats for the current user.

**Auth:** Verified user

**Request**

No additional parameters.

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/chats/shared`

**Summary:** Get the current user's shared chats list (id, title, share_id) with optional pagination.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | page | integer | No | Page number (default: 1, 60 items/page) |
| Query | query | string | No | Text search filter |
| Query | order_by | string | No | Sort field |
| Query | direction | string | No | `asc` or `desc` |

**Response `200`**

```json
[
  {
    "id": "chat-uuid",
    "title": "My Shared Chat",
    "share_id": "share-uuid",
    "updated_at": 1700000000,
    "created_at": 1699999000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/chats/share/{share_id}`

**Summary:** Get a shared chat by its share ID (publicly accessible to verified users).

**Auth:** Verified user (pending users are rejected)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | share_id | string | Yes | Share UUID or chat UUID (admin with `ENABLE_ADMIN_CHAT_ACCESS`) |

**Response `200`**

`ChatResponse` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated, pending user, or share not found |

---

### POST `/api/v1/chats/tags`

**Summary:** Get the current user's chats filtered by a specific tag name.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | name | string | Yes | Tag name to filter by |
| Body | skip | integer | No | Offset (default: 0) |
| Body | limit | integer | No | Max results (default: 50) |

```json
{
  "name": "work",
  "skip": 0,
  "limit": 50
}
```

**Response `200`**

Array of `ChatTitleIdResponse` objects.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/chats/{id}`

**Summary:** Get a single chat by ID (must belong to the current user).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

`ChatResponse` object (see Chat Object Schema).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found/not owned |

---

### POST `/api/v1/chats/{id}`

**Summary:** Update the chat JSON body of an existing chat (merges new chat fields over existing).

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |
| Body | chat | object | Yes | Chat data to merge (history, title, etc.) |
| Body | folder_id | string | No | Folder ID |

```json
{
  "chat": {
    "title": "Updated Title",
    "history": {
      "currentId": "msg-uuid-2",
      "messages": {
        "msg-uuid-1": { "id": "msg-uuid-1", "role": "user", "content": "Hello", "timestamp": 1700000000 },
        "msg-uuid-2": { "id": "msg-uuid-2", "parentId": "msg-uuid-1", "role": "assistant", "content": "Hi!", "timestamp": 1700000005 }
      }
    }
  }
}
```

**Response `200`**

Updated `ChatResponse` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not owned |

---

### POST `/api/v1/chats/{id}/messages/{message_id}`

**Summary:** Update the content of a specific message within a chat's history (upserts the message).

**Auth:** Verified user (must own the chat, or be admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |
| Path | message_id | string | Yes | Message UUID within `history.messages` |
| Body | content | string | Yes | New message content |

```json
{
  "content": "Updated message content"
}
```

**Response `200`**

Updated `ChatResponse` object. Also emits a `chat:message` Socket.IO event to connected clients.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or insufficient permissions |

---

### POST `/api/v1/chats/{id}/messages/{message_id}/event`

**Summary:** Emit a Socket.IO event for a specific chat message to connected clients.

**Auth:** Verified user (must own the chat, or be admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |
| Path | message_id | string | Yes | Message UUID |
| Body | type | string | Yes | Event type string |
| Body | data | object | Yes | Event data payload |

```json
{
  "type": "chat:message:delta",
  "data": { "content": "partial..." }
}
```

**Response `200`**

```json
true
```

Returns `false` if no event emitter was available.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or insufficient permissions |

---

### DELETE `/api/v1/chats/{id}`

**Summary:** Delete a chat by ID.

**Auth:** Verified user (requires `chat.delete` permission for non-admin users; admin can delete any chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or insufficient permissions |
| 404 | Chat not found |

---

### GET `/api/v1/chats/{id}/pinned`

**Summary:** Get the pin status of a specific chat.

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

```json
true
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | boolean | `true` if pinned, `false` otherwise |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found |

---

### POST `/api/v1/chats/{id}/pin`

**Summary:** Toggle the pin status of a chat.

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

Updated `ChatResponse` object with new `pinned` value.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found |

---

### POST `/api/v1/chats/{id}/clone`

**Summary:** Clone a chat owned by the current user into a new chat.

**Auth:** Verified user (must own the source chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Source chat UUID |
| Body | title | string | No | Title for the clone (default: `"Clone of {original title}"`) |

```json
{
  "title": "My Clone"
}
```

**Response `200`**

`ChatResponse` of the newly created clone. The clone includes `originalChatId` and `branchPointMessageId` in its chat JSON.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found |
| 500 | Clone creation failed |

---

### POST `/api/v1/chats/{id}/clone/shared`

**Summary:** Clone a shared (publicly accessible) chat into the current user's account.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Share ID or chat UUID (admin only) |

**Response `200`**

`ChatResponse` of the newly created clone.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or share not found |
| 500 | Clone creation failed |

---

### POST `/api/v1/chats/{id}/archive`

**Summary:** Toggle the archive status of a chat (archive or unarchive).

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

Updated `ChatResponse` object with new `archived` value.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found |

---

### POST `/api/v1/chats/{id}/share`

**Summary:** Create or update a public share link for a chat.

**Auth:** Verified user (requires `chat.share` permission or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

`ChatResponse` object with `share_id` populated.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or insufficient permissions |
| 500 | Share creation failed |

---

### DELETE `/api/v1/chats/{id}/share`

**Summary:** Remove the public share link from a chat.

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

```json
true
```

Returns `false` if the chat was not shared.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not owned |

---

### POST `/api/v1/chats/{id}/folder`

**Summary:** Move a chat to a different folder (or remove from any folder).

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |
| Body | folder_id | string \| null | No | Target folder UUID, or `null` to remove from folder |

```json
{
  "folder_id": "folder-uuid"
}
```

**Response `200`**

Updated `ChatResponse` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found |

---

### GET `/api/v1/chats/{id}/tags`

**Summary:** Get all tags associated with a specific chat.

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

Array of tag objects (same as `GET /api/v1/chats/all/tags` items).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found |

---

### POST `/api/v1/chats/{id}/tags`

**Summary:** Add a tag to a chat by tag name.

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |
| Body | name | string | Yes | Tag name (will be lowercased and spaces replaced with underscores) |

```json
{
  "name": "work project"
}
```

**Response `200`**

Updated array of tag objects for the chat.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Tag name is `"none"` (reserved) |
| 401 | Not authenticated or chat not found |

---

### DELETE `/api/v1/chats/{id}/tags`

**Summary:** Remove a specific tag from a chat; deletes the tag globally if it has no remaining chats.

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |
| Body | name | string | Yes | Tag name to remove |

```json
{
  "name": "work"
}
```

**Response `200`**

Updated array of remaining tag objects for the chat.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found |

---

### DELETE `/api/v1/chats/{id}/tags/all`

**Summary:** Remove all tags from a chat.

**Auth:** Verified user (must own the chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Chat UUID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or chat not found |

---

*Total endpoints documented: 39 (including both `GET /` and `GET /list` aliases)*
