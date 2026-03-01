# Retrieval (RAG) API

Base path: `/api/v1/retrieval`

This module configures the RAG (Retrieval-Augmented Generation) pipeline: embedding models, chunking parameters, web search, and vector store operations. Configuration endpoints require admin access; document processing and query endpoints require a verified user.

---

### GET /api/v1/retrieval/

**Summary:** Return a brief status summary of the current RAG configuration.

**Auth:** Public (no auth required)

**Request**

No additional parameters.

**Response `200`**

```json
{
  "status": true,
  "CHUNK_SIZE": 1500,
  "CHUNK_OVERLAP": 100,
  "RAG_TEMPLATE": "...",
  "RAG_EMBEDDING_ENGINE": "openai",
  "RAG_EMBEDDING_MODEL": "text-embedding-3-small",
  "RAG_RERANKING_MODEL": "",
  "RAG_EMBEDDING_BATCH_SIZE": 1,
  "ENABLE_ASYNC_EMBEDDING": true,
  "RAG_EMBEDDING_CONCURRENT_REQUESTS": 0
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | bool | Always `true`. |
| `CHUNK_SIZE` | int | Max characters (or tokens) per chunk. |
| `CHUNK_OVERLAP` | int | Overlap between consecutive chunks. |
| `RAG_TEMPLATE` | string | Jinja2 template used to inject context into prompts. |
| `RAG_EMBEDDING_ENGINE` | string | Active embedding engine: `""` (local), `openai`, `ollama`, or `azure_openai`. |
| `RAG_EMBEDDING_MODEL` | string | Model identifier used for embeddings. |
| `RAG_RERANKING_MODEL` | string | Reranker model identifier (empty = disabled). |
| `RAG_EMBEDDING_BATCH_SIZE` | int | Batch size for embedding API calls. |
| `ENABLE_ASYNC_EMBEDDING` | bool | Whether async embedding is enabled. |
| `RAG_EMBEDDING_CONCURRENT_REQUESTS` | int | Max concurrent embedding requests (0 = unlimited). |

**Error Responses**

No error responses.

---

### GET /api/v1/retrieval/embedding

**Summary:** Get the full embedding model configuration including provider credentials.

**Auth:** Admin only

**Request**

No additional parameters.

**Response `200`**

```json
{
  "status": true,
  "RAG_EMBEDDING_ENGINE": "openai",
  "RAG_EMBEDDING_MODEL": "text-embedding-3-small",
  "RAG_EMBEDDING_BATCH_SIZE": 1,
  "ENABLE_ASYNC_EMBEDDING": true,
  "RAG_EMBEDDING_CONCURRENT_REQUESTS": 0,
  "openai_config": {
    "url": "https://api.openai.com/v1",
    "key": "sk-..."
  },
  "ollama_config": {
    "url": "http://localhost:11434",
    "key": ""
  },
  "azure_openai_config": {
    "url": "https://my-resource.openai.azure.com",
    "key": "...",
    "version": "2024-02-01"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `RAG_EMBEDDING_ENGINE` | string | Active engine: `""`, `openai`, `ollama`, or `azure_openai`. |
| `RAG_EMBEDDING_MODEL` | string | Model name/ID. |
| `RAG_EMBEDDING_BATCH_SIZE` | int | API call batch size. |
| `ENABLE_ASYNC_EMBEDDING` | bool | Async embedding flag. |
| `RAG_EMBEDDING_CONCURRENT_REQUESTS` | int | Concurrency limit. |
| `openai_config.url` | string | OpenAI-compatible API base URL. |
| `openai_config.key` | string | API key. |
| `ollama_config.url` | string | Ollama base URL. |
| `ollama_config.key` | string | Ollama API key (if required). |
| `azure_openai_config.url` | string | Azure OpenAI endpoint. |
| `azure_openai_config.key` | string | Azure API key. |
| `azure_openai_config.version` | string | Azure API version. |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |

---

### POST /api/v1/retrieval/embedding/update

**Summary:** Update the embedding model and provider configuration.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `RAG_EMBEDDING_ENGINE` | string | Yes | Engine to use: `""` (local SentenceTransformer), `openai`, `ollama`, `azure_openai`. |
| Body | `RAG_EMBEDDING_MODEL` | string | Yes | Model identifier. |
| Body | `RAG_EMBEDDING_BATCH_SIZE` | int | No | Batch size for API calls. Default `1`. |
| Body | `ENABLE_ASYNC_EMBEDDING` | bool | No | Enable async embedding. Default `true`. |
| Body | `RAG_EMBEDDING_CONCURRENT_REQUESTS` | int | No | Concurrent requests limit (`0` = unlimited). Default `0`. |
| Body | `openai_config` | object | No | `{ "url": string, "key": string }` — required when engine is `openai`. |
| Body | `ollama_config` | object | No | `{ "url": string, "key": string }` — required when engine is `ollama`. |
| Body | `azure_openai_config` | object | No | `{ "url": string, "key": string, "version": string }` — required when engine is `azure_openai`. |

**Response `200`**

Same schema as `GET /embedding`.

**Notes:** Unloads the current in-process embedding model before applying changes. For local (`""`) engine the GPU cache is also cleared.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |
| 500 | Error loading new embedding model. |

---

### GET /api/v1/retrieval/config

**Summary:** Get the full RAG pipeline configuration.

**Auth:** Admin only

**Request**

No additional parameters.

**Response `200`**

Large configuration object. Key sections:

```json
{
  "status": true,
  "RAG_TEMPLATE": "...",
  "TOP_K": 5,
  "BYPASS_EMBEDDING_AND_RETRIEVAL": false,
  "RAG_FULL_CONTEXT": false,
  "ENABLE_RAG_HYBRID_SEARCH": false,
  "ENABLE_RAG_HYBRID_SEARCH_ENRICHED_TEXTS": false,
  "TOP_K_RERANKER": 5,
  "RELEVANCE_THRESHOLD": 0.0,
  "HYBRID_BM25_WEIGHT": 0.5,
  "CONTENT_EXTRACTION_ENGINE": "",
  "PDF_EXTRACT_IMAGES": false,
  "PDF_LOADER_MODE": "default",
  "DATALAB_MARKER_API_KEY": "",
  "DATALAB_MARKER_API_BASE_URL": "",
  "DATALAB_MARKER_ADDITIONAL_CONFIG": "",
  "DATALAB_MARKER_SKIP_CACHE": false,
  "DATALAB_MARKER_FORCE_OCR": false,
  "DATALAB_MARKER_PAGINATE": false,
  "DATALAB_MARKER_STRIP_EXISTING_OCR": false,
  "DATALAB_MARKER_DISABLE_IMAGE_EXTRACTION": false,
  "DATALAB_MARKER_FORMAT_LINES": false,
  "DATALAB_MARKER_USE_LLM": false,
  "DATALAB_MARKER_OUTPUT_FORMAT": "markdown",
  "EXTERNAL_DOCUMENT_LOADER_URL": "",
  "EXTERNAL_DOCUMENT_LOADER_API_KEY": "",
  "TIKA_SERVER_URL": "",
  "DOCLING_SERVER_URL": "",
  "DOCLING_API_KEY": "",
  "DOCLING_PARAMS": {},
  "DOCUMENT_INTELLIGENCE_ENDPOINT": "",
  "DOCUMENT_INTELLIGENCE_KEY": "",
  "DOCUMENT_INTELLIGENCE_MODEL": "",
  "MISTRAL_OCR_API_BASE_URL": "",
  "MISTRAL_OCR_API_KEY": "",
  "MINERU_API_MODE": "",
  "MINERU_API_URL": "",
  "MINERU_API_KEY": "",
  "MINERU_API_TIMEOUT": "",
  "MINERU_PARAMS": {},
  "RAG_RERANKING_MODEL": "",
  "RAG_RERANKING_ENGINE": "",
  "RAG_EXTERNAL_RERANKER_URL": "",
  "RAG_EXTERNAL_RERANKER_API_KEY": "",
  "RAG_EXTERNAL_RERANKER_TIMEOUT": "",
  "TEXT_SPLITTER": "character",
  "ENABLE_MARKDOWN_HEADER_TEXT_SPLITTER": false,
  "CHUNK_SIZE": 1500,
  "CHUNK_MIN_SIZE_TARGET": 0,
  "CHUNK_OVERLAP": 100,
  "FILE_MAX_SIZE": null,
  "FILE_MAX_COUNT": null,
  "FILE_IMAGE_COMPRESSION_WIDTH": null,
  "FILE_IMAGE_COMPRESSION_HEIGHT": null,
  "ALLOWED_FILE_EXTENSIONS": [],
  "ENABLE_GOOGLE_DRIVE_INTEGRATION": false,
  "ENABLE_ONEDRIVE_INTEGRATION": false,
  "web": { "...": "..." }
}
```

**Config field reference:**

**RAG Settings**

| Field | Type | Description |
|-------|------|-------------|
| `RAG_TEMPLATE` | string | Jinja2 template for injecting retrieved context into prompts. |
| `TOP_K` | int | Number of top results to retrieve. |
| `BYPASS_EMBEDDING_AND_RETRIEVAL` | bool | Skip embedding and retrieval entirely (return raw content). |
| `RAG_FULL_CONTEXT` | bool | Return the full document text instead of chunked excerpts. |

**Hybrid Search Settings**

| Field | Type | Description |
|-------|------|-------------|
| `ENABLE_RAG_HYBRID_SEARCH` | bool | Enable BM25 + vector hybrid search. |
| `ENABLE_RAG_HYBRID_SEARCH_ENRICHED_TEXTS` | bool | Use enriched text representations in hybrid search. |
| `TOP_K_RERANKER` | int | Number of candidates passed to the reranker. |
| `RELEVANCE_THRESHOLD` | float | Minimum relevance score to include a result. |
| `HYBRID_BM25_WEIGHT` | float | BM25 weight in the hybrid scoring formula (0.0–1.0). |

**Content Extraction Settings**

| Field | Type | Description |
|-------|------|-------------|
| `CONTENT_EXTRACTION_ENGINE` | string | `""` (default), `datalab_marker`, `external`, `tika`, `docling`, `document_intelligence`, `mistral_ocr`, or `mineru`. |
| `PDF_EXTRACT_IMAGES` | bool | Extract images from PDFs. |
| `PDF_LOADER_MODE` | string | PDF loader mode: `default` or `ocr`. |
| `DATALAB_MARKER_*` | various | Datalab Marker API settings (key, URL, config, flags). |
| `EXTERNAL_DOCUMENT_LOADER_URL` | string | URL of external document loader service. |
| `EXTERNAL_DOCUMENT_LOADER_API_KEY` | string | API key for external loader. |
| `TIKA_SERVER_URL` | string | Apache Tika server URL. |
| `DOCLING_SERVER_URL` | string | Docling server URL. |
| `DOCLING_API_KEY` | string | Docling API key. |
| `DOCLING_PARAMS` | object | Additional Docling parameters. |
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | string | Azure Document Intelligence endpoint. |
| `DOCUMENT_INTELLIGENCE_KEY` | string | Azure Document Intelligence key. |
| `DOCUMENT_INTELLIGENCE_MODEL` | string | Azure Document Intelligence model. |
| `MISTRAL_OCR_API_BASE_URL` | string | Mistral OCR API base URL. |
| `MISTRAL_OCR_API_KEY` | string | Mistral OCR API key. |
| `MINERU_API_MODE` | string | MinerU API mode. |
| `MINERU_API_URL` | string | MinerU API URL. |
| `MINERU_API_KEY` | string | MinerU API key. |
| `MINERU_API_TIMEOUT` | string | MinerU request timeout. |
| `MINERU_PARAMS` | object | Additional MinerU parameters. |

**Reranking Settings**

| Field | Type | Description |
|-------|------|-------------|
| `RAG_RERANKING_MODEL` | string | Reranker model name (empty = disabled). |
| `RAG_RERANKING_ENGINE` | string | `""` (local CrossEncoder), `external`. |
| `RAG_EXTERNAL_RERANKER_URL` | string | External reranker service URL. |
| `RAG_EXTERNAL_RERANKER_API_KEY` | string | External reranker API key. |
| `RAG_EXTERNAL_RERANKER_TIMEOUT` | string | Timeout in seconds (as string). |

**Chunking Settings**

| Field | Type | Description |
|-------|------|-------------|
| `TEXT_SPLITTER` | string | `character` (RecursiveCharacterTextSplitter) or `token` (TokenTextSplitter). |
| `ENABLE_MARKDOWN_HEADER_TEXT_SPLITTER` | bool | Pre-split on markdown headers before chunking. |
| `CHUNK_SIZE` | int | Max chunk size in characters or tokens. |
| `CHUNK_MIN_SIZE_TARGET` | int | Minimum target size; small chunks are merged up to this size. |
| `CHUNK_OVERLAP` | int | Overlap between consecutive chunks. |

**File Upload Settings**

| Field | Type | Description |
|-------|------|-------------|
| `FILE_MAX_SIZE` | int \| null | Maximum upload file size in MB (`null` = unlimited). |
| `FILE_MAX_COUNT` | int \| null | Maximum number of files per upload (`null` = unlimited). |
| `FILE_IMAGE_COMPRESSION_WIDTH` | int \| null | Max image width for compression. |
| `FILE_IMAGE_COMPRESSION_HEIGHT` | int \| null | Max image height for compression. |
| `ALLOWED_FILE_EXTENSIONS` | array of strings | Whitelist of allowed file extensions (empty = all allowed). |

**Integration Settings**

| Field | Type | Description |
|-------|------|-------------|
| `ENABLE_GOOGLE_DRIVE_INTEGRATION` | bool | Enable Google Drive file picker. |
| `ENABLE_ONEDRIVE_INTEGRATION` | bool | Enable OneDrive file picker. |

**Web Search Settings** (nested under `web` key)

| Field | Type | Description |
|-------|------|-------------|
| `ENABLE_WEB_SEARCH` | bool | Enable web search feature. |
| `WEB_SEARCH_ENGINE` | string | Active search engine (e.g. `duckduckgo`, `searxng`, `brave`, `google_pse`, etc.). |
| `WEB_SEARCH_TRUST_ENV` | bool | Trust proxy settings from environment for web requests. |
| `WEB_SEARCH_RESULT_COUNT` | int | Number of search results to fetch. |
| `WEB_SEARCH_CONCURRENT_REQUESTS` | int | Max concurrent search queries (0 = unlimited). |
| `WEB_LOADER_CONCURRENT_REQUESTS` | int | Max concurrent page loads. |
| `WEB_SEARCH_DOMAIN_FILTER_LIST` | array | Domains to include/exclude in results. |
| `BYPASS_WEB_SEARCH_EMBEDDING_AND_RETRIEVAL` | bool | Skip embedding web search results. |
| `BYPASS_WEB_SEARCH_WEB_LOADER` | bool | Use only search snippets, skip full page loading. |
| `WEB_LOADER_ENGINE` | string | Web loader backend: `""` (default), `playwright`, `firecrawl`. |
| `WEB_LOADER_TIMEOUT` | string | Timeout for web page loading. |
| `ENABLE_WEB_LOADER_SSL_VERIFICATION` | bool | Verify SSL certificates when loading pages. |
| `PLAYWRIGHT_WS_URL` | string | Remote Playwright websocket URL. |
| `PLAYWRIGHT_TIMEOUT` | int | Playwright navigation timeout (ms). |
| `YOUTUBE_LOADER_LANGUAGE` | array | Preferred transcript languages for YouTube. |
| `YOUTUBE_LOADER_PROXY_URL` | string | Proxy URL for YouTube transcript fetching. |
| `YOUTUBE_LOADER_TRANSLATION` | string | Target language for YouTube transcript translation. |
| Various `*_API_KEY` / `*_ENGINE` fields | string | Credentials for individual search providers (Brave, SearXNG, Tavily, Perplexity, Bing, Jina, etc.). |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |

---

### POST /api/v1/retrieval/config/update

**Summary:** Update any subset of RAG pipeline configuration fields.

**Auth:** Admin only

**Request**

JSON body using the `ConfigForm` schema. All fields are optional — only provided fields are updated.

The body mirrors the `GET /config` response structure (all top-level fields plus nested `web` object).

**Response `200`**

Updated configuration object (same schema as `GET /config`).

**Notes:** When `RAG_RERANKING_MODEL` is changed, the reranker is reloaded. When `RAG_RERANKING_ENGINE` is changed to `""`, the in-process model is unloaded and GPU memory is freed.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |
| 500 | Error loading reranker model. |

---

### POST /api/v1/retrieval/process/file

**Summary:** Extract text from an uploaded file and save it to the vector store.

**Auth:** Verified user (non-admins can only process their own files)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `file_id` | string | Yes | UUID of an already-uploaded file. |
| Body | `content` | string | No | Provide text directly instead of re-parsing the file. Clears the existing file collection. |
| Body | `collection_name` | string | No | Target vector collection name. Defaults to `file-{file_id}`. If provided, adds to that collection (KB use case). |

**Response `200`**

```json
{
  "status": true,
  "collection_name": "file-3f8e1a2b-...",
  "filename": "report.pdf",
  "content": "Extracted text..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | bool | `true` on success. |
| `collection_name` | string \| null | Vector collection name where chunks were stored (`null` if `BYPASS_EMBEDDING_AND_RETRIEVAL` is enabled). |
| `filename` | string | Original filename. |
| `content` | string | Full extracted text. |

**Notes:**
- Uses the configured `CONTENT_EXTRACTION_ENGINE` to load the file.
- Splits text according to `TEXT_SPLITTER`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, and `CHUNK_MIN_SIZE_TARGET`.
- Sets `file.data.status` to `completed` or `failed` after processing.
- Raises HTTP 400 if pandoc is required but not installed.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Processing error (e.g. unsupported format, duplicate content, empty content). |
| 401 | Not authenticated. |
| 404 | File not found. |

---

### POST /api/v1/retrieval/process/text

**Summary:** Embed arbitrary text content into a vector collection.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `name` | string | Yes | A label for the text (stored in chunk metadata). |
| Body | `content` | string | Yes | Text to embed. |
| Body | `collection_name` | string | No | Target collection name. Defaults to SHA-256 of the content. |

**Response `200`**

```json
{
  "status": true,
  "collection_name": "a1b2c3d4...",
  "content": "Text that was embedded..."
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |
| 500 | Error saving to vector database. |

---

### POST /api/v1/retrieval/process/web

**Summary:** Fetch a URL, extract its content, and embed it into a vector collection.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `url` | string | Yes | URL to fetch and process. |
| Body | `collection_name` | string | No | Target collection name. Defaults to SHA-256 of the URL (first 63 chars). |
| Query | `process` | bool | No | Whether to embed the content. Default `true`. If `false`, returns raw content without embedding. |
| Query | `overwrite` | bool | No | Overwrite existing collection. Default `true`. |

**Response `200`**

```json
{
  "status": true,
  "collection_name": "ab1234...",
  "filename": "https://example.com/page",
  "file": {
    "data": { "content": "Page content..." },
    "meta": { "name": "https://example.com/page", "source": "https://example.com/page" }
  }
}
```

When `process=false`:

```json
{ "status": true, "content": "Raw page content..." }
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Fetch or embedding error. |
| 401 | Not authenticated. |

---

### POST /api/v1/retrieval/process/youtube

**Summary:** Fetch YouTube transcript and embed it into a vector collection.

**Auth:** Verified user

**Request**

Same as `POST /process/web` (shares the same handler).

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `url` | string | Yes | YouTube video URL. |
| Body | `collection_name` | string | No | Target collection name. |
| Query | `process` | bool | No | Embed content. Default `true`. |
| Query | `overwrite` | bool | No | Overwrite existing collection. Default `true`. |

**Response `200`**

Same schema as `POST /process/web`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Transcript fetch or embedding error. |
| 401 | Not authenticated. |

---

### POST /api/v1/retrieval/process/web/search

**Summary:** Perform one or more web searches and embed the results into a vector collection.

**Auth:** Verified user (requires `features.web_search` permission or admin role; `ENABLE_WEB_SEARCH` must be `true`)

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `queries` | array of strings | Yes | List of search queries to execute in parallel. |

**Response `200`**

```json
{
  "status": true,
  "collection_names": ["web-search-ab1234..."],
  "items": [
    { "link": "https://...", "title": "Page Title", "snippet": "..." }
  ],
  "filenames": ["https://example.com/page"],
  "loaded_count": 3
}
```

| Field | Type | Description |
|-------|------|-------------|
| `collection_names` | array | Vector collection names where results were stored. |
| `items` | array | Search result items with `link`, `title`, `snippet`. |
| `filenames` | array | URLs of pages successfully loaded. |
| `loaded_count` | int | Number of pages loaded. |

When `BYPASS_WEB_SEARCH_EMBEDDING_AND_RETRIEVAL` is enabled, `collection_names` is `null` and `docs` array is included in the response with raw content.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Search engine error. |
| 401 | Not authenticated / insufficient permission. |
| 403 | Web search feature disabled. |
| 404 | No search results found. |

---

### POST /api/v1/retrieval/process/files/batch

**Summary:** Process multiple files and embed them all into a single vector collection.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `files` | array of `FileModel` | Yes | Full file objects (id, filename, data, meta, user_id, etc.). |
| Body | `collection_name` | string | Yes | Target vector collection name. |

**Response `200`**

```json
{
  "results": [
    { "file_id": "abc123", "status": "completed" }
  ],
  "errors": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Per-file result: `file_id`, `status` (`prepared`, `completed`, or `failed`). |
| `errors` | array | Files that failed: `file_id`, `status`, `error` message. |

**Notes:** All documents are embedded in a single `save_docs_to_vector_db` call. File records are updated with the new collection name on success.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated. |

---

### POST /api/v1/retrieval/query/doc

**Summary:** Query a single vector collection for relevant document chunks.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `collection_name` | string | Yes | Name of the vector collection to query. |
| Body | `query` | string | Yes | Natural language query. |
| Body | `k` | int | No | Number of results to return. Defaults to `TOP_K`. |
| Body | `k_reranker` | int | No | Number of candidates for the reranker. Defaults to `TOP_K_RERANKER`. |
| Body | `r` | float | No | Relevance threshold. Defaults to `RELEVANCE_THRESHOLD`. |
| Body | `hybrid` | bool | No | Force hybrid search. Defaults to `ENABLE_RAG_HYBRID_SEARCH`. |

**Response `200`**

Array of document result objects from the vector store query, each containing `id`, `text`, `metadata`, and `distance` (or reranked score).

**Notes:** When hybrid search is enabled, uses BM25 + vector search and optionally reranks. When disabled, uses pure vector similarity.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Query error. |
| 401 | Not authenticated. |

---

### POST /api/v1/retrieval/query/collection

**Summary:** Query multiple vector collections and merge the results.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `collection_names` | array of strings | Yes | List of collection names to query. |
| Body | `query` | string | Yes | Natural language query. |
| Body | `k` | int | No | Number of results. Defaults to `TOP_K`. |
| Body | `k_reranker` | int | No | Reranker candidate count. Defaults to `TOP_K_RERANKER`. |
| Body | `r` | float | No | Relevance threshold. Defaults to `RELEVANCE_THRESHOLD`. |
| Body | `hybrid` | bool | No | Force hybrid search. |
| Body | `hybrid_bm25_weight` | float | No | BM25 weight override. Defaults to `HYBRID_BM25_WEIGHT`. |
| Body | `enable_enriched_texts` | bool | No | Use enriched text representations. Defaults to `ENABLE_RAG_HYBRID_SEARCH_ENRICHED_TEXTS`. |

**Response `200`**

Merged and ranked results from all queried collections.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Query error. |
| 401 | Not authenticated. |

---

### POST /api/v1/retrieval/delete

**Summary:** Delete vector entries for a specific file from a collection (admin only).

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | `collection_name` | string | Yes | Vector collection to delete from. |
| Body | `file_id` | string | Yes | File ID whose hash will be used to match and delete entries. |

**Response `200`**

```json
{ "status": true }
```

Returns `{ "status": false }` if the collection does not exist.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |
| 404 | File not found. |

---

### POST /api/v1/retrieval/reset/db

**Summary:** Reset the entire vector database and delete all knowledge base records (admin only).

**Auth:** Admin only

**Request**

No additional parameters.

**Response `200`**

No body.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |

---

### POST /api/v1/retrieval/reset/uploads

**Summary:** Delete all files in the upload directory (admin only).

**Auth:** Admin only

**Request**

No additional parameters.

**Response `200`**

```json
true
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not an admin. |
