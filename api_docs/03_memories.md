# Memories API Reference

Base path: `/api/v1/memories`

All endpoints require the memories feature to be enabled (`ENABLE_MEMORIES=true`) and the user to have the `features.memories` permission.

---

## Memory Object Schema

### `MemoryModel`

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique memory ID (UUID) |
| user_id | string | Owner user ID |
| content | string | Memory text content |
| updated_at | integer | Last update timestamp (epoch seconds) |
| created_at | integer | Creation timestamp (epoch seconds) |

---

### GET `/api/v1/memories/`

**Summary:** Get all memories belonging to the current user.

**Auth:** Verified user with `features.memories` permission

**Request**

No additional parameters.

**Response `200`**

```json
[
  {
    "id": "memory-uuid",
    "user_id": "user-uuid",
    "content": "User prefers concise answers.",
    "updated_at": 1700000000,
    "created_at": 1699999000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Memory UUID |
| user_id | string | Owner user ID |
| content | string | Memory text |
| updated_at | integer | Last update timestamp |
| created_at | integer | Creation timestamp |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | `features.memories` permission denied |
| 404 | Memories feature disabled |

---

### POST `/api/v1/memories/add`

**Summary:** Add a new memory for the current user; generates and stores an embedding vector.

**Auth:** Verified user with `features.memories` permission

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | content | string | Yes | Text content to remember |

```json
{
  "content": "User prefers bullet-point summaries."
}
```

**Response `200`**

```json
{
  "id": "memory-uuid",
  "user_id": "user-uuid",
  "content": "User prefers bullet-point summaries.",
  "updated_at": 1700000000,
  "created_at": 1700000000
}
```

**Implementation note:** This endpoint intentionally avoids holding a DB session while generating the embedding (which may take 1–5+ seconds via an external API). The vector is stored in the collection `user-memory-{user_id}` in the configured vector database.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | `features.memories` permission denied |
| 404 | Memories feature disabled |

---

### POST `/api/v1/memories/query`

**Summary:** Perform a semantic (vector similarity) search over the current user's memories.

**Auth:** Verified user with `features.memories` permission

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | content | string | Yes | Query text to embed and search against |
| Body | k | integer | No | Number of results to return (default: 1) |

```json
{
  "content": "What does the user prefer about formatting?",
  "k": 3
}
```

**Response `200`**

Raw vector search results from the configured vector database. Structure depends on the vector DB client (typically includes `ids`, `distances`, and `documents`):

```json
{
  "ids": [["memory-uuid-1", "memory-uuid-2"]],
  "distances": [[0.12, 0.34]],
  "documents": [["User prefers bullet-point summaries.", "User likes concise answers."]]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | `features.memories` permission denied |
| 404 | Memories feature disabled, or no memories found for user |

---

### POST `/api/v1/memories/reset`

**Summary:** Delete and regenerate all embedding vectors for the current user's memories in the vector database.

**Auth:** Verified user with `features.memories` permission

**Request**

No additional parameters.

**Response `200`**

```json
true
```

**Implementation note:** All embeddings are generated in parallel via `asyncio.gather()`. This endpoint does not hold a DB session during the (potentially long-running) embedding generation phase.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | `features.memories` permission denied |
| 404 | Memories feature disabled |

---

### DELETE `/api/v1/memories/delete/user`

**Summary:** Delete all memories for the current user from both the database and the vector store.

**Auth:** Verified user with `features.memories` permission

**Request**

No additional parameters.

**Response `200`**

```json
true
```

Returns `false` if no memories were found or deletion failed.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | `features.memories` permission denied |
| 404 | Memories feature disabled |

---

### POST `/api/v1/memories/{memory_id}/update`

**Summary:** Update the content of a specific memory and refresh its embedding vector.

**Auth:** Verified user with `features.memories` permission (must own the memory)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | memory_id | string | Yes | Memory UUID |
| Body | content | string | No | New memory text content |

```json
{
  "content": "User prefers numbered lists, not bullet points."
}
```

**Response `200`**

Updated `MemoryModel` object:

```json
{
  "id": "memory-uuid",
  "user_id": "user-uuid",
  "content": "User prefers numbered lists, not bullet points.",
  "updated_at": 1700000050,
  "created_at": 1699999000
}
```

**Implementation note:** If `content` is provided, the embedding is regenerated and upserted into the vector store. The DB session is not held during embedding generation.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | `features.memories` permission denied |
| 404 | Memories feature disabled, or memory not found |

---

### DELETE `/api/v1/memories/{memory_id}`

**Summary:** Delete a specific memory from both the database and the vector store.

**Auth:** Verified user with `features.memories` permission (must own the memory)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | memory_id | string | Yes | Memory UUID |

**Response `200`**

```json
true
```

Returns `false` if the memory was not found or not owned by the user.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | `features.memories` permission denied |
| 404 | Memories feature disabled |

---

*Total endpoints documented: 7*
