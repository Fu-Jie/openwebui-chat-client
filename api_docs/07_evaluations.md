# Evaluations API

Base path: `/api/v1/evaluations`

Feedback and rating data for model responses. Includes per-user feedback, admin-wide views, a paginated list, and an Elo-based leaderboard.

---

### GET /api/v1/evaluations/leaderboard

**Summary:** Get the model Elo leaderboard computed from all feedback data.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | No | If provided, re-weights Elo ratings by semantic similarity to this topic (e.g. `"coding"`) |

**Response `200`**

```json
{
  "entries": [
    {
      "model_id": "llama3:8b",
      "rating": 1052,
      "won": 34,
      "lost": 18,
      "count": 52,
      "top_tags": [
        { "tag": "coding", "count": 12 },
        { "tag": "writing", "count": 8 }
      ]
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| entries | array | Ranked list of model entries |
| entries[].model_id | string | Model identifier |
| entries[].rating | integer | Elo rating (baseline 1000) |
| entries[].won | integer | Number of comparisons won |
| entries[].lost | integer | Number of comparisons lost |
| entries[].count | integer | Total comparisons (won + lost) |
| entries[].top_tags | array | Top conversation tags associated with this model |

**Elo Algorithm Notes**
- Each model starts at rating 1000. K-factor = 32.
- When a user selects a winner in arena mode (`rating=1`), the winner gains points and the loser loses points based on expected probability.
- When `query` is supplied, semantic similarity (via sentence-transformers embeddings) weights each feedback's contribution to the final rating.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/evaluations/leaderboard/{model_id}/history

**Summary:** Get daily win/loss history for a specific model.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| model_id | string | Model identifier |

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| days | integer | No | Number of history days to return (default: 30) |

**Response `200`**

```json
{
  "model_id": "llama3:8b",
  "history": [
    { "date": "2024-03-01", "won": 5, "lost": 2 },
    { "date": "2024-03-02", "won": 3, "lost": 4 }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| model_id | string | Model identifier |
| history | array | Daily win/loss entries |
| history[].date | string | ISO date string (`YYYY-MM-DD`) |
| history[].won | integer | Wins on that date |
| history[].lost | integer | Losses on that date |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 404 | Model not found in feedback data |

---

### GET /api/v1/evaluations/config

**Summary:** Get arena evaluation configuration.

**Auth:** Admin only

**Response `200`**

```json
{
  "ENABLE_EVALUATION_ARENA_MODELS": true,
  "EVALUATION_ARENA_MODELS": [
    { "model_id": "llama3:8b", "name": "Llama 3 8B" }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| ENABLE_EVALUATION_ARENA_MODELS | boolean | Whether arena mode is enabled |
| EVALUATION_ARENA_MODELS | array | Models available for arena comparison |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/evaluations/config

**Summary:** Update arena evaluation configuration.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | ENABLE_EVALUATION_ARENA_MODELS | boolean | No | Enable/disable arena mode |
| Body | EVALUATION_ARENA_MODELS | array | No | List of arena model objects |

**Response `200`** — same schema as GET `/evaluations/config`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 422 | Validation error |

---

### GET /api/v1/evaluations/feedbacks/all

**Summary:** Get all feedback records across all users (admin view).

**Auth:** Admin only

**Response `200`**

```json
[
  {
    "id": "fb-123",
    "user_id": "user-abc",
    "data": {
      "model_id": "llama3:8b",
      "rating": 1,
      "sibling_model_ids": ["mistral:7b"],
      "reason": "More accurate",
      "comment": "Clear and concise.",
      "tags": ["coding"]
    },
    "meta": {
      "chat_id": "chat-456",
      "message_id": "msg-789"
    },
    "snapshot": {},
    "created_at": 1710000000,
    "updated_at": 1710000001
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Feedback UUID |
| user_id | string | User who submitted the feedback |
| data.model_id | string | Model being rated |
| data.rating | integer | `1` = thumbs up / winner, `-1` = thumbs down / loser |
| data.sibling_model_ids | array[string] | Opponent model IDs (arena mode) |
| data.reason | string | Short reason category |
| data.comment | string | Free-text user comment |
| data.tags | array[string] | Conversation topic tags |
| meta.chat_id | string | Associated chat ID |
| meta.message_id | string | Associated message ID |
| snapshot | object | Message/context snapshot at feedback time |
| created_at | integer | Unix epoch creation timestamp |
| updated_at | integer | Unix epoch last-updated timestamp |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/evaluations/feedbacks/all/ids

**Summary:** Get all feedback IDs (lightweight admin list).

**Auth:** Admin only

**Response `200`**

```json
[
  { "id": "fb-123" },
  { "id": "fb-456" }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### DELETE /api/v1/evaluations/feedbacks/all

**Summary:** Delete all feedback records.

**Auth:** Admin only

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/evaluations/feedbacks/all/export

**Summary:** Export all feedbacks as a raw FeedbackModel list (includes full snapshot data).

**Auth:** Admin only

**Response `200`** — same schema as `GET /feedbacks/all` but uses `FeedbackModel` (includes all stored fields).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/evaluations/feedbacks/user

**Summary:** Get all feedback submitted by the current user.

**Auth:** Verified user

**Response `200`** — list of FeedbackUserResponse objects (same structure as admin feedbacks but scoped to current user).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### DELETE /api/v1/evaluations/feedbacks

**Summary:** Delete all feedback submitted by the current user.

**Auth:** Verified user

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/evaluations/feedbacks/list

**Summary:** Paginated admin list of all feedbacks with sorting.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| order_by | string | No | Sort field |
| direction | string | No | `asc` or `desc` |
| page | integer | No | Page number (default: 1, page size: 30) |

**Response `200`**

```json
{
  "items": [ { "...feedback fields..." } ],
  "total": 120
}
```

| Field | Type | Description |
|-------|------|-------------|
| items | array | List of feedback objects |
| total | integer | Total feedback count for pagination |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/evaluations/feedback

**Summary:** Create a new feedback record.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | data | object | Yes | Feedback payload (see structure below) |
| Body | data.model_id | string | Yes | Model being rated |
| Body | data.rating | integer | Yes | `1` (positive) or `-1` (negative) |
| Body | data.sibling_model_ids | array[string] | No | Competing model IDs in arena mode |
| Body | data.reason | string | No | Short reason category |
| Body | data.comment | string | No | Free-text comment |
| Body | data.tags | array[string] | No | Conversation topic tags |
| Body | meta | object | No | Context metadata (chat_id, message_id) |
| Body | snapshot | object | No | Snapshot of the message context |

**Response `200`** — created FeedbackModel.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Failed to create feedback |
| 401 | Not authenticated |

---

### GET /api/v1/evaluations/feedback/{id}

**Summary:** Get a specific feedback record by ID. Admin sees all; regular users see only their own.

**Auth:** Verified user

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Feedback UUID |

**Response `200`** — FeedbackModel.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 404 | Feedback not found |

---

### POST /api/v1/evaluations/feedback/{id}

**Summary:** Update an existing feedback record.

**Auth:** Verified user (own feedback; admin can update any)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Feedback UUID |

**Request** — same body schema as `POST /evaluations/feedback`.

**Response `200`** — updated FeedbackModel.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 404 | Feedback not found |

---

### DELETE /api/v1/evaluations/feedback/{id}

**Summary:** Delete a specific feedback record.

**Auth:** Verified user (own feedback; admin can delete any)

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Feedback UUID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 404 | Feedback not found |
