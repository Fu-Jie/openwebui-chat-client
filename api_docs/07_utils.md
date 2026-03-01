# Utilities API

Base path: `/api/v1/utils`

Miscellaneous utility endpoints for code formatting, execution, markdown rendering, PDF export, and database download.

---

### GET /api/v1/utils/gravatar

**Summary:** Return the Gravatar URL for a given email address.

**Auth:** Verified user

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Email address to look up |

**Response `200`**

```json
"https://www.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?d=mp&s=100"
```

| Field | Type | Description |
|-------|------|-------------|
| (string) | string | Gravatar URL for the given email |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/utils/code/format

**Summary:** Format Python code using the `black` formatter.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | code | string | Yes | Python source code to format |

**Response `200`**

```json
{
  "code": "def hello():\n    print(\"Hello, world!\")\n"
}
```

| Field | Type | Description |
|-------|------|-------------|
| code | string | Formatted Python code (or original code if already formatted) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Syntax error or formatting failed |
| 401 | Not authenticated / not admin |

---

### POST /api/v1/utils/code/execute

**Summary:** Execute code in a Jupyter kernel (requires `CODE_EXECUTION_ENGINE=jupyter`).

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | code | string | Yes | Code to execute in the Jupyter kernel |

**Response `200`**

```json
{
  "output": "Hello, world!\n",
  "error": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| output | string | Standard output from code execution |
| error | string\|null | Error output or traceback, if any |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Code execution engine not supported (only `jupyter` engine is currently supported) |
| 401 | Not authenticated |

---

### POST /api/v1/utils/markdown

**Summary:** Render a Markdown string to HTML.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | md | string | Yes | Markdown source text |

**Response `200`**

```json
{
  "html": "<h1>Hello</h1>\n<p>This is <strong>bold</strong>.</p>\n"
}
```

| Field | Type | Description |
|-------|------|-------------|
| html | string | Rendered HTML output |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/utils/pdf

**Summary:** Export a chat conversation as a PDF file.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | title | string | Yes | Chat title (used as PDF heading) |
| Body | messages | array[object] | Yes | List of message objects to include in the PDF |

**Message Object**

```json
{
  "role": "user",
  "content": "Explain quantum entanglement."
}
```

| Field | Type | Description |
|-------|------|-------------|
| role | string | `user` or `assistant` |
| content | string | Message text content |

**Response `200`**

- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=chat.pdf`
- Body: raw PDF binary

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | PDF generation failed |
| 401 | Not authenticated |

---

### GET /api/v1/utils/db/download

**Summary:** Download the SQLite database file (only available when `ENABLE_ADMIN_EXPORT=true` and the database engine is SQLite).

**Auth:** Admin only

**Response `200`**

- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename=webui.db`
- Body: raw SQLite database binary

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Database is not SQLite (PostgreSQL or other engines not exportable) |
| 401 | Not authenticated / not admin, or `ENABLE_ADMIN_EXPORT` is disabled |
