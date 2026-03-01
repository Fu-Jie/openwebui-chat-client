# Analytics API

Base path: `/api/v1/analytics`

Usage statistics endpoints for the admin dashboard. All endpoints require **Admin** authentication.

---

### GET /api/v1/analytics/models

**Summary:** Get message counts per model, sorted descending.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start_date | integer | No | Start of range as Unix epoch (inclusive) |
| end_date | integer | No | End of range as Unix epoch (inclusive) |
| group_id | string | No | Filter to messages from users in this group |

**Response `200`**

```json
{
  "models": [
    { "model_id": "llama3:8b", "count": 1024 },
    { "model_id": "mistral:7b", "count": 512 }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| models | array | List of model analytics entries sorted by count (desc) |
| models[].model_id | string | Model identifier |
| models[].count | integer | Total messages sent using this model |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/analytics/users

**Summary:** Get message counts and token usage per user.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start_date | integer | No | Start timestamp (Unix epoch) |
| end_date | integer | No | End timestamp (Unix epoch) |
| group_id | string | No | Filter to members of this group |
| limit | integer | No | Max users to return (default: 50) |

**Response `200`**

```json
{
  "users": [
    {
      "user_id": "user-abc",
      "name": "Alice",
      "email": "alice@example.com",
      "count": 320,
      "input_tokens": 45000,
      "output_tokens": 92000,
      "total_tokens": 137000
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| users | array | User analytics entries sorted by message count (desc) |
| users[].user_id | string | User identifier |
| users[].name | string\|null | User display name |
| users[].email | string\|null | User email |
| users[].count | integer | Total messages sent |
| users[].input_tokens | integer | Total input/prompt tokens consumed |
| users[].output_tokens | integer | Total output/completion tokens generated |
| users[].total_tokens | integer | Sum of input and output tokens |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/analytics/messages

**Summary:** Query raw chat messages with filters. At least one filter (model_id, user_id, or chat_id) is required; returns empty list otherwise.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| model_id | string | No* | Filter by model ID |
| user_id | string | No* | Filter by user ID |
| chat_id | string | No* | Filter by chat ID (returns all messages in that chat) |
| start_date | integer | No | Start timestamp (Unix epoch) |
| end_date | integer | No | End timestamp (Unix epoch) |
| skip | integer | No | Pagination offset (default: 0) |
| limit | integer | No | Results per page (default: 50, max: 100) |

\* At least one of `model_id`, `user_id`, or `chat_id` should be specified.

**Response `200`**

```json
[
  {
    "id": "msg-123",
    "chat_id": "chat-456",
    "user_id": "user-abc",
    "model": "llama3:8b",
    "role": "assistant",
    "content": "...",
    "created_at": 1710000000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Message UUID |
| chat_id | string | Parent chat UUID |
| user_id | string | User who sent/received the message |
| model | string | Model ID used for this message |
| role | string | `user` or `assistant` |
| content | string | Message text content |
| created_at | integer | Unix epoch creation timestamp |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/analytics/summary

**Summary:** Get high-level dashboard summary statistics.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start_date | integer | No | Start timestamp (Unix epoch) |
| end_date | integer | No | End timestamp (Unix epoch) |
| group_id | string | No | Filter to messages from users in this group |

**Response `200`**

```json
{
  "total_messages": 5120,
  "total_chats": 810,
  "total_models": 6,
  "total_users": 42
}
```

| Field | Type | Description |
|-------|------|-------------|
| total_messages | integer | Total message count in the period |
| total_chats | integer | Distinct chats with at least one message |
| total_models | integer | Distinct models used |
| total_users | integer | Distinct users who sent messages |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/analytics/daily

**Summary:** Get time-series message counts grouped by model (for charts).

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start_date | integer | No | Start timestamp (Unix epoch) |
| end_date | integer | No | End timestamp (Unix epoch) |
| group_id | string | No | Filter to group members |
| granularity | string | No | `"daily"` (default) or `"hourly"` |

**Response `200`**

```json
{
  "data": [
    {
      "date": "2024-03-01",
      "models": {
        "llama3:8b": 82,
        "mistral:7b": 34
      }
    },
    {
      "date": "2024-03-02",
      "models": {
        "llama3:8b": 91,
        "mistral:7b": 27
      }
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| data | array | Time-series entries sorted by date ascending |
| data[].date | string | Date label (`YYYY-MM-DD` for daily, `YYYY-MM-DD HH:00` for hourly) |
| data[].models | object | Map of `model_id → message_count` for that period |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/analytics/tokens

**Summary:** Get token usage aggregated by model.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start_date | integer | No | Start timestamp (Unix epoch) |
| end_date | integer | No | End timestamp (Unix epoch) |
| group_id | string | No | Filter to group members |

**Response `200`**

```json
{
  "models": [
    {
      "model_id": "llama3:8b",
      "input_tokens": 520000,
      "output_tokens": 980000,
      "total_tokens": 1500000,
      "message_count": 2048
    }
  ],
  "total_input_tokens": 600000,
  "total_output_tokens": 1100000,
  "total_tokens": 1700000
}
```

| Field | Type | Description |
|-------|------|-------------|
| models | array | Per-model token usage, sorted by total_tokens (desc) |
| models[].model_id | string | Model identifier |
| models[].input_tokens | integer | Prompt tokens consumed |
| models[].output_tokens | integer | Completion tokens generated |
| models[].total_tokens | integer | Total tokens |
| models[].message_count | integer | Message count for this model |
| total_input_tokens | integer | Sum of input tokens across all models |
| total_output_tokens | integer | Sum of output tokens across all models |
| total_tokens | integer | Grand total tokens |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/analytics/models/{model_id}/chats

**Summary:** Get chats that used a specific model, with first-message preview.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| model_id | string | Model identifier |

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start_date | integer | No | Start timestamp (Unix epoch) |
| end_date | integer | No | End timestamp (Unix epoch) |
| skip | integer | No | Pagination offset (default: 0) |
| limit | integer | No | Max results (default: 50, max: 100) |

**Response `200`**

```json
{
  "chats": [
    {
      "chat_id": "chat-456",
      "user_id": "user-abc",
      "user_name": "Alice",
      "first_message": "Can you help me debug this Python script?",
      "updated_at": 1710000100
    }
  ],
  "total": 38
}
```

| Field | Type | Description |
|-------|------|-------------|
| chats | array | List of chat preview entries |
| chats[].chat_id | string | Chat UUID |
| chats[].user_id | string\|null | User who started the chat |
| chats[].user_name | string\|null | Display name of the user |
| chats[].first_message | string\|null | First 200 characters of the first user message |
| chats[].updated_at | integer | Unix epoch of the most recent message |
| total | integer | Total matching chat count |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/analytics/models/{model_id}/overview

**Summary:** Get a model's feedback history (win/loss per day) and top conversation tags.

**Auth:** Admin only

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| model_id | string | Model identifier |

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| days | integer | No | Number of history days (default: 30; `0` = all time) |

**Response `200`**

```json
{
  "history": [
    { "date": "2024-03-01", "won": 4, "lost": 1 },
    { "date": "2024-03-02", "won": 6, "lost": 3 }
  ],
  "tags": [
    { "tag": "coding", "count": 18 },
    { "tag": "writing", "count": 9 }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| history | array | Daily win/loss from feedback data |
| history[].date | string | ISO date (`YYYY-MM-DD`) |
| history[].won | integer | Positive feedback count |
| history[].lost | integer | Negative feedback count |
| tags | array | Top 10 conversation tags from chats using this model |
| tags[].tag | string | Tag label |
| tags[].count | integer | Number of chats tagged with this label |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
