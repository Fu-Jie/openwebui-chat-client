# Channels API Reference

Base path: `/api/v1/channels`

All endpoints require channels to be globally enabled (`ENABLE_CHANNELS=true`). Most endpoints require the user to have the `features.channels` permission (or be admin).

---

## Channel Object Schemas

### `ChannelModel`

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique channel ID (UUID) |
| user_id | string | Owner/creator user ID |
| type | string \| null | Channel type: `null` = standard, `"group"` = private group, `"dm"` = direct message |
| name | string | Channel name (stored lowercase) |
| description | string \| null | Channel description |
| is_private | boolean \| null | Whether the channel is private (relevant for `group` type) |
| data | object \| null | Arbitrary channel data |
| meta | object \| null | Metadata |
| access_grants | array | List of `AccessGrantModel` objects controlling read/write permissions |
| created_at | integer | Creation timestamp (nanosecond epoch) |
| updated_at | integer | Last update timestamp (nanosecond epoch) |
| updated_by | string \| null | User ID who last updated |
| archived_at | integer \| null | Archive timestamp |
| archived_by | string \| null | User who archived |
| deleted_at | integer \| null | Soft-delete timestamp |
| deleted_by | string \| null | User who deleted |

### `AccessGrantModel`

| Field | Type | Description |
|-------|------|-------------|
| principal_type | string | `"user"` or `"group"` |
| principal_id | string | User/group ID, or `"*"` for public |
| permission | string | `"read"` or `"write"` |

### `MessageModel`

| Field | Type | Description |
|-------|------|-------------|
| id | string | Message UUID |
| user_id | string | Author user ID |
| channel_id | string \| null | Parent channel ID |
| reply_to_id | string \| null | ID of message this is quoting/replying to |
| parent_id | string \| null | Thread parent message ID |
| is_pinned | boolean | Whether message is pinned |
| pinned_by | string \| null | User ID who pinned |
| pinned_at | integer \| null | Pin timestamp (nanosecond epoch) |
| content | string | Message text content |
| data | object \| null | Attached files and other data |
| meta | object \| null | Metadata (e.g., `model_id`, `model_name`, `webhook`) |
| created_at | integer | Creation timestamp (nanosecond epoch) |
| updated_at | integer | Last update timestamp (nanosecond epoch) |

### `MessageForm` (request body for posting/updating messages)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| content | string | Yes | Message text |
| temp_id | string | No | Client-side temporary ID (echoed in Socket.IO event) |
| reply_to_id | string | No | Message ID being quoted |
| parent_id | string | No | Thread parent message ID |
| data | object | No | Attached files: `{"files": [{"id": "...", "type": "image", "url": "..."}]}` |
| meta | object | No | Extra metadata (e.g., `{"model_id": "gpt-4o"}`) |

### `ChannelWebhookModel`

| Field | Type | Description |
|-------|------|-------------|
| id | string | Webhook UUID |
| channel_id | string | Parent channel ID |
| user_id | string | Creator user ID |
| name | string | Display name for the webhook bot |
| profile_image_url | string \| null | Avatar URL or base64 data URI |
| token | string | Secret token used to authenticate webhook POSTs |
| last_used_at | integer \| null | Last use timestamp (nanosecond epoch) |
| created_at | integer | Creation timestamp (nanosecond epoch) |
| updated_at | integer | Last update timestamp (nanosecond epoch) |

---

## Socket.IO Real-Time Events

Channel endpoints emit events on the `events:channel` Socket.IO event to the room `channel:{channel_id}`.

**Event envelope:**

```json
{
  "channel_id": "channel-uuid",
  "message_id": "message-uuid",
  "data": {
    "type": "<event_type>",
    "data": { }
  },
  "user": { "id": "user-uuid", "name": "Alice", "role": "user" },
  "channel": { }
}
```

| `data.type` | Triggered by |
|-------------|-------------|
| `message` | New message posted |
| `message:reply` | New reply added to a thread (emitted to parent) |
| `message:update` | Message content updated |
| `message:delete` | Message deleted |
| `message:reaction:add` | Reaction added |
| `message:reaction:remove` | Reaction removed |

---

### GET `/api/v1/channels/`

**Summary:** List all channels the current user is a member of, with unread count and last message time.

**Auth:** Verified user with `features.channels` permission

**Request**

No additional parameters.

**Response `200`**

```json
[
  {
    "id": "channel-uuid",
    "user_id": "creator-uuid",
    "type": null,
    "name": "general",
    "description": "General discussion",
    "is_private": null,
    "data": null,
    "meta": null,
    "access_grants": [],
    "created_at": 1700000000000000000,
    "updated_at": 1700000000000000000,
    "updated_by": null,
    "archived_at": null,
    "archived_by": null,
    "deleted_at": null,
    "deleted_by": null,
    "user_ids": null,
    "users": null,
    "last_message_at": 1700000000000000000,
    "unread_count": 3
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| (all ChannelModel fields) | — | See ChannelModel schema |
| user_ids | array[string] \| null | Member user IDs (only for `dm` type channels) |
| users | array \| null | Member user objects with `is_active` (only for `dm` type channels) |
| last_message_at | integer \| null | Timestamp of last message (nanosecond epoch) |
| unread_count | integer | Number of unread messages since last read |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or channels feature disabled for user |
| 403 | Channels globally disabled |

---

### GET `/api/v1/channels/list`

**Summary:** List all channels — returns all channels for admins, or the user's accessible channels for regular users.

**Auth:** Verified user with `features.channels` permission

**Request**

No additional parameters.

**Response `200`**

Array of `ChannelModel` objects.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Channels globally disabled |

---

### GET `/api/v1/channels/users/{user_id}`

**Summary:** Get or create a DM channel between the current user and the specified user.

**Auth:** Verified user with `features.channels` permission

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | user_id | string | Yes | Target user UUID to DM |

**Response `200`**

`ChannelModel` object for the DM channel. Emits `channel:created` Socket.IO event to both participants.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error creating channel |
| 401 | Not authenticated |
| 403 | Channels globally disabled |

---

### POST `/api/v1/channels/create`

**Summary:** Create a new channel. Only admins can create standard channels; users can create `group` or `dm` channels.

**Auth:** Verified user (admin required for standard channel type)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | name | string | Yes | Channel name (will be stored lowercase) |
| Body | type | string | No | `null` = standard, `"group"`, `"dm"` |
| Body | description | string | No | Channel description |
| Body | is_private | boolean | No | Make channel private |
| Body | data | object | No | Custom channel data |
| Body | meta | object | No | Channel metadata |
| Body | access_grants | array | No | Array of access grant objects |
| Body | user_ids | array[string] | No | Initial member user IDs |
| Body | group_ids | array[string] | No | Group IDs to invite |

```json
{
  "name": "engineering",
  "type": null,
  "description": "Engineering team channel",
  "access_grants": [
    { "principal_type": "group", "principal_id": "eng-group-uuid", "permission": "read" },
    { "principal_type": "group", "principal_id": "eng-group-uuid", "permission": "write" }
  ]
}
```

**Response `200`**

`ChannelModel` object for the created channel. Emits `channel:created` Socket.IO event.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error creating channel |
| 401 | Not authenticated; or non-admin trying to create standard channel |
| 403 | Channels globally disabled |

---

### GET `/api/v1/channels/{id}`

**Summary:** Get a channel by ID with full details, write-access flag, and unread count.

**Auth:** Verified user with `features.channels` permission; must have read access

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |

**Response `200`**

```json
{
  "id": "channel-uuid",
  "user_id": "creator-uuid",
  "type": null,
  "name": "general",
  "description": "General discussion",
  "is_private": null,
  "data": null,
  "meta": null,
  "access_grants": [],
  "created_at": 1700000000000000000,
  "updated_at": 1700000000000000000,
  "updated_by": null,
  "archived_at": null,
  "archived_by": null,
  "deleted_at": null,
  "deleted_by": null,
  "is_manager": false,
  "write_access": true,
  "user_count": 42,
  "user_ids": null,
  "users": null,
  "last_read_at": 1700000000000000000,
  "unread_count": 0
}
```

| Field | Type | Description |
|-------|------|-------------|
| (all ChannelModel fields) | — | See ChannelModel schema |
| is_manager | boolean | Whether the current user is a channel manager |
| write_access | boolean | Whether the current user can post messages |
| user_count | integer | Number of users with read access |
| user_ids | array[string] \| null | Member IDs (for `group`/`dm` channels) |
| users | array \| null | Member user objects with `is_active` (for `group`/`dm` channels) |
| last_read_at | integer \| null | Last time current user read the channel |
| unread_count | integer | Unread message count |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | No read access or not a member (for group/dm) |
| 404 | Channel not found |

---

### GET `/api/v1/channels/{id}/members`

**Summary:** Get paginated list of members who have access to a channel.

**Auth:** Verified user with `features.channels` permission

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Query | query | string | No | Search by username |
| Query | order_by | string | No | Sort field |
| Query | direction | string | No | `asc` or `desc` |
| Query | page | integer | No | Page number (default: 1, 30 items/page) |

**Response `200`**

```json
{
  "users": [
    {
      "id": "user-uuid",
      "name": "Alice",
      "email": "alice@example.com",
      "role": "user",
      "profile_image_url": "/user.png",
      "is_active": true
    }
  ],
  "total": 42
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Not a member (for group/dm) |
| 404 | Channel not found |

---

### POST `/api/v1/channels/{id}/members/active`

**Summary:** Update the current user's active membership status in a channel (mark as active/inactive).

**Auth:** Verified user (must be a member of the channel)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Body | is_active | boolean | Yes | New active status |

```json
{
  "is_active": true
}
```

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 404 | Channel or membership not found |

---

### POST `/api/v1/channels/{id}/update/members/add`

**Summary:** Add users and/or group members to a channel (owner or admin only).

**Auth:** Verified user (must be channel owner or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Body | user_ids | array[string] | No | User IDs to add |
| Body | group_ids | array[string] | No | Group IDs whose members to add |

```json
{
  "user_ids": ["user-uuid-1", "user-uuid-2"],
  "group_ids": ["group-uuid-1"]
}
```

**Response `200`**

Array of `ChannelMemberModel` objects for newly added members.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |
| 403 | Not owner or admin |
| 404 | Channel not found |

---

### POST `/api/v1/channels/{id}/update/members/remove`

**Summary:** Remove users from a channel (owner or admin only).

**Auth:** Verified user (must be channel owner or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Body | user_ids | array[string] | Yes | User IDs to remove |

```json
{
  "user_ids": ["user-uuid-1"]
}
```

**Response `200`**

Number of deleted membership records (integer).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |
| 403 | Not owner or admin |
| 404 | Channel not found |

---

### POST `/api/v1/channels/{id}/update`

**Summary:** Update a channel's settings (owner or admin only).

**Auth:** Verified user (must be channel owner or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Body | name | string | No | New channel name |
| Body | description | string | No | New description |
| Body | is_private | boolean | No | Privacy setting |
| Body | data | object | No | Custom data |
| Body | meta | object | No | Metadata |
| Body | access_grants | array | No | New access grants list (replaces existing) |
| Body | group_ids | array[string] | No | Group IDs |
| Body | user_ids | array[string] | No | User IDs |

```json
{
  "name": "engineering-v2",
  "description": "Updated description"
}
```

**Response `200`**

Updated `ChannelModel` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |
| 403 | Not owner or admin |
| 404 | Channel not found |

---

### DELETE `/api/v1/channels/{id}/delete`

**Summary:** Delete a channel permanently (owner or admin only).

**Auth:** Verified user (must be channel owner or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |
| 403 | Not owner or admin |
| 404 | Channel not found |

---

### GET `/api/v1/channels/{id}/messages`

**Summary:** Get paginated messages for a channel, including reply counts and reactions.

**Auth:** Verified user (must have read access; for standard channels, joining is automatic)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Query | skip | integer | No | Offset (default: 0) |
| Query | limit | integer | No | Max messages to return (default: 50) |

**Response `200`**

```json
[
  {
    "id": "msg-uuid",
    "user_id": "user-uuid",
    "channel_id": "channel-uuid",
    "reply_to_id": null,
    "parent_id": null,
    "is_pinned": false,
    "pinned_by": null,
    "pinned_at": null,
    "content": "Hello channel!",
    "data": null,
    "meta": null,
    "created_at": 1700000000000000000,
    "updated_at": 1700000000000000000,
    "user": { "id": "user-uuid", "name": "Alice", "role": "user" },
    "reply_count": 2,
    "latest_reply_at": 1700000010000000000,
    "reactions": [
      { "name": "👍", "users": [{"id": "user-uuid", "name": "Bob"}], "count": 1 }
    ],
    "data": false
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| (all MessageModel fields) | — | See MessageModel schema |
| user | object \| null | Author info (`id`, `name`, `role`) |
| reply_count | integer | Number of thread replies |
| latest_reply_at | integer \| null | Timestamp of most recent reply |
| reactions | array | Emoji reactions (name, users array, count) |
| data | boolean | `true` if the message has attached file data, `false` otherwise |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | No read access |
| 404 | Channel not found |

---

### GET `/api/v1/channels/{id}/messages/pinned`

**Summary:** Get paginated pinned messages for a channel.

**Auth:** Verified user (must have read access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Query | page | integer | No | Page number (default: 1, 20 items/page) |

**Response `200`**

Array of `MessageWithReactionsResponse` objects (same as messages response but without reply metadata).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | No read access |
| 404 | Channel not found |

---

### POST `/api/v1/channels/{id}/messages/post`

**Summary:** Post a new message to a channel; triggers model responses for @-mentions and sends background notifications.

**Auth:** Verified user (must have write access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Body | content | string | Yes | Message text |
| Body | temp_id | string | No | Client temporary ID (echoed in Socket.IO event) |
| Body | reply_to_id | string | No | Message ID being quoted |
| Body | parent_id | string | No | Thread parent message ID (for threaded replies) |
| Body | data | object | No | File attachments: `{"files": [...]}` |
| Body | meta | object | No | Extra metadata |

```json
{
  "content": "Hello @gpt-4o, summarize this thread.",
  "temp_id": "client-temp-123",
  "parent_id": null,
  "data": {
    "files": [
      { "id": "file-uuid", "type": "image", "url": "data:image/png;base64,..." }
    ]
  }
}
```

**Response `200`**

`MessageModel` of the newly created message. Also emits `events:channel` Socket.IO event with type `message` to `channel:{id}`.

If the message contains an @-mention of a model, a model response is generated asynchronously in the background.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |
| 403 | No write access |
| 404 | Channel not found |

---

### GET `/api/v1/channels/{id}/messages/{message_id}`

**Summary:** Get a single message by ID within a channel.

**Auth:** Verified user (must have read access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | message_id | string | Yes | Message UUID |

**Response `200`**

```json
{
  "id": "msg-uuid",
  "user_id": "user-uuid",
  "channel_id": "channel-uuid",
  "reply_to_id": null,
  "parent_id": null,
  "is_pinned": false,
  "pinned_by": null,
  "pinned_at": null,
  "content": "Hello!",
  "data": null,
  "meta": null,
  "created_at": 1700000000000000000,
  "updated_at": 1700000000000000000,
  "user": { "id": "user-uuid", "name": "Alice", "role": "user" },
  "reply_to_message": null,
  "latest_reply_at": null,
  "reply_count": 0,
  "reactions": []
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Message belongs to different channel |
| 401 | Not authenticated |
| 403 | No read access |
| 404 | Channel or message not found |

---

### GET `/api/v1/channels/{id}/messages/{message_id}/data`

**Summary:** Get only the `data` field (file attachments) of a specific message.

**Auth:** Verified user (must have read access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | message_id | string | Yes | Message UUID |

**Response `200`**

```json
{
  "files": [
    { "id": "file-uuid", "type": "image", "url": "...", "content_type": "image/png" }
  ]
}
```

Returns `null` if the message has no data.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Message belongs to different channel |
| 401 | Not authenticated |
| 403 | No read access |
| 404 | Channel or message not found |

---

### POST `/api/v1/channels/{id}/messages/{message_id}/pin`

**Summary:** Pin or unpin a message in a channel.

**Auth:** Verified user (must have read access; admin or manager recommended)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | message_id | string | Yes | Message UUID |
| Body | is_pinned | boolean | Yes | `true` to pin, `false` to unpin |

```json
{
  "is_pinned": true
}
```

**Response `200`**

Updated `MessageUserResponse` object with `is_pinned`, `pinned_at`, `pinned_by` set.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request or message/channel mismatch |
| 401 | Not authenticated |
| 403 | No read access |
| 404 | Channel or message not found |

---

### GET `/api/v1/channels/{id}/messages/{message_id}/thread`

**Summary:** Get paginated thread replies to a specific (parent) message.

**Auth:** Verified user (must have read access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | message_id | string | Yes | Thread parent message UUID |
| Query | skip | integer | No | Offset (default: 0) |
| Query | limit | integer | No | Max results (default: 50) |

**Response `200`**

Array of `MessageUserResponse` objects (same structure as channel messages, but `reply_count` is always 0 for thread replies).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | No read access |
| 404 | Channel not found |

---

### POST `/api/v1/channels/{id}/messages/{message_id}/update`

**Summary:** Update a message's content or metadata.

**Auth:** Verified user (message author, admin, or user with channel read access for standard channels)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | message_id | string | Yes | Message UUID |
| Body | content | string | Yes | New message content |
| Body | temp_id | string | No | Temporary ID |
| Body | reply_to_id | string | No | Updated reply-to reference |
| Body | parent_id | string | No | Updated thread parent |
| Body | data | object | No | Updated file data |
| Body | meta | object | No | Updated metadata |

```json
{
  "content": "Edited message content",
  "meta": { "done": true }
}
```

**Response `200`**

Updated `MessageModel` object. Also emits `events:channel` Socket.IO event with type `message:update`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request or message/channel mismatch |
| 401 | Not authenticated |
| 403 | No write access |
| 404 | Channel or message not found |

---

### POST `/api/v1/channels/{id}/messages/{message_id}/reactions/add`

**Summary:** Add an emoji reaction to a message.

**Auth:** Verified user (must have write access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | message_id | string | Yes | Message UUID |
| Body | name | string | Yes | Emoji or reaction name (e.g., `"👍"`) |

```json
{
  "name": "👍"
}
```

**Response `200`**

```json
true
```

Also emits `events:channel` Socket.IO event with type `message:reaction:add`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |
| 403 | No write access |
| 404 | Channel or message not found |

---

### POST `/api/v1/channels/{id}/messages/{message_id}/reactions/remove`

**Summary:** Remove an emoji reaction from a message.

**Auth:** Verified user (must have write access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | message_id | string | Yes | Message UUID |
| Body | name | string | Yes | Emoji or reaction name to remove |

```json
{
  "name": "👍"
}
```

**Response `200`**

```json
true
```

Also emits `events:channel` Socket.IO event with type `message:reaction:remove`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request |
| 401 | Not authenticated |
| 403 | No write access |
| 404 | Channel or message not found |

---

### DELETE `/api/v1/channels/{id}/messages/{message_id}/delete`

**Summary:** Delete a message from a channel.

**Auth:** Verified user (message author or admin; for standard channels, write access required)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | message_id | string | Yes | Message UUID |

**Response `200`**

```json
true
```

Also emits `events:channel` Socket.IO event with type `message:delete`. If the message was a thread reply, also emits `message:reply` to the parent.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Message belongs to different channel |
| 401 | Not authenticated |
| 403 | No write access |
| 404 | Channel or message not found |

---

## Webhook Endpoints

### GET `/api/v1/channels/webhooks/{webhook_id}/profile/image`

**Summary:** Get the profile image for a webhook; redirects to URL or streams base64 image. Falls back to the default favicon.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | webhook_id | string | Yes | Webhook UUID |

**Response `200`**

- Image file stream (PNG/JPEG), or
- HTTP 302 redirect to the webhook's `profile_image_url`, or
- Default `favicon.png`

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET `/api/v1/channels/{id}/webhooks`

**Summary:** List all webhooks for a channel (channel managers and admins only).

**Auth:** Verified user (must be channel manager or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |

**Response `200`**

Array of `ChannelWebhookModel` objects.

```json
[
  {
    "id": "webhook-uuid",
    "channel_id": "channel-uuid",
    "user_id": "creator-uuid",
    "name": "CI Bot",
    "profile_image_url": null,
    "token": "secret-token",
    "last_used_at": null,
    "created_at": 1700000000000000000,
    "updated_at": 1700000000000000000
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Not channel manager or admin |
| 404 | Channel not found |

---

### POST `/api/v1/channels/{id}/webhooks/create`

**Summary:** Create a new webhook for a channel (channel managers and admins only).

**Auth:** Verified user (must be channel manager or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Body | name | string | Yes | Display name for the webhook bot |
| Body | profile_image_url | string | No | Avatar URL or base64 data URI |

```json
{
  "name": "CI Bot",
  "profile_image_url": null
}
```

**Response `200`**

`ChannelWebhookModel` object (includes the generated `token`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Creation failed |
| 401 | Not authenticated |
| 403 | Not channel manager or admin |
| 404 | Channel not found |

---

### POST `/api/v1/channels/{id}/webhooks/{webhook_id}/update`

**Summary:** Update a channel webhook's name or profile image (channel managers and admins only).

**Auth:** Verified user (must be channel manager or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | webhook_id | string | Yes | Webhook UUID |
| Body | name | string | Yes | New display name |
| Body | profile_image_url | string | No | New avatar URL or base64 data URI |

```json
{
  "name": "Updated CI Bot",
  "profile_image_url": "https://example.com/bot.png"
}
```

**Response `200`**

Updated `ChannelWebhookModel` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Update failed |
| 401 | Not authenticated |
| 403 | Not channel manager or admin |
| 404 | Channel or webhook not found |

---

### DELETE `/api/v1/channels/{id}/webhooks/{webhook_id}/delete`

**Summary:** Delete a channel webhook (channel managers and admins only).

**Auth:** Verified user (must be channel manager or admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | id | string | Yes | Channel UUID |
| Path | webhook_id | string | Yes | Webhook UUID |

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Not channel manager or admin |
| 404 | Channel or webhook not found |

---

### POST `/api/v1/channels/webhooks/{webhook_id}/{token}`

**Summary:** Public endpoint — post a message to a channel via webhook (no user authentication required).

**Auth:** Public (validated by webhook ID + secret token in URL)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | webhook_id | string | Yes | Webhook UUID |
| Path | token | string | Yes | Webhook secret token |
| Body | content | string | Yes | Message text to post |

```json
{
  "content": "Build #42 passed ✅"
}
```

**Response `200`**

```json
{
  "success": true,
  "message_id": "msg-uuid"
}
```

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | `true` on success |
| message_id | string | UUID of the newly created message |

Also emits `events:channel` Socket.IO event with type `message` to `channel:{channel_id}`. The `user` field in the event shows the webhook's identity (`role: "webhook"`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Message creation failed |
| 401 | Invalid webhook URL (wrong ID or token) |
| 403 | Channels globally disabled |
| 404 | Channel not found |

---

*Total endpoints documented: 28*
