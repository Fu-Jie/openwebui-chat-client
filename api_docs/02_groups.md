# Groups API Reference

Base path: `/api/v1/groups`

---

### GET /api/v1/groups/

**Summary:** Returns groups visible to the current user (all groups for admins, member-only groups for regular users).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Query | share | boolean | No | Filter by share setting; admins ignore this filter |

**Response `200`**

```json
[
  {
    "id": "group_id",
    "user_id": "owner_id",
    "name": "Team Alpha",
    "description": "Alpha team group",
    "data": null,
    "meta": null,
    "permissions": null,
    "member_count": 5,
    "created_at": 1699000000,
    "updated_at": 1700000000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | array | List of GroupResponse objects |
| [].id | string | Group ID |
| [].user_id | string | Group owner user ID |
| [].name | string | Group name |
| [].description | string | Group description |
| [].data | object \| null | Arbitrary group data (includes `config.share` key) |
| [].meta | object \| null | Arbitrary group metadata |
| [].permissions | object \| null | Group permission overrides |
| [].member_count | integer \| null | Number of members in the group |
| [].created_at | integer | Creation timestamp (epoch) |
| [].updated_at | integer | Last update timestamp (epoch) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/groups/create

**Summary:** Creates a new group.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | name | string | Yes | Group name |
| Body | description | string | Yes | Group description |
| Body | permissions | object | No | Permission overrides for the group |
| Body | data | object | No | Arbitrary group data |

**Response `200`**

```json
{
  "id": "group_id",
  "user_id": "owner_id",
  "name": "Team Alpha",
  "description": "Alpha team group",
  "data": null,
  "meta": null,
  "permissions": null,
  "member_count": 0,
  "created_at": 1699000000,
  "updated_at": 1699000000
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | New group ID (UUID) |
| user_id | string | Group owner user ID |
| name | string | Group name |
| description | string | Group description |
| data | object \| null | Group data |
| meta | object \| null | Group metadata |
| permissions | object \| null | Group permission overrides |
| member_count | integer \| null | Member count (0 for new group) |
| created_at | integer | Creation timestamp (epoch) |
| updated_at | integer | Last update timestamp (epoch) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error creating group |
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/groups/id/{id}

**Summary:** Returns full group details by ID (admin view).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | id | string | Yes | Group ID |

**Response `200`**

```json
{
  "id": "group_id",
  "user_id": "owner_id",
  "name": "Team Alpha",
  "description": "Alpha team group",
  "data": null,
  "meta": null,
  "permissions": null,
  "member_count": 5,
  "created_at": 1699000000,
  "updated_at": 1700000000
}
```

Returns a GroupResponse object (same schema as GET `/`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Group not found or not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/groups/id/{id}/info

**Summary:** Returns limited group info (name, description, member count) for verified users.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | id | string | Yes | Group ID |

**Response `200`**

```json
{
  "id": "group_id",
  "user_id": "owner_id",
  "name": "Team Alpha",
  "description": "Alpha team group",
  "member_count": 5,
  "created_at": 1699000000,
  "updated_at": 1700000000
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Group ID |
| user_id | string | Group owner user ID |
| name | string | Group name |
| description | string | Group description |
| member_count | integer \| null | Number of members |
| created_at | integer | Creation timestamp (epoch) |
| updated_at | integer | Last update timestamp (epoch) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Group not found or not authenticated |

---

### GET /api/v1/groups/id/{id}/export

**Summary:** Exports full group data including member user IDs.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | id | string | Yes | Group ID |

**Response `200`**

```json
{
  "id": "group_id",
  "user_id": "owner_id",
  "name": "Team Alpha",
  "description": "Alpha team group",
  "data": null,
  "meta": null,
  "permissions": null,
  "member_count": 2,
  "user_ids": ["user_id_1", "user_id_2"],
  "created_at": 1699000000,
  "updated_at": 1700000000
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Group ID |
| user_id | string | Group owner user ID |
| name | string | Group name |
| description | string | Group description |
| data | object \| null | Group data |
| meta | object \| null | Group metadata |
| permissions | object \| null | Group permission overrides |
| member_count | integer \| null | Number of members |
| user_ids | array[string] | List of member user IDs |
| created_at | integer | Creation timestamp (epoch) |
| updated_at | integer | Last update timestamp (epoch) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Group not found or not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/groups/id/{id}/users

**Summary:** Returns the list of users belonging to a group.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | id | string | Yes | Group ID |

*No request body.*

**Response `200`**

```json
[
  {
    "id": "user_id",
    "name": "John Doe",
    "email": "user@example.com",
    "role": "user",
    "bio": null,
    "groups": [],
    "is_active": false
  }
]
```

Returns a list of UserInfoResponse objects.

| Field | Type | Description |
|-------|------|-------------|
| (root) | array | List of UserInfoResponse objects |
| [].id | string | User ID |
| [].name | string | Display name |
| [].email | string | User email |
| [].role | string | User role |
| [].bio | string \| null | User bio |
| [].groups | array | Groups the user belongs to |
| [].is_active | boolean | Whether user is active |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error fetching users |
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/groups/id/{id}/update

**Summary:** Updates a group's name, description, permissions, and data.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | id | string | Yes | Group ID |
| Body | name | string | Yes | New group name |
| Body | description | string | Yes | New group description |
| Body | permissions | object | No | Permission overrides |
| Body | data | object | No | Arbitrary group data |

**Response `200`**

Returns the updated GroupResponse object (same schema as GET `/id/{id}`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error updating group |
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/groups/id/{id}/users/add

**Summary:** Adds one or more users to a group.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | id | string | Yes | Group ID |
| Body | user_ids | array[string] | No | List of user IDs to add (invalid IDs are filtered out) |

**Response `200`**

Returns the updated GroupResponse object (same schema as GET `/id/{id}`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error adding users to group |
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/groups/id/{id}/users/remove

**Summary:** Removes one or more users from a group.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | id | string | Yes | Group ID |
| Body | user_ids | array[string] | No | List of user IDs to remove |

**Response `200`**

Returns the updated GroupResponse object (same schema as GET `/id/{id}`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error removing users from group |
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### DELETE /api/v1/groups/id/{id}/delete

**Summary:** Deletes a group by ID.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Path | id | string | Yes | Group ID |

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
| 400 | Error deleting group |
| 401 | Not authenticated |
| 403 | Insufficient permissions |
