# Knowledge Base API

Base path: `/api/v1/knowledge`

All endpoints require a verified user session. Creating and managing knowledge bases requires the `workspace.knowledge` permission (admins are exempt).

**Vector store interactions:** Endpoints that add/remove files or reindex trigger embedding generation and upsert/delete operations against the configured vector database.

---

### GET /api/v1/knowledge/

**Summary:** List knowledge bases accessible to the current user (paginated, 30 per page).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | `page` | int | No | Page number (1-based). Default `1`. |

**Response `200`**

```json
{
  "items": [
    {
      "id": "kb_abc123",
      "user_id": "user_xyz",
      "name": "Company Docs",
      "description": "Internal documentation",
      "meta": null,
      "access_grants": [],
      "user": { "id": "user_xyz", "name": "Alice", "email": "alice@example.com" },
      "write_access": true,
      "created_at": 1700000000,
      "updated_at": 1700000001
    }
  ],
  "total": 42
}
```

| Field | Type | Description |
|-------|------|-------------|
| `items` | array | Array of `KnowledgeAccessResponse` objects. |
| `total` | int | Total number of matching knowledge bases (for pagination). |
| `items[].id` | string | UUID of the knowledge base. |
| `items[].user_id` | string | Owner's user ID. |
| `items[].name` | string | Display name. |
| `items[].description` | string | Description. |
| `items[].meta` | object \| null | Arbitrary metadata. |
| `items[].access_grants` | array | Access control grants attached to this KB. |
| `items[].user` | object \| null | Owner user info. |
| `items[].write_access` | bool | Whether the current user has write access. |
| `items[].created_at` | int | Unix timestamp. |
| `items[].updated_at` | int | Unix timestamp. |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |

---

### GET /api/v1/knowledge/search

**Summary:** Search knowledge bases by name, description, or owner with optional view filter.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | `query` | string | No | Text to search in name, description, owner name/email. |
| Query | `view_option` | string | No | `created` — only show KBs owned by the caller; `shared` — only show KBs owned by others. |
| Query | `page` | int | No | Page number (1-based). Default `1`. |

**Response `200`**

Same schema as `GET /api/v1/knowledge/` (`KnowledgeAccessListResponse`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |

---

### GET /api/v1/knowledge/search/files

**Summary:** Search files across all knowledge bases accessible to the current user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | `query` | string | No | Filename substring to match. |
| Query | `page` | int | No | Page number (1-based). Default `1`. |

**Response `200`**

```json
{
  "items": [
    {
      "id": "file_abc",
      "user_id": "user_xyz",
      "filename": "report.pdf",
      "data": { "status": "completed" },
      "meta": { "name": "report.pdf", "content_type": "application/pdf", "size": 10240 },
      "user": { "id": "user_xyz", "name": "Alice" },
      "created_at": 1700000000,
      "updated_at": 1700000001
    }
  ],
  "total": 5
}
```

`KnowledgeFileListResponse` — paginated list of files with their uploader's user info.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |

---

### POST /api/v1/knowledge/create

**Summary:** Create a new knowledge base and embed its metadata into the vector store.

**Auth:** Verified user (requires `workspace.knowledge` permission or admin role)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `name` | string | Yes | Knowledge base display name. |
| Body | `description` | string | Yes | Short description. |
| Body | `access_grants` | array of objects | No | Access control grants (see Access Grants schema). |

**Response `200`**

`KnowledgeResponse` — same as the base KB model plus:

```json
{
  "id": "kb_abc123",
  "user_id": "user_xyz",
  "name": "Company Docs",
  "description": "Internal documentation",
  "meta": null,
  "access_grants": [],
  "files": [],
  "created_at": 1700000000,
  "updated_at": 1700000000
}
```

| Field | Type | Description |
|-------|------|-------------|
| `files` | array | Array of `FileMetadataResponse` objects linked to this KB (empty on creation). |

**Notes:** After creation, the KB's name + description are embedded into the `knowledge-bases` vector collection to enable semantic KB discovery.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | KB already exists or creation error. |
| 401 | Not authenticated or insufficient permission. |

---

### POST /api/v1/knowledge/reindex

**Summary:** Reindex all files in every knowledge base (admin only).

**Auth:** Admin only

**Request**

No additional parameters.

**Response `200`**

```json
true
```

**Notes:** Deletes and recreates the vector collection for each knowledge base by re-processing all linked files. Files that fail to process are logged but do not abort the overall operation.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |

---

### POST /api/v1/knowledge/metadata/reindex

**Summary:** Re-embed metadata (name + description) for all knowledge bases into the semantic search collection.

**Auth:** Admin only

**Request**

No additional parameters.

**Response `200`**

```json
{ "total": 15, "success": 15 }
```

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Number of knowledge bases processed. |
| `success` | int | Number successfully embedded. |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |

---

### GET /api/v1/knowledge/{id}

**Summary:** Retrieve a knowledge base by ID including its linked file list.

**Auth:** Verified user (owner, admin, or user with read access)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |

**Response `200`**

```json
{
  "id": "kb_abc123",
  "user_id": "user_xyz",
  "name": "Company Docs",
  "description": "Internal documentation",
  "meta": null,
  "access_grants": [],
  "files": [
    {
      "id": "file_001",
      "hash": "sha256...",
      "meta": { "name": "report.pdf", "content_type": "application/pdf", "size": 10240 },
      "created_at": 1700000000,
      "updated_at": 1700000001
    }
  ],
  "write_access": true,
  "created_at": 1700000000,
  "updated_at": 1700000001
}
```

`KnowledgeFilesResponse` fields:

| Field | Type | Description |
|-------|------|-------------|
| `files` | array of `FileMetadataResponse` | Metadata for each file linked to this KB. |
| `write_access` | bool | Whether the current user has write access. |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated or access prohibited. |
| 404 | Knowledge base not found. |

---

### POST /api/v1/knowledge/{id}/update

**Summary:** Update the name, description, and/or access grants of a knowledge base.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |
| Body | `name` | string | Yes | New name. |
| Body | `description` | string | Yes | New description. |
| Body | `access_grants` | array of objects | No | Replacement access grants list. |

**Response `200`**

`KnowledgeFilesResponse` (same schema as `GET /{id}`).

**Notes:** Re-embeds the updated name + description into the `knowledge-bases` vector collection.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Knowledge base not found or access prohibited. |
| 401 | Not authenticated. |

---

### POST /api/v1/knowledge/{id}/access/update

**Summary:** Replace the access grants for a knowledge base.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |
| Body | `access_grants` | array of objects | Yes | New set of access grants. Each object follows the `AccessGrantModel` schema (see below). |

**Access grant object schema:**

```json
{
  "principal_type": "user",
  "principal_id": "user_abc",
  "permission": "read"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `principal_type` | string | `user` or `group`. Use `user` with `principal_id: "*"` for public access. |
| `principal_id` | string | User/group ID, or `*` for public. |
| `permission` | string | `read` or `write`. |

**Response `200`**

`KnowledgeFilesResponse`.

**Notes:** Users without `sharing.public_knowledge` permission cannot grant public (`principal_id: "*"`) read access.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Access prohibited. |
| 401 | Not authenticated. |
| 404 | Knowledge base not found. |

---

### GET /api/v1/knowledge/{id}/files

**Summary:** List files linked to a knowledge base (paginated, with optional search/sort).

**Auth:** Verified user (owner, admin, or read-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |
| Query | `query` | string | No | Filename substring filter. |
| Query | `view_option` | string | No | `created` — only files uploaded by the caller; `shared` — files uploaded by others. |
| Query | `order_by` | string | No | Sort field: `name`, `created_at`, or `updated_at`. Default: `updated_at`. |
| Query | `direction` | string | No | Sort direction: `asc` or `desc`. Default: `desc`. |
| Query | `page` | int | No | Page number (1-based). Default `1`. |

**Response `200`**

`KnowledgeFileListResponse` — paginated list of `FileUserResponse` objects (file metadata + uploader user info).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Knowledge base not found or access prohibited. |
| 401 | Not authenticated. |

---

### POST /api/v1/knowledge/{id}/file/add

**Summary:** Add an already-uploaded file to a knowledge base and index it in the vector store.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |
| Body | `file_id` | string | Yes | ID of the file to add (must already be processed). |

**Response `200`**

`KnowledgeFilesResponse` reflecting the updated files list.

**Notes:**
- Calls `process_file` with `collection_name=<kb_id>` to embed the file's content into the KB's vector collection.
- The file must have non-empty `data` (i.e. processing must have completed).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Knowledge base or file not found, access prohibited, or file not yet processed. |
| 401 | Not authenticated. |

---

### POST /api/v1/knowledge/{id}/file/update

**Summary:** Re-embed a file that is already linked to a knowledge base (refresh its vector store entries).

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |
| Body | `file_id` | string | Yes | ID of the file to re-process. |

**Response `200`**

`KnowledgeFilesResponse`.

**Notes:** Deletes the file's existing vectors from the KB collection (`filter: {file_id: ...}`) then re-runs `process_file`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Knowledge base or file not found, or access prohibited. |
| 401 | Not authenticated. |

---

### POST /api/v1/knowledge/{id}/file/remove

**Summary:** Remove a file from a knowledge base and optionally delete the file itself.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |
| Body | `file_id` | string | Yes | File ID to remove. |
| Query | `delete_file` | bool | No | Also permanently delete the file record and its storage object. Default `true`. |

**Response `200`**

`KnowledgeFilesResponse`.

**Notes:** Removes vector entries by both `file_id` and `hash` filters. If `delete_file=true`, the file's own `file-{id}` vector collection is also deleted.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Knowledge base or file not found, or access prohibited. |
| 401 | Not authenticated. |

---

### DELETE /api/v1/knowledge/{id}/delete

**Summary:** Permanently delete a knowledge base, its vector collection, and update any models referencing it.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |

**Response `200`**

```json
true
```

**Notes:**
- Removes the KB's vector collection from the vector store.
- Removes the KB's entry from the `knowledge-bases` semantic embedding collection.
- Updates all models that reference this KB to remove the stale reference.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Knowledge base not found or access prohibited. |
| 401 | Not authenticated. |

---

### POST /api/v1/knowledge/{id}/reset

**Summary:** Clear all file associations from a knowledge base and delete its vector collection.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |

**Response `200`**

`KnowledgeResponse` with an empty `files` array.

**Notes:** Deletes the entire vector collection for the KB but does not delete the underlying file records.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Knowledge base not found or access prohibited. |
| 401 | Not authenticated. |

---

### POST /api/v1/knowledge/{id}/files/batch/add

**Summary:** Add multiple files to a knowledge base in a single batch operation.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |
| Body | (array) | array of `{ "file_id": string }` | Yes | List of file IDs to add. |

**Response `200`**

`KnowledgeFilesResponse`. If some files failed to process, the response includes a `warnings` object:

```json
{
  "id": "kb_abc123",
  "files": [...],
  "warnings": {
    "message": "Some files failed to process",
    "errors": ["file_001: Duplicate content detected"]
  }
}
```

**Notes:** Uses `process_files_batch` which batches all file documents into a single `save_docs_to_vector_db` call for efficiency. Only successfully processed files are linked to the KB.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Knowledge base not found, a requested file not found, access prohibited, or processing error. |
| 401 | Not authenticated. |

---

### GET /api/v1/knowledge/{id}/export

**Summary:** Export all file contents in a knowledge base as a `.zip` archive.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | Knowledge base UUID. |

**Response `200`**

Binary ZIP file (`Content-Type: application/zip`). Each file inside is named `<original_filename>.txt` and contains the extracted text content.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |
| 404 | Knowledge base not found. |
