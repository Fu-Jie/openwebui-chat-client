# Files API

Base path: `/api/v1/files`

All endpoints require a verified user session (Bearer token) unless noted.

---

### POST /api/v1/files/

**Summary:** Upload a file, optionally extracting and embedding its content into the vector store.

**Auth:** Verified user

**Request** — `multipart/form-data`

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Form | `file` | binary (UploadFile) | Yes | The file to upload. |
| Form | `metadata` | JSON string or object | No | Arbitrary key/value metadata to attach (e.g. `{"channel_id": "..."}`). |
| Query | `process` | bool | No | Whether to extract text and embed content. Default `true`. |
| Query | `process_in_background` | bool | No | Run processing asynchronously. Default `true`. |

**Response `200`**

```json
{
  "id": "3f8e1a2b-4c5d-6e7f-8a9b-0c1d2e3f4a5b",
  "user_id": "user_abc123",
  "hash": null,
  "filename": "report.pdf",
  "data": {
    "status": "pending"
  },
  "meta": {
    "name": "report.pdf",
    "content_type": "application/pdf",
    "size": 102400
  },
  "created_at": 1700000000,
  "updated_at": 1700000000
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | UUID of the uploaded file. |
| `user_id` | string | ID of the uploading user. |
| `hash` | string \| null | SHA-256 of extracted text (set after processing completes). |
| `filename` | string | Original filename. |
| `data.status` | string | Processing status: `pending`, `completed`, or `failed`. |
| `meta.name` | string | Original filename. |
| `meta.content_type` | string | MIME type detected from upload. |
| `meta.size` | int | File size in bytes. |
| `created_at` | int | Unix timestamp. |
| `updated_at` | int | Unix timestamp. |

**Notes:**
- Upload uses `multipart/form-data`; the `metadata` field accepts a JSON-encoded string.
- If `process=true` and `process_in_background=true`, the response is returned immediately with `status: pending`; processing happens asynchronously.
- Audio files whose MIME type matches `STT_SUPPORTED_CONTENT_TYPES` are first transcribed via the STT pipeline before embedding.
- Files with extensions not in `ALLOWED_FILE_EXTENSIONS` (when configured) are rejected with HTTP 400.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid metadata format, disallowed file extension, or upload error. |
| 401 | Not authenticated. |

---

### GET /api/v1/files/

**Summary:** List all files accessible to the current user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | `content` | bool | No | Include extracted text in `data.content`. Default `true`. |

**Response `200`**

```json
[
  {
    "id": "3f8e1a2b-...",
    "user_id": "user_abc123",
    "filename": "report.pdf",
    "data": { "status": "completed", "content": "..." },
    "meta": { "name": "report.pdf", "content_type": "application/pdf", "size": 102400 },
    "created_at": 1700000000,
    "updated_at": 1700000000
  }
]
```

Array of `FileModelResponse` objects (same schema as upload response).

Admins with `BYPASS_ADMIN_ACCESS_CONTROL` see all files; otherwise only the caller's own files are returned.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |

---

### GET /api/v1/files/search

**Summary:** Search files by filename pattern with optional pagination.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Query | `filename` | string | Yes | Glob pattern to match (e.g. `*.pdf`, `report*`). |
| Query | `content` | bool | No | Include extracted text. Default `true`. |
| Query | `skip` | int | No | Number of results to skip. Default `0`. |
| Query | `limit` | int | No | Max results to return (1–1000). Default `100`. |

**Response `200`**

Array of `FileModelResponse` objects matching the pattern.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | No files found matching the pattern. |

---

### DELETE /api/v1/files/all

**Summary:** Delete all files and reset the vector store (admin only).

**Auth:** Admin only

**Request**

No additional parameters.

**Response `200`**

```json
{ "message": "All files deleted successfully" }
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Error deleting files or resetting vector store. |
| 401 | Not authenticated / not an admin. |

---

### GET /api/v1/files/{id}

**Summary:** Retrieve file metadata by ID.

**Auth:** Verified user (owner, admin, or user with read access via a knowledge base or shared chat)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | File UUID. |

**Response `200`**

Full `FileModel` object including `path`, `data`, and `meta`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | File not found or access denied. |

---

### GET /api/v1/files/{id}/process/status

**Summary:** Poll or stream the processing status of a file.

**Auth:** Verified user (owner, admin, or read-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | File UUID. |
| Query | `stream` | bool | No | If `true`, returns an SSE stream instead of a single JSON object. Default `false`. |

**Response `200`** (non-streaming)

```json
{ "status": "completed" }
```

**Response `200`** (streaming, `Content-Type: text/event-stream`)

Server-sent events, one per second, each formatted as:

```
data: {"status": "pending"}

data: {"status": "completed"}
```

If the status is `failed` the event also contains `"error": "<message>"`. The stream terminates when status reaches `completed` or `failed`.

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `pending`, `completed`, or `failed`. |
| `error` | string | Only present when `status` is `failed`. |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | File not found or access denied. |

---

### GET /api/v1/files/{id}/data/content

**Summary:** Retrieve the extracted text content stored in `file.data.content`.

**Auth:** Verified user (owner, admin, or read-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | File UUID. |

**Response `200`**

```json
{ "content": "Extracted text from the file..." }
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | File not found or access denied. |

---

### POST /api/v1/files/{id}/data/content/update

**Summary:** Replace the extracted text content and re-embed the file in the vector store.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | File UUID. |
| Body | `content` | string | Yes | New text content to store and index. |

**Response `200`**

```json
{ "content": "Updated text content..." }
```

**Notes:** Triggers `process_file` to update the vector store with the new content.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | File not found or access denied. |

---

### GET /api/v1/files/{id}/content

**Summary:** Download the raw file binary.

**Auth:** Verified user (owner, admin, or read-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | File UUID. |
| Query | `attachment` | bool | No | Force `Content-Disposition: attachment`. Default `false`. |

**Response `200`**

Raw file bytes. `Content-Type` is set to the stored MIME type. For PDFs the disposition is `inline`; for all other types it defaults to `attachment` unless overridden.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | File not found or access denied. |

---

### GET /api/v1/files/{id}/content/html

**Summary:** Serve the raw file as HTML (owner's admin status is required).

**Auth:** Verified user — additionally the file owner must be an admin.

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | File UUID. |

**Response `200`**

Raw file bytes served with no explicit `Content-Disposition`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | File not found, access denied, or file owner is not an admin. |

---

### GET /api/v1/files/{id}/content/{file_name}

**Summary:** Download the raw file with a forced `attachment` disposition using the original filename.

**Auth:** Verified user (owner, admin, or read-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | File UUID. |
| Path | `file_name` | string | Yes | Ignored server-side; the actual filename comes from `file.meta.name`. |

**Response `200`**

Raw file bytes with `Content-Disposition: attachment; filename*=UTF-8''<encoded_name>`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 404 | File not found or access denied. |

---

### DELETE /api/v1/files/{id}

**Summary:** Delete a file, its vector store embeddings, and its storage object.

**Auth:** Verified user (owner, admin, or write-access user)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | `id` | string | Yes | File UUID. |

**Response `200`**

```json
{ "message": "File deleted successfully" }
```

**Notes:** Also removes the file from any knowledge base associations and deletes the corresponding vector collections.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Deletion error. |
| 401 | Not authenticated. |
| 404 | File not found or access denied. |
