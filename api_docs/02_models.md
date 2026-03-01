# Models API Reference

Base path: `/api/v1/models`

---

### GET /api/v1/models/list

**Summary:** Returns a paginated list of models accessible to the current user with read/write access flags.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Query | query | string | No | Search string to filter models by name |
| Query | view_option | string | No | View filter option |
| Query | tag | string | No | Filter by model tag name |
| Query | order_by | string | No | Field to sort by |
| Query | direction | string | No | Sort direction (`asc` or `desc`) |
| Query | page | integer | No | Page number (default `1`) |

**Response `200`**

```json
{
  "items": [
    {
      "id": "my-model",
      "user_id": "user_id",
      "base_model_id": "llama3",
      "name": "My Custom Model",
      "params": {},
      "meta": {
        "profile_image_url": "/static/favicon.png",
        "description": "A custom model",
        "capabilities": null
      },
      "access_grants": [],
      "is_active": true,
      "updated_at": 1700000000,
      "created_at": 1699000000,
      "user": {
        "id": "user_id",
        "name": "John Doe",
        "role": "user",
        "email": "user@example.com"
      },
      "write_access": true
    }
  ],
  "total": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| items | array | List of ModelAccessResponse objects |
| items[].id | string | Model ID |
| items[].user_id | string | Owner user ID |
| items[].base_model_id | string \| null | Base model ID for proxying |
| items[].name | string | Display name |
| items[].params | object | Model parameters (arbitrary extra fields allowed) |
| items[].meta.profile_image_url | string \| null | Profile image URL |
| items[].meta.description | string \| null | User-facing model description |
| items[].meta.capabilities | object \| null | Model capability flags |
| items[].access_grants | array | Access grant entries |
| items[].is_active | boolean | Whether the model is active |
| items[].updated_at | integer | Last update timestamp (epoch) |
| items[].created_at | integer | Creation timestamp (epoch) |
| items[].user | object \| null | Owner user summary (`id`, `name`, `role`, `email`) |
| items[].write_access | boolean | Whether the current user can write/modify this model |
| total | integer | Total number of matching models |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/models/base

**Summary:** Returns all base (non-custom) models.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
[
  {
    "id": "llama3",
    "user_id": "system",
    "base_model_id": null,
    "name": "LLaMA 3",
    "params": {},
    "meta": {
      "profile_image_url": "/static/favicon.png",
      "description": null,
      "capabilities": null
    },
    "access_grants": [],
    "is_active": true,
    "updated_at": 1700000000,
    "created_at": 1699000000
  }
]
```

Returns a list of ModelResponse objects (same schema as items in `/list` minus `user` and `write_access`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/models/tags

**Summary:** Returns all unique tag names across models accessible to the current user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
["coding", "general", "vision"]
```

| Field | Type | Description |
|-------|------|-------------|
| (root) | array[string] | Sorted list of unique tag names |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/models/create

**Summary:** Creates a new custom model entry.

**Auth:** Verified user (requires `workspace.models` permission if not admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | id | string | Yes | Model ID (max 256 chars; used as API identifier) |
| Body | name | string | Yes | Display name |
| Body | meta | object | Yes | Model metadata (`profile_image_url`, `description`, `capabilities`) |
| Body | params | object | Yes | Model parameters (arbitrary key-value pairs) |
| Body | base_model_id | string | No | Base model ID for proxying |
| Body | access_grants | array[object] | No | Initial access grants |
| Body | is_active | boolean | No | Whether model is active (default `true`) |

**Response `200`**

```json
{
  "id": "my-model",
  "user_id": "user_id",
  "base_model_id": null,
  "name": "My Custom Model",
  "params": {},
  "meta": {
    "profile_image_url": "/static/favicon.png",
    "description": null,
    "capabilities": null
  },
  "access_grants": [],
  "is_active": true,
  "updated_at": 1700000000,
  "created_at": 1700000000
}
```

Returns a ModelModel object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Model ID too long |
| 401 | Not authenticated or model ID already taken |
| 403 | No permission to create models (non-admin without `workspace.models` permission) |

---

### GET /api/v1/models/export

**Summary:** Exports all models accessible to the current user as a JSON list.

**Auth:** Verified user (requires `workspace.models_export` permission if not admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
[
  {
    "id": "my-model",
    "user_id": "user_id",
    "base_model_id": null,
    "name": "My Custom Model",
    "params": {},
    "meta": {},
    "access_grants": [],
    "is_active": true,
    "updated_at": 1700000000,
    "created_at": 1699000000
  }
]
```

Returns a list of ModelModel objects.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or insufficient permissions |

---

### POST /api/v1/models/import

**Summary:** Imports a list of models, creating new ones or updating existing ones.

**Auth:** Verified user (requires `workspace.models_import` permission if not admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | models | array[object] | Yes | List of model data objects to import; each must have `id` (max 256 chars) |

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
| 400 | Invalid JSON format or import error |
| 401 | Not authenticated or insufficient permissions |
| 500 | Internal server error |

---

### POST /api/v1/models/sync

**Summary:** Synchronizes the database models with a provided list (admin only).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | models | array[object] | No | List of ModelModel objects to sync (default `[]`) |

**Response `200`**

```json
[
  {
    "id": "my-model",
    "user_id": "user_id",
    "name": "My Custom Model",
    "params": {},
    "meta": {},
    "access_grants": [],
    "is_active": true,
    "updated_at": 1700000000,
    "created_at": 1699000000
  }
]
```

Returns the list of synchronized ModelModel objects.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/models/model

**Summary:** Returns a single model by ID with read/write access flags.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Query | id | string | Yes | Model ID (query param instead of path param to support `/` in IDs) |

**Response `200`**

```json
{
  "id": "my-model",
  "user_id": "user_id",
  "base_model_id": null,
  "name": "My Custom Model",
  "params": {},
  "meta": {
    "profile_image_url": "/static/favicon.png",
    "description": null,
    "capabilities": null
  },
  "access_grants": [],
  "is_active": true,
  "updated_at": 1700000000,
  "created_at": 1699000000,
  "user": null,
  "write_access": true
}
```

Returns a ModelAccessResponse object (same schema as items in `/list`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or access denied |
| 404 | Model not found |

---

### GET /api/v1/models/model/profile/image

**Summary:** Returns the profile image for a model (redirect, inline image, or default favicon).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Query | id | string | Yes | Model ID |

**Response `200`**

Image data stream, a `302` redirect to external URL, or the default `/static/favicon.png` file.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/models/model/toggle

**Summary:** Toggles the `is_active` state of a model.

**Auth:** Verified user (must be model owner, have write access grant, or be admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Query | id | string | Yes | Model ID to toggle |

**Response `200`**

```json
{
  "id": "my-model",
  "user_id": "user_id",
  "name": "My Custom Model",
  "params": {},
  "meta": {},
  "access_grants": [],
  "is_active": false,
  "updated_at": 1700000001,
  "created_at": 1699000000
}
```

Returns a ModelResponse object with the updated `is_active` state.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Toggle operation failed |
| 401 | Not authenticated, no write access, or model not found |

---

### POST /api/v1/models/model/update

**Summary:** Updates a model's full configuration.

**Auth:** Verified user (must be model owner, have write access grant, or be admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | id | string | Yes | Model ID to update |
| Body | name | string | Yes | New display name |
| Body | meta | object | Yes | Updated metadata |
| Body | params | object | Yes | Updated parameters |
| Body | base_model_id | string | No | Base model ID |
| Body | access_grants | array[object] | No | Access grant list |
| Body | is_active | boolean | No | Active state (default `true`) |

**Response `200`**

Returns the updated ModelModel object.

```json
{
  "id": "my-model",
  "user_id": "user_id",
  "base_model_id": null,
  "name": "Updated Model Name",
  "params": {},
  "meta": {
    "profile_image_url": "/static/favicon.png",
    "description": "Updated description",
    "capabilities": null
  },
  "access_grants": [],
  "is_active": true,
  "updated_at": 1700000001,
  "created_at": 1699000000
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Access prohibited or update failed |
| 401 | Not authenticated or model not found |

---

### POST /api/v1/models/model/access/update

**Summary:** Sets access grants for a model (creates the model entry if it does not exist).

**Auth:** Verified user (must be model owner, have write access grant, or be admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | id | string | Yes | Model ID |
| Body | name | string | No | Model display name (used when creating a missing model entry) |
| Body | access_grants | array[object] | Yes | List of access grant objects; each has `principal_type`, `principal_id`, `permission` |

**Response `200`**

Returns the updated ModelModel object (same schema as POST `/model/update` response).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Access prohibited |
| 403 | Non-admin trying to create a missing model entry or trying to set public access without permission |
| 500 | Failed to create model entry |

---

### POST /api/v1/models/model/delete

**Summary:** Deletes a model by ID.

**Auth:** Verified user (must be model owner, have write access grant, or be admin)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | id | string | Yes | Model ID to delete |

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
| 401 | Not authenticated, no write access, or model not found |

---

### DELETE /api/v1/models/delete/all

**Summary:** Deletes all models from the database.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

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
| 403 | Insufficient permissions |
