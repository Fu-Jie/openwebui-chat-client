# Folders API

Base path: `/api/v1/folders`

All endpoints require a verified user session. The `ENABLE_FOLDERS` config flag must be `true` and users need the `features.folders` permission (admins are exempt from the permission check).

---

### GET /api/v1/folders/

**Summary:** List all folders belonging to the current user.

**Auth:** Verified user (requires `features.folders` permission or admin role; `ENABLE_FOLDERS` must be enabled)

**Request**

No additional parameters.

**Response `200`**

```json
[
  {
    "id": "fld_abc123",
    "name": "My Research",
    "meta": { "icon": "📁" },
    "parent_id": null,
    "is_expanded": false,
    "created_at": 1700000000,
    "updated_at": 1700000001
  }
]
```

Array of `FolderNameIdResponse` objects.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Folder UUID. |
| `name` | string | Display name. |
| `meta.icon` | string \| null | Optional icon for the folder. |
| `parent_id` | string \| null | Parent folder ID, or `null` for root folders. |
| `is_expanded` | bool | Whether the folder is expanded in the UI. |
| `created_at` | int | Unix timestamp. |
| `updated_at` | int | Unix timestamp. |

**Notes:** The response validates file/collection access within each folder's `data.files` array and silently strips entries the user no longer has permission to see.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 403 | Folders feature disabled or user lacks `features.folders` permission. |

---

### POST /api/v1/folders/

**Summary:** Create a new root-level folder.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `name` | string | Yes | Folder name (must be unique at root level for this user). |
| Body | `data` | object | No | Arbitrary data payload for the folder. |
| Body | `meta` | object | No | Metadata (e.g. `{"icon": "📁"}`). |

**Response `200`**

```json
{
  "id": "fld_abc123",
  "parent_id": null,
  "user_id": "user_xyz",
  "name": "My Research",
  "items": null,
  "meta": null,
  "data": null,
  "is_expanded": false,
  "created_at": 1700000000,
  "updated_at": 1700000000
}
```

Full `FolderModel` object.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Folder UUID. |
| `parent_id` | string \| null | Always `null` for newly created folders. |
| `user_id` | string | Owner's user ID. |
| `name` | string | Folder name. |
| `items` | object \| null | Reserved for nested items. |
| `meta` | object \| null | Metadata. |
| `data` | object \| null | Data payload. |
| `is_expanded` | bool | Default `false`. |
| `created_at` | int | Unix timestamp. |
| `updated_at` | int | Unix timestamp. |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Folder with the same name already exists at root level, or creation error. |
| 401 | Not authenticated. |

---

### GET /api/v1/folders/{id}

**Summary:** Retrieve a folder by ID.

**Auth:** Verified user (owner only)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Folder UUID. |

**Response `200`**

Full `FolderModel` object (same schema as create response).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | Folder not found or not owned by current user. |

---

### POST /api/v1/folders/{id}/update

**Summary:** Update a folder's name and/or metadata.

**Auth:** Verified user (owner only)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Folder UUID. |
| Body | `name` | string | No | New folder name. Must be unique among siblings. |
| Body | `data` | object | No | Data to merge into the folder's existing `data`. |
| Body | `meta` | object | No | Metadata to merge into the folder's existing `meta`. |

**Response `200`**

Updated `FolderModel` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | A sibling folder with the new name already exists, or update error. |
| 401 | Not authenticated. |
| 404 | Folder not found or not owned by current user. |

---

### POST /api/v1/folders/{id}/update/parent

**Summary:** Move a folder under a different parent (or to root).

**Auth:** Verified user (owner only)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Folder UUID to move. |
| Body | `parent_id` | string \| null | No | Target parent folder ID, or `null` to move to root. |

**Response `200`**

Updated `FolderModel` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | A folder with the same name already exists under the target parent, or update error. |
| 401 | Not authenticated. |
| 404 | Folder not found or not owned by current user. |

---

### POST /api/v1/folders/{id}/update/expanded

**Summary:** Toggle the expanded/collapsed state of a folder in the UI.

**Auth:** Verified user (owner only)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Folder UUID. |
| Body | `is_expanded` | bool | Yes | `true` to expand, `false` to collapse. |

**Response `200`**

Updated `FolderModel` object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Update error. |
| 401 | Not authenticated. |
| 404 | Folder not found or not owned by current user. |

---

### DELETE /api/v1/folders/{id}

**Summary:** Delete a folder and optionally its contained chats.

**Auth:** Verified user (owner only; deleting chats also requires `chat.delete` permission or admin role)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Folder UUID. |
| Query | `delete_contents` | bool | No | If `true` (default), chats inside the folder are permanently deleted. If `false`, chats are moved to the root. |

**Response `200`**

```json
true
```

**Notes:** Recursively deletes all sub-folders. If `delete_contents=false` all chats inside (including sub-folders) are re-parented to root instead of deleted.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Deletion error. |
| 401 | Not authenticated. |
| 403 | Folder contains chats and user lacks `chat.delete` permission. |
| 404 | Folder not found or not owned by current user. |
