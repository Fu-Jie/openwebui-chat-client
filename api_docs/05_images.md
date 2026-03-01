# Images API Reference

> **Base path prefix:** `/api/v1/images`
>
> Provides image generation and editing endpoints along with configuration management. The active engine for generation and editing are configured separately and each can be one of: `openai` (DALL-E / GPT-Image), `gemini` (Google Imagen), `comfyui` (ComfyUI), or `automatic1111` (Stable Diffusion Web UI). Generated images are stored in the server's file store and returned as internal file URLs.

---

### GET /api/v1/images/config

**Summary:** Retrieve the complete image generation and editing configuration including engine selection, model, size, API credentials, and backend-specific settings.

**Auth:** Admin only

**Request**

_No parameters._

**Response `200`**

```json
{
  "ENABLE_IMAGE_GENERATION": true,
  "ENABLE_IMAGE_PROMPT_GENERATION": true,
  "IMAGE_GENERATION_ENGINE": "openai",
  "IMAGE_GENERATION_MODEL": "dall-e-3",
  "IMAGE_SIZE": "1024x1024",
  "IMAGE_STEPS": 50,
  "IMAGES_OPENAI_API_BASE_URL": "https://api.openai.com/v1",
  "IMAGES_OPENAI_API_KEY": "sk-...",
  "IMAGES_OPENAI_API_VERSION": "",
  "IMAGES_OPENAI_API_PARAMS": null,
  "AUTOMATIC1111_BASE_URL": "http://localhost:7860",
  "AUTOMATIC1111_API_AUTH": null,
  "AUTOMATIC1111_PARAMS": null,
  "COMFYUI_BASE_URL": "http://localhost:8188",
  "COMFYUI_API_KEY": "",
  "COMFYUI_WORKFLOW": "{}",
  "COMFYUI_WORKFLOW_NODES": [],
  "IMAGES_GEMINI_API_BASE_URL": "https://generativelanguage.googleapis.com/v1beta",
  "IMAGES_GEMINI_API_KEY": "",
  "IMAGES_GEMINI_ENDPOINT_METHOD": "predict",
  "ENABLE_IMAGE_EDIT": false,
  "IMAGE_EDIT_ENGINE": "openai",
  "IMAGE_EDIT_MODEL": "gpt-image-1",
  "IMAGE_EDIT_SIZE": null,
  "IMAGES_EDIT_OPENAI_API_BASE_URL": "https://api.openai.com/v1",
  "IMAGES_EDIT_OPENAI_API_KEY": "",
  "IMAGES_EDIT_OPENAI_API_VERSION": "",
  "IMAGES_EDIT_GEMINI_API_BASE_URL": "https://generativelanguage.googleapis.com/v1beta",
  "IMAGES_EDIT_GEMINI_API_KEY": "",
  "IMAGES_EDIT_COMFYUI_BASE_URL": "http://localhost:8188",
  "IMAGES_EDIT_COMFYUI_API_KEY": "",
  "IMAGES_EDIT_COMFYUI_WORKFLOW": "{}",
  "IMAGES_EDIT_COMFYUI_WORKFLOW_NODES": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| ENABLE_IMAGE_GENERATION | boolean | Whether image generation is enabled |
| ENABLE_IMAGE_PROMPT_GENERATION | boolean | Whether AI-assisted prompt expansion is enabled |
| IMAGE_GENERATION_ENGINE | string | Active generation engine: `openai`, `gemini`, `comfyui`, `automatic1111`, or `""` (defaults to automatic1111) |
| IMAGE_GENERATION_MODEL | string | Default model name for generation |
| IMAGE_SIZE | string | Default output size in `WxH` format (e.g. `1024x1024`) or `"auto"` (only for models matching auto-size pattern) |
| IMAGE_STEPS | integer | Default diffusion steps (≥0); used for ComfyUI and Automatic1111 |
| IMAGES_OPENAI_API_BASE_URL | string | OpenAI-compatible API base URL for image generation |
| IMAGES_OPENAI_API_VERSION | string | Azure API version string (appended as `?api-version=...`) |
| IMAGES_OPENAI_API_PARAMS | object \| null | Extra parameters merged into every generation request |
| AUTOMATIC1111_BASE_URL | string | Automatic1111 Web UI base URL |
| AUTOMATIC1111_API_AUTH | string \| null | HTTP Basic auth string for Automatic1111 |
| AUTOMATIC1111_PARAMS | object \| null | Extra parameters merged into every Automatic1111 request |
| COMFYUI_BASE_URL | string | ComfyUI server base URL |
| COMFYUI_WORKFLOW | string | JSON string of the ComfyUI workflow template |
| COMFYUI_WORKFLOW_NODES | object[] | Workflow node configuration for prompt/model injection |
| IMAGES_GEMINI_API_BASE_URL | string | Google Generative Language API base URL |
| IMAGES_GEMINI_ENDPOINT_METHOD | string | Gemini API method: `"predict"` (Imagen) or `"generateContent"` |
| ENABLE_IMAGE_EDIT | boolean | Whether image editing is enabled |
| IMAGE_EDIT_ENGINE | string | Active editing engine: `openai`, `gemini`, `comfyui` |
| IMAGE_EDIT_MODEL | string | Default model for image editing |
| IMAGE_EDIT_SIZE | string \| null | Output size for edits (e.g. `1024x1024`) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/images/config/update

**Summary:** Persist image generation and editing configuration; validates IMAGE_SIZE format and IMAGE_STEPS range.

**Auth:** Admin only

**Request**

Same schema as the `GET /api/v1/images/config` response. All fields are required.

Validation rules:
- `IMAGE_SIZE` must be `"auto"`, `""`, or match `\d+x\d+` (e.g. `512x512`). `"auto"` is only allowed with specific model IDs.
- `IMAGE_STEPS` must be ≥ 0.

**Response `200`**

Same shape as `GET /api/v1/images/config`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid `IMAGE_SIZE` format or `IMAGE_STEPS` value |
| 401 | Not authenticated / not admin |

---

### GET /api/v1/images/config/url/verify

**Summary:** Verify that the configured image generation backend URL is reachable; for Automatic1111 and ComfyUI engines only.

**Auth:** Admin only

**Request**

_No parameters. Uses the current `IMAGE_GENERATION_ENGINE` setting._

**Response `200`**

```json
true
```

> For `automatic1111`: calls `GET {AUTOMATIC1111_BASE_URL}/sdapi/v1/options`.
> For `comfyui`: calls `GET {COMFYUI_BASE_URL}/object_info`.
> For other engines (e.g. `openai`, `gemini`): always returns `true` without making a network request.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Backend URL is unreachable (also disables image generation) |
| 401 | Not authenticated / not admin |

---

### GET /api/v1/images/models

**Summary:** Return the list of image generation models available for the configured engine.

**Auth:** Verified user

**Request**

_No parameters. Returns models for the currently configured `IMAGE_GENERATION_ENGINE`._

**Response `200`**

Array of model objects:
```json
[
  { "id": "dall-e-2", "name": "DALL·E 2" },
  { "id": "dall-e-3", "name": "DALL·E 3" },
  { "id": "gpt-image-1", "name": "GPT-IMAGE 1" }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Model identifier used in generation requests |
| name | string | Human-readable display name |

> **Engine behaviour:**
> - **`openai`** — Returns static list: `dall-e-2`, `dall-e-3`, `gpt-image-1`, `gpt-image-1.5`
> - **`gemini`** — Returns static list: `imagen-3.0-generate-002`
> - **`comfyui`** — Queries `GET {COMFYUI_BASE_URL}/object_info` and extracts checkpoint/model names from the workflow's model node
> - **`automatic1111`** / **`""`** — Queries `GET {AUTOMATIC1111_BASE_URL}/sdapi/v1/sd-models`

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Backend unreachable (also disables image generation) |
| 401 | Not authenticated |

---

### POST /api/v1/images/generations

**Summary:** Generate one or more images from a text prompt using the configured image generation engine; generated images are saved to the file store and returned as internal content URLs.

**Auth:** Verified user (requires `features.image_generation` permission or admin role)

> **Engine behaviour:**
> - **`openai`** — Calls `POST {IMAGES_OPENAI_API_BASE_URL}/images/generations`. Returns `b64_json` for non-URL-response models (DALL-E 2/3), or `url` for models matching `gpt-image-1`/`gpt-image-1.5`.
> - **`gemini`** — Calls `POST {IMAGES_GEMINI_API_BASE_URL}/models/{model}:{method}`. Supports `predict` (Imagen) and `generateContent` methods.
> - **`comfyui`** — Executes the configured workflow via ComfyUI API.
> - **`automatic1111`** / **`""`** — Calls `POST {AUTOMATIC1111_BASE_URL}/sdapi/v1/txt2img`.
>
> All generated images are uploaded to the server's file store. The response contains internal file content URLs.

**Request**

```json
{
  "prompt": "A photorealistic cat sitting on a bookshelf",
  "model": "dall-e-3",
  "n": 1,
  "size": "1024x1024",
  "steps": 50,
  "negative_prompt": "blurry, low quality"
}
```

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | prompt | string | Yes | Text description of the image to generate |
| Body | model | string | No | Model override; defaults to `IMAGE_GENERATION_MODEL` config |
| Body | n | integer | No | Number of images to generate (default: `1`) |
| Body | size | string | No | Output dimensions in `WxH` format (e.g. `1024x1024`); defaults to `IMAGE_SIZE` config |
| Body | steps | integer | No | Diffusion steps override; used by ComfyUI and Automatic1111 |
| Body | negative_prompt | string | No | Negative prompt (ComfyUI and Automatic1111 only) |

**Response `200`**

```json
[
  { "url": "/api/v1/files/c3f5a2e1-1234-5678-abcd-ef0123456789/content/generated-image.png" }
]
```

| Field | Type | Description |
|-------|------|-------------|
| (array) | object[] | One entry per generated image |
| [].url | string | Internal content URL to retrieve the generated image |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Generation failed (upstream error detail included) |
| 403 | Image generation disabled or user lacks permission |
| 401 | Not authenticated |

---

### POST /api/v1/images/edit

**Summary:** Edit one or more images using a text prompt with the configured image editing engine; supports OpenAI edits (gpt-image-1), Gemini generateContent, and ComfyUI workflows.

**Auth:** Verified user

> **Input image formats:** Each `image` value can be:
> - A base64 data URL (`data:image/png;base64,...`)
> - An HTTPS URL (fetched server-side; SSRF protection applies — private/local addresses are blocked)
> - An OpenWebUI file path (`/api/v1/files/{id}/content`) or bare file ID
>
> **Engine behaviour:**
> - **`openai`** — Calls `POST {IMAGES_EDIT_OPENAI_API_BASE_URL}/images/edits` as multipart/form-data. Supports single or multiple images (`image[]` parameter for arrays). Returns `b64_json` by default.
> - **`gemini`** — Calls `POST {IMAGES_EDIT_GEMINI_API_BASE_URL}/models/{model}:generateContent` with inline image data.
> - **`comfyui`** — Uploads image(s) to ComfyUI, then executes the configured edit workflow.

**Request**

```json
{
  "image": "data:image/png;base64,...",
  "prompt": "Add a sunset sky in the background",
  "model": "gpt-image-1",
  "size": "1024x1024",
  "n": 1,
  "negative_prompt": null,
  "background": "opaque"
}
```

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | image | string \| string[] | Yes | Source image(s) as base64 data URL, HTTPS URL, or file ID/path |
| Body | prompt | string | Yes | Edit instruction |
| Body | model | string | No | Model override; defaults to `IMAGE_EDIT_MODEL` config |
| Body | size | string | No | Output size in `WxH` format; defaults to `IMAGE_EDIT_SIZE` config |
| Body | n | integer | No | Number of output images |
| Body | negative_prompt | string | No | Negative prompt (ComfyUI only) |
| Body | background | string | No | Background handling: `"opaque"` or `"transparent"` (OpenAI gpt-image-1 only) |

**Response `200`**

```json
[
  { "url": "/api/v1/files/a1b2c3d4-5678-90ab-cdef-1234567890ab/content/generated-image.png" }
]
```

| Field | Type | Description |
|-------|------|-------------|
| (array) | object[] | One entry per output image |
| [].url | string | Internal content URL to retrieve the edited image |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid image input, SSRF-blocked URL, or upstream editing error |
| 401 | Not authenticated |
| 403 | Image editing disabled |
