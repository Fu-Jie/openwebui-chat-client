# Users API Reference

Base path: `/api/v1/users`

---

### GET /api/v1/users/

**Summary:** Returns a paginated list of all users with their group memberships.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Query | query | string | No | Search string to filter users by name/email |
| Query | order_by | string | No | Field to sort by |
| Query | direction | string | No | Sort direction (`asc` or `desc`) |
| Query | page | integer | No | Page number (default `1`) |

**Response `200`**

```json
{
  "users": [
    {
      "id": "user_id",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "profile_image_url": "/api/v1/users/user_id/profile/image",
      "group_ids": ["group_id_1"],
      "last_active_at": 1700000000,
      "updated_at": 1700000000,
      "created_at": 1699000000
    }
  ],
  "total": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| users | array | List of user objects (UserGroupIdsModel) |
| users[].id | string | User ID |
| users[].email | string | User email |
| users[].name | string | Display name |
| users[].role | string | User role |
| users[].profile_image_url | string | Profile image path |
| users[].group_ids | array[string] | IDs of groups the user belongs to |
| users[].last_active_at | integer | Last active timestamp (epoch) |
| users[].updated_at | integer | Last update timestamp (epoch) |
| users[].created_at | integer | Creation timestamp (epoch) |
| total | integer | Total number of matching users |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/users/all

**Summary:** Returns all users without pagination (admin view).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
{
  "users": [
    {
      "id": "user_id",
      "name": "John Doe",
      "email": "user@example.com",
      "role": "user",
      "bio": null,
      "groups": [],
      "is_active": false,
      "status_emoji": null,
      "status_message": null,
      "status_expires_at": null
    }
  ],
  "total": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| users | array | List of UserInfoResponse objects |
| users[].id | string | User ID |
| users[].name | string | Display name |
| users[].email | string | User email |
| users[].role | string | User role |
| users[].bio | string \| null | User bio |
| users[].groups | array | Groups the user belongs to |
| users[].is_active | boolean | Whether the user is currently active |
| users[].status_emoji | string \| null | Status emoji |
| users[].status_message | string \| null | Status message |
| users[].status_expires_at | integer \| null | Status expiry (epoch) |
| total | integer | Total user count |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/users/search

**Summary:** Searches users with pagination (accessible to all verified users).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Query | query | string | No | Search string to filter users |
| Query | order_by | string | No | Field to sort by |
| Query | direction | string | No | Sort direction (`asc` or `desc`) |
| Query | page | integer | No | Page number (default `1`) |

**Response `200`**

```json
{
  "users": [
    {
      "id": "user_id",
      "name": "John Doe",
      "email": "user@example.com",
      "role": "user",
      "bio": null,
      "groups": [],
      "is_active": false
    }
  ],
  "total": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| users | array | List of UserInfoResponse objects |
| total | integer | Total matching user count |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/users/groups

**Summary:** Returns the groups the current session user belongs to.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
[
  {
    "id": "group_id",
    "user_id": "owner_id",
    "name": "Team Alpha",
    "description": "Alpha team group",
    "created_at": 1699000000,
    "updated_at": 1700000000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | array | List of GroupModel objects |
| [].id | string | Group ID |
| [].user_id | string | Group owner user ID |
| [].name | string | Group name |
| [].description | string | Group description |
| [].created_at | integer | Creation timestamp (epoch) |
| [].updated_at | integer | Last update timestamp (epoch) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/users/permissions

**Summary:** Returns the effective permissions for the current session user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
{
  "workspace": {
    "models": false,
    "knowledge": false
  },
  "chat": {
    "file_upload": true,
    "delete": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | object | Nested permission map derived from user role and group memberships |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/users/default/permissions

**Summary:** Returns the configured default permissions for all users.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
{
  "workspace": {
    "models": false,
    "knowledge": false,
    "prompts": false,
    "tools": false,
    "skills": false,
    "models_import": false,
    "models_export": false,
    "prompts_import": false,
    "prompts_export": false,
    "tools_import": false,
    "tools_export": false
  },
  "sharing": {
    "models": false,
    "public_models": false,
    "knowledge": false,
    "public_knowledge": false,
    "prompts": false,
    "public_prompts": false,
    "tools": false,
    "public_tools": true,
    "skills": false,
    "public_skills": false,
    "notes": false,
    "public_notes": true
  },
  "chat": {
    "controls": true,
    "valves": true,
    "system_prompt": true,
    "params": true,
    "file_upload": true,
    "web_upload": true,
    "delete": true,
    "delete_message": true,
    "continue_response": true,
    "regenerate_response": true,
    "rate_response": true,
    "edit": true,
    "share": true,
    "export": true,
    "stt": true,
    "tts": true,
    "call": true,
    "multiple_models": true,
    "temporary": true,
    "temporary_enforced": false
  },
  "features": {
    "api_keys": false,
    "notes": true,
    "channels": true,
    "folders": true,
    "direct_tool_servers": false,
    "web_search": true,
    "image_generation": true,
    "code_interpreter": true,
    "memories": true
  },
  "settings": {
    "interface": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| workspace | object | Workspace-level permissions |
| sharing | object | Sharing permissions |
| chat | object | Chat feature permissions |
| features | object | Feature access permissions |
| settings | object | Settings permissions |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/users/default/permissions

**Summary:** Updates the default permissions applied to all users.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | workspace | object | Yes | Workspace permission overrides |
| Body | sharing | object | Yes | Sharing permission overrides |
| Body | chat | object | Yes | Chat permission overrides |
| Body | features | object | Yes | Feature permission overrides |
| Body | settings | object | Yes | Settings permission overrides |

**Response `200`**

Returns the updated UserPermissions object (same schema as GET response).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/users/user/settings

**Summary:** Returns the UI settings for the current session user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
{
  "ui": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| ui | object \| null | UI settings dictionary |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |

---

### POST /api/v1/users/user/settings/update

**Summary:** Updates the UI settings for the current session user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | ui | object | No | UI settings dictionary (key `toolServers` removed if user lacks `direct_tool_servers` permission) |

**Response `200`**

```json
{
  "ui": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| ui | object \| null | Updated UI settings |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |

---

### GET /api/v1/users/user/status

**Summary:** Returns the presence status of the current session user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

Returns the full UserModel for the session user including all status fields.

```json
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "status_emoji": "😊",
  "status_message": "Available",
  "status_expires_at": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | User ID |
| status_emoji | string \| null | Status emoji |
| status_message | string \| null | Status message |
| status_expires_at | integer \| null | Status expiry (epoch) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |
| 403 | User status feature disabled |

---

### POST /api/v1/users/user/status/update

**Summary:** Updates the presence status of the current session user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | status_emoji | string | No | Status emoji |
| Body | status_message | string | No | Status message text |
| Body | status_expires_at | integer | No | Status expiry (epoch) |

**Response `200`**

Returns the updated UserModel (same schema as GET `/user/status`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |
| 403 | User status feature disabled |

---

### GET /api/v1/users/user/info

**Summary:** Returns the custom info dictionary for the current session user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
{
  "custom_key": "custom_value"
}
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | object \| null | Arbitrary key-value info dictionary |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |

---

### POST /api/v1/users/user/info/update

**Summary:** Merges new key-value pairs into the current session user's info dictionary.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | (any key) | any | Yes | Key-value pairs to merge into the user info dictionary |

**Response `200`**

```json
{
  "custom_key": "updated_value"
}
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | object | Updated info dictionary |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |

---

### GET /api/v1/users/{user_id}

**Summary:** Returns full user details including group memberships and active status (admin view).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | user_id | string | Yes | User ID, or `"shared-{chat_id}"` to resolve from a shared chat |

**Response `200`**

```json
{
  "id": "user_id",
  "name": "John Doe",
  "email": "user@example.com",
  "role": "user",
  "profile_image_url": "/api/v1/users/user_id/profile/image",
  "groups": [
    {"id": "group_id", "name": "Team Alpha"}
  ],
  "is_active": true,
  "status_emoji": null,
  "status_message": null,
  "status_expires_at": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | User ID |
| name | string | Display name |
| email | string | User email |
| role | string | User role |
| profile_image_url | string | Profile image path |
| groups | array | List of `{id, name}` objects |
| is_active | boolean | Whether the user is currently active |
| status_emoji | string \| null | Status emoji |
| status_message | string \| null | Status message |
| status_expires_at | integer \| null | Status expiry (epoch) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/users/{user_id}/info

**Summary:** Returns publicly visible user info including groups and active status.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | user_id | string | Yes | User ID |

**Response `200`**

```json
{
  "id": "user_id",
  "name": "John Doe",
  "email": "user@example.com",
  "role": "user",
  "bio": null,
  "groups": [
    {"id": "group_id", "name": "Team Alpha"}
  ],
  "is_active": false,
  "status_emoji": null,
  "status_message": null,
  "status_expires_at": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | User ID |
| name | string | Display name |
| email | string | User email |
| role | string | User role |
| bio | string \| null | User bio |
| groups | array | List of `{id, name}` objects |
| is_active | boolean | Whether the user is active |
| status_emoji | string \| null | Status emoji |
| status_message | string \| null | Status message |
| status_expires_at | integer \| null | Status expiry (epoch) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |

---

### GET /api/v1/users/{user_id}/oauth/sessions

**Summary:** Returns OAuth sessions associated with a user.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | user_id | string | Yes | User ID |

**Response `200`**

```json
[
  {
    "id": "session_id",
    "user_id": "user_id",
    "provider": "google",
    "token": {}
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | array | List of OAuth session objects |
| [].id | string | Session ID |
| [].user_id | string | Associated user ID |
| [].provider | string | OAuth provider name |
| [].token | object | Token data |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found or no sessions |
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/users/{user_id}/profile/image

**Summary:** Returns the profile image for a user (redirect, inline image, or default).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | user_id | string | Yes | User ID |

**Response `200`**

Image data stream, a `302` redirect to external URL, or the default `/static/user.png` file.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | User not found |
| 401 | Not authenticated |

---

### GET /api/v1/users/{user_id}/active

**Summary:** Returns whether a specific user is currently active.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | user_id | string | Yes | User ID |

**Response `200`**

```json
{
  "active": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| active | boolean | Whether the user is currently active |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/users/{user_id}/update

**Summary:** Updates a user's role, name, email, password, and profile image (admin only).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | user_id | string | Yes | User ID to update |
| Body | role | string | Yes | New role (`pending`, `user`, `admin`) |
| Body | name | string | Yes | New display name |
| Body | email | string | Yes | New email address |
| Body | profile_image_url | string | Yes | New profile image URL |
| Body | password | string | No | New password (if provided, must pass validation) |

**Response `200`**

```json
{
  "id": "user_id",
  "email": "new@example.com",
  "name": "Updated Name",
  "role": "user",
  "profile_image_url": "/api/v1/users/user_id/profile/image",
  "last_active_at": 1700000000,
  "updated_at": 1700000000,
  "created_at": 1699000000
}
```

Returns the full UserModel object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Email taken, password validation failed, or update failed |
| 401 | Not authenticated |
| 403 | Attempt to modify primary admin or insufficient permissions |
| 500 | Primary admin check failed |

---

### DELETE /api/v1/users/{user_id}

**Summary:** Deletes a user account by ID.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | user_id | string | Yes | User ID to delete |

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
| 401 | Not authenticated |
| 403 | Attempt to delete primary admin or self-deletion |
| 500 | Deletion failed or primary admin check error |

---

### GET /api/v1/users/{user_id}/groups

**Summary:** Returns the groups a specific user belongs to (admin view).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | user_id | string | Yes | User ID |

**Response `200`**

```json
[
  {
    "id": "group_id",
    "user_id": "owner_id",
    "name": "Team Alpha",
    "description": "Alpha team",
    "created_at": 1699000000,
    "updated_at": 1700000000
  }
]
```

Returns a list of GroupModel objects.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |
