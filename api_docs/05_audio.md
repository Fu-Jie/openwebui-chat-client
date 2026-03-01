# Audio API Reference

> **Base path prefix:** `/api/v1/audio`
>
> Provides text-to-speech (TTS), speech-to-text (STT) transcription, and audio configuration endpoints. The active engine is configured per TTS/STT separately and can be one of: `openai`, `elevenlabs`, `azure`, `transformers` (TTS) or `openai`, `deepgram`, `azure`, `mistral` (STT). An empty engine string uses the built-in `faster-whisper` model for STT.

---

### GET /api/v1/audio/config

**Summary:** Retrieve the full TTS and STT configuration including engine type, model, voice, and provider-specific API settings.

**Auth:** Admin only

**Request**

_No parameters._

**Response `200`**

```json
{
  "tts": {
    "OPENAI_API_BASE_URL": "https://api.openai.com/v1",
    "OPENAI_API_KEY": "sk-...",
    "OPENAI_PARAMS": null,
    "API_KEY": "",
    "ENGINE": "openai",
    "MODEL": "tts-1",
    "VOICE": "alloy",
    "SPLIT_ON": "punctuation",
    "AZURE_SPEECH_REGION": "",
    "AZURE_SPEECH_BASE_URL": "",
    "AZURE_SPEECH_OUTPUT_FORMAT": "audio-16khz-128kbitrate-mono-mp3"
  },
  "stt": {
    "OPENAI_API_BASE_URL": "https://api.openai.com/v1",
    "OPENAI_API_KEY": "sk-...",
    "ENGINE": "openai",
    "MODEL": "whisper-1",
    "SUPPORTED_CONTENT_TYPES": ["audio/mpeg", "audio/wav", "audio/webm"],
    "WHISPER_MODEL": "base",
    "DEEPGRAM_API_KEY": "",
    "AZURE_API_KEY": "",
    "AZURE_REGION": "",
    "AZURE_LOCALES": "",
    "AZURE_BASE_URL": "",
    "AZURE_MAX_SPEAKERS": "",
    "MISTRAL_API_KEY": "",
    "MISTRAL_API_BASE_URL": "",
    "MISTRAL_USE_CHAT_COMPLETIONS": false
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| tts.ENGINE | string | Active TTS engine (`openai`, `elevenlabs`, `azure`, `transformers`) |
| tts.MODEL | string | TTS model name |
| tts.VOICE | string | Default voice ID |
| tts.SPLIT_ON | string | How to split long text: `punctuation` or `none` |
| tts.AZURE_SPEECH_REGION | string | Azure region code (e.g. `eastus`) |
| tts.AZURE_SPEECH_OUTPUT_FORMAT | string | Azure TTS output codec format |
| stt.ENGINE | string | Active STT engine (`openai`, `deepgram`, `azure`, `mistral`, or `""` for built-in whisper) |
| stt.MODEL | string | STT model name |
| stt.SUPPORTED_CONTENT_TYPES | string[] | MIME types accepted for transcription uploads |
| stt.WHISPER_MODEL | string | Built-in faster-whisper model size (`tiny`, `base`, `small`, `medium`, `large`) |
| stt.MISTRAL_USE_CHAT_COMPLETIONS | boolean | Use Mistral chat-completions endpoint for transcription instead of dedicated STT endpoint |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/audio/config/update

**Summary:** Persist updated TTS and STT configuration; reloads the faster-whisper model when STT engine is set to built-in.

**Auth:** Admin only

**Request**

```json
{
  "tts": {
    "OPENAI_API_BASE_URL": "https://api.openai.com/v1",
    "OPENAI_API_KEY": "sk-...",
    "OPENAI_PARAMS": null,
    "API_KEY": "",
    "ENGINE": "openai",
    "MODEL": "tts-1",
    "VOICE": "alloy",
    "SPLIT_ON": "punctuation",
    "AZURE_SPEECH_REGION": "",
    "AZURE_SPEECH_BASE_URL": "",
    "AZURE_SPEECH_OUTPUT_FORMAT": "audio-16khz-128kbitrate-mono-mp3"
  },
  "stt": {
    "OPENAI_API_BASE_URL": "https://api.openai.com/v1",
    "OPENAI_API_KEY": "sk-...",
    "ENGINE": "openai",
    "MODEL": "whisper-1",
    "SUPPORTED_CONTENT_TYPES": ["audio/mpeg", "audio/wav"],
    "WHISPER_MODEL": "base",
    "DEEPGRAM_API_KEY": "",
    "AZURE_API_KEY": "",
    "AZURE_REGION": "",
    "AZURE_LOCALES": "",
    "AZURE_BASE_URL": "",
    "AZURE_MAX_SPEAKERS": "",
    "MISTRAL_API_KEY": "",
    "MISTRAL_API_BASE_URL": "",
    "MISTRAL_USE_CHAT_COMPLETIONS": false
  }
}
```

All fields mirror the `GET /api/v1/audio/config` response. See that endpoint for field descriptions.

**Response `200`**

Same shape as `GET /api/v1/audio/config`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/audio/speech

**Summary:** Synthesize speech from text using the configured TTS engine; results are cached on disk by a hash of the input body + engine + model.

**Auth:** Verified user (requires `chat.tts` permission or admin role)

> **Supported engines:**
> - **`openai`** — Proxies to configured `TTS_OPENAI_API_BASE_URL/audio/speech`
> - **`elevenlabs`** — Calls ElevenLabs text-to-speech API
> - **`azure`** — Calls Azure Cognitive Services TTS using SSML
> - **`transformers`** — Uses local HuggingFace `speecht5_tts` pipeline

**Request**

JSON body (passed through to the upstream TTS provider):

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | input | string | Yes | Text to synthesize |
| Body | voice | string | No | Voice ID; must be a valid voice for the configured engine |
| Body | model | string | No | TTS model override (the server may override this with the configured model) |
| Body | speed | number | No | Playback speed (OpenAI engine only; 0.25–4.0) |

> For the `elevenlabs` engine, `voice` must be a valid ElevenLabs voice ID.
> For the `azure` engine, `voice` is the Azure voice short name (e.g. `en-US-JennyNeural`).

**Response `200`**

Audio file response (MP3). If the same request was made before, the cached file is returned directly.

| Header | Value |
|--------|-------|
| Content-Type | `audio/mpeg` |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid JSON payload |
| 403 | User does not have TTS permission |
| 404 | TTS engine not configured |
| 500 | Upstream TTS provider error |

---

### POST /api/v1/audio/transcriptions

**Summary:** Transcribe an uploaded audio file to text using the configured STT engine; supports OpenAI Whisper, Deepgram, Azure, Mistral, and built-in faster-whisper.

**Auth:** Verified user (requires `chat.stt` permission or admin role)

**Content-Type:** `multipart/form-data`

> **Supported audio formats (MIME types):** Configured via `STT_SUPPORTED_CONTENT_TYPES` in audio config. Default includes: `audio/mpeg`, `audio/mp4`, `audio/wav`, `audio/webm`, `audio/flac`, `audio/x-m4a`, `audio/mpeg`, `video/mp4`, `video/mpeg`, `video/webm`.
>
> Files that require conversion (e.g. AAC/mp4a) are automatically converted to MP3 before transcription.

> **Supported engines:**
> - **`""`** (empty) — Built-in faster-whisper (local inference)
> - **`openai`** — OpenAI Whisper API (or compatible endpoint)
> - **`deepgram`** — Deepgram speech recognition API
> - **`azure`** — Azure Speech-to-Text service
> - **`mistral`** — Mistral AI STT or chat-completion based transcription

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Form (multipart) | file | file | Yes | Audio file to transcribe |
| Form (multipart) | language | string | No | BCP-47 language code hint (e.g. `en`, `ja`); auto-detected if omitted |

**Response `200`**

```json
{
  "text": "Hello, this is a transcription.",
  "filename": "c3f5a2e1-1234-5678-abcd-ef0123456789.mp3"
}
```

| Field | Type | Description |
|-------|------|-------------|
| text | string | Transcribed text |
| filename | string | Internal filename of the uploaded audio in the cache directory |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Unsupported file content type, or transcription failed |
| 403 | User does not have STT permission |
| 500 | Upstream STT provider error |

---

### GET /api/v1/audio/models

**Summary:** Return available TTS models for the configured TTS engine.

**Auth:** Verified user

**Request**

_No parameters._

**Response `200`**

```json
{
  "models": [
    { "id": "tts-1", "name": "tts-1" },
    { "id": "tts-1-hd", "name": "tts-1-hd" }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| models | object[] | List of available TTS models |
| models[].id | string | Model identifier |
| models[].name | string | Display name |

> **Engine behaviour:**
> - **`openai`** — Returns `tts-1` and `tts-1-hd` (or fetches from custom endpoint if not api.openai.com)
> - **`elevenlabs`** — Fetches model list from ElevenLabs API
> - Other engines — Returns empty list

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### GET /api/v1/audio/voices

**Summary:** Return available TTS voices for the configured TTS engine.

**Auth:** Verified user

**Request**

_No parameters._

**Response `200`**

```json
{
  "voices": [
    { "id": "alloy", "name": "alloy" },
    { "id": "echo", "name": "echo" },
    { "id": "fable", "name": "fable" },
    { "id": "onyx", "name": "onyx" },
    { "id": "nova", "name": "nova" },
    { "id": "shimmer", "name": "shimmer" }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| voices | object[] | List of available TTS voices |
| voices[].id | string | Voice identifier used in synthesis requests |
| voices[].name | string | Display name |

> **Engine behaviour:**
> - **`openai`** — Returns standard OpenAI voices (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`); or fetches from custom endpoint if not api.openai.com
> - **`elevenlabs`** — Fetches voice list from ElevenLabs API (voice_id → name)
> - **`azure`** — Fetches voice list from Azure Cognitive Services (ShortName → DisplayName)
> - Other engines — Returns empty list

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
