# Configuration API

Base path: `/api/v1/configs`

All endpoints require **Admin** authentication unless noted.

---

### POST /api/v1/configs/import

**Summary:** Import a full configuration object and save it as the active config.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | config | object | Yes | Full config object matching exported format |

**Response `200`**

```json
{
  "ui": {},
  "auth": {},
  "models": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| (varies) | object | The resulting full config object after save |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 422 | Validation error |

---

### GET /api/v1/configs/export

**Summary:** Export the full active configuration as a JSON object.

**Auth:** Admin only

**Request** — no parameters.

**Response `200`**

```json
{
  "ui": { "default_locale": "en" },
  "auth": { "enable_api_keys": true }
}
```

| Field | Type | Description |
|-------|------|-------------|
| (varies) | object | Full config snapshot keyed by config path sections |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### GET /api/v1/configs/connections

**Summary:** Get direct-connection and base-model-cache settings.

**Auth:** Admin only

**Response `200`**

```json
{
  "ENABLE_DIRECT_CONNECTIONS": false,
  "ENABLE_BASE_MODELS_CACHE": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| ENABLE_DIRECT_CONNECTIONS | boolean | Allow users to connect directly to their own LLM endpoints |
| ENABLE_BASE_MODELS_CACHE | boolean | Cache base model list to improve performance |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/configs/connections

**Summary:** Update direct-connection and base-model-cache settings.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | ENABLE_DIRECT_CONNECTIONS | boolean | Yes | Enable/disable direct connections |
| Body | ENABLE_BASE_MODELS_CACHE | boolean | Yes | Enable/disable base-models cache |

**Response `200`** — same schema as GET `/configs/connections`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 422 | Validation error |

---

### POST /api/v1/configs/oauth/clients/register

**Summary:** Register an OAuth client via dynamic client registration for a tool server.

**Auth:** Admin only

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | No | Optional prefix type (e.g. `mcp`) |

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | url | string | Yes | OAuth server URL |
| Body | client_id | string | Yes | Client ID to register |
| Body | client_name | string | No | Human-readable client name |

**Response `200`**

```json
{
  "status": true,
  "oauth_client_info": "<encrypted_blob>"
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | boolean | Whether registration succeeded |
| oauth_client_info | string | Encrypted OAuth client information |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Failed to register OAuth client |
| 401 | Not authenticated / not admin |

---

### GET /api/v1/configs/tool_servers

**Summary:** Get the list of configured external tool server connections.

**Auth:** Admin only

**Response `200`**

```json
{
  "TOOL_SERVER_CONNECTIONS": [
    {
      "url": "http://tools.example.com",
      "path": "/openapi.json",
      "type": "openapi",
      "auth_type": "bearer",
      "key": "secret-token",
      "headers": null,
      "config": {}
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| TOOL_SERVER_CONNECTIONS | array | List of tool server connection objects |
| TOOL_SERVER_CONNECTIONS[].url | string | Base URL of the tool server |
| TOOL_SERVER_CONNECTIONS[].path | string | Path to OpenAPI spec or MCP endpoint |
| TOOL_SERVER_CONNECTIONS[].type | string | `openapi` or `mcp` |
| TOOL_SERVER_CONNECTIONS[].auth_type | string | `none`, `bearer`, `session`, `system_oauth`, `oauth_2.1` |
| TOOL_SERVER_CONNECTIONS[].key | string | Bearer token (if auth_type=bearer) |
| TOOL_SERVER_CONNECTIONS[].headers | object\|null | Extra HTTP headers |
| TOOL_SERVER_CONNECTIONS[].config | object | Additional config (type-specific) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/configs/tool_servers

**Summary:** Replace all tool server connection configurations.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | TOOL_SERVER_CONNECTIONS | array | Yes | Array of ToolServerConnection objects (same schema as GET) |

**Response `200`** — same schema as GET `/configs/tool_servers`.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 422 | Validation error |

---

### POST /api/v1/configs/tool_servers/verify

**Summary:** Verify connectivity to a single tool server connection.

**Auth:** Admin only

**Request** — single `ToolServerConnection` object (same schema as items in `TOOL_SERVER_CONNECTIONS` array).

**Response `200`**

```json
{
  "status": true,
  "specs": [ ... ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | boolean | Whether connection succeeded |
| specs | array | Tool specs fetched (MCP type) |
| oauth_server_metadata | object | OAuth discovery document (MCP + oauth_2.1) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Failed to connect to tool server or parse OAuth metadata |
| 401 | Not authenticated / not admin |

---

### GET /api/v1/configs/code_execution

**Summary:** Get code execution and code interpreter settings.

**Auth:** Admin only

**Response `200`**

```json
{
  "ENABLE_CODE_EXECUTION": false,
  "CODE_EXECUTION_ENGINE": "pyodide",
  "CODE_EXECUTION_JUPYTER_URL": null,
  "CODE_EXECUTION_JUPYTER_AUTH": null,
  "CODE_EXECUTION_JUPYTER_AUTH_TOKEN": null,
  "CODE_EXECUTION_JUPYTER_AUTH_PASSWORD": null,
  "CODE_EXECUTION_JUPYTER_TIMEOUT": null,
  "ENABLE_CODE_INTERPRETER": false,
  "CODE_INTERPRETER_ENGINE": "pyodide",
  "CODE_INTERPRETER_PROMPT_TEMPLATE": null,
  "CODE_INTERPRETER_JUPYTER_URL": null,
  "CODE_INTERPRETER_JUPYTER_AUTH": null,
  "CODE_INTERPRETER_JUPYTER_AUTH_TOKEN": null,
  "CODE_INTERPRETER_JUPYTER_AUTH_PASSWORD": null,
  "CODE_INTERPRETER_JUPYTER_TIMEOUT": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| ENABLE_CODE_EXECUTION | boolean | Enable inline code execution in chat |
| CODE_EXECUTION_ENGINE | string | Engine: `pyodide` or `jupyter` |
| CODE_EXECUTION_JUPYTER_URL | string\|null | Jupyter server URL (if engine=jupyter) |
| CODE_EXECUTION_JUPYTER_AUTH | string\|null | Auth method: `token` or `password` |
| CODE_EXECUTION_JUPYTER_AUTH_TOKEN | string\|null | Jupyter token (if auth=token) |
| CODE_EXECUTION_JUPYTER_AUTH_PASSWORD | string\|null | Jupyter password (if auth=password) |
| CODE_EXECUTION_JUPYTER_TIMEOUT | integer\|null | Execution timeout in seconds |
| ENABLE_CODE_INTERPRETER | boolean | Enable the AI code interpreter feature |
| CODE_INTERPRETER_ENGINE | string | Engine: `pyodide` or `jupyter` |
| CODE_INTERPRETER_PROMPT_TEMPLATE | string\|null | Custom prompt template for code interpreter |
| CODE_INTERPRETER_JUPYTER_URL | string\|null | Jupyter URL for interpreter |
| CODE_INTERPRETER_JUPYTER_AUTH | string\|null | Auth method for interpreter Jupyter |
| CODE_INTERPRETER_JUPYTER_AUTH_TOKEN | string\|null | Token for interpreter Jupyter |
| CODE_INTERPRETER_JUPYTER_AUTH_PASSWORD | string\|null | Password for interpreter Jupyter |
| CODE_INTERPRETER_JUPYTER_TIMEOUT | integer\|null | Timeout for interpreter Jupyter |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/configs/code_execution

**Summary:** Update code execution and code interpreter settings.

**Auth:** Admin only

**Request** — same body schema as GET `/configs/code_execution` response.

**Response `200`** — same schema as GET.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 422 | Validation error |

---

### GET /api/v1/configs/models

**Summary:** Get default model selection and ordering configuration.

**Auth:** Admin only

**Response `200`**

```json
{
  "DEFAULT_MODELS": null,
  "DEFAULT_PINNED_MODELS": null,
  "MODEL_ORDER_LIST": [],
  "DEFAULT_MODEL_METADATA": {},
  "DEFAULT_MODEL_PARAMS": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| DEFAULT_MODELS | string\|null | Comma-separated default model IDs shown to users |
| DEFAULT_PINNED_MODELS | string\|null | Comma-separated pinned model IDs |
| MODEL_ORDER_LIST | array | Ordered list of model IDs for display ordering |
| DEFAULT_MODEL_METADATA | object | Default metadata applied to all models |
| DEFAULT_MODEL_PARAMS | object | Default inference parameters (temperature, etc.) |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |

---

### POST /api/v1/configs/models

**Summary:** Update default model selection and ordering configuration.

**Auth:** Admin only

**Request** — same body schema as GET `/configs/models` response.

**Response `200`** — same schema as GET.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 422 | Validation error |

---

### POST /api/v1/configs/suggestions

**Summary:** Set the list of default prompt suggestions shown on the home screen.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | suggestions | array | Yes | List of PromptSuggestion objects |
| Body | suggestions[].title | array[string] | Yes | Display title lines (multiline support) |
| Body | suggestions[].content | string | Yes | Prompt text that is sent when clicked |

**Response `200`**

```json
[
  {
    "title": ["Explain", "this concept"],
    "content": "Explain the concept of recursion in simple terms."
  }
]
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 422 | Validation error |

---

### GET /api/v1/configs/banners

**Summary:** Get the list of UI banners displayed to all users.

**Auth:** Verified user

**Response `200`**

```json
[
  {
    "id": "banner-1",
    "type": "info",
    "title": "Maintenance",
    "content": "System maintenance at midnight.",
    "dismissible": true,
    "timestamp": 1710000000
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique banner identifier |
| type | string | `info`, `warning`, `error`, `success` |
| title | string | Banner headline |
| content | string | Banner body text |
| dismissible | boolean | Whether users can dismiss the banner |
| timestamp | integer | Unix epoch when banner was created |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |

---

### POST /api/v1/configs/banners

**Summary:** Replace the full list of UI banners.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | banners | array | Yes | List of BannerModel objects (same schema as GET response) |

**Response `200`** — updated banner list (same schema as GET).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated / not admin |
| 422 | Validation error |

---

## Appendix — All Config Fields

The table below enumerates all `PersistentConfig` fields in `backend/open_webui/config.py`, grouped by category.

### Authentication

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| ENABLE_API_KEYS | auth.enable_api_keys | `false` | Allow API key authentication |
| ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS | auth.api_keys_endpoint_restrictions | `false` | Restrict API keys to specific endpoints |
| API_KEYS_ALLOWED_ENDPOINTS | auth.api_keys_allowed_endpoints | `""` | Comma-separated allowed endpoint paths |
| JWT_EXPIRES_IN | auth.jwt_expiry | `"4w"` | JWT token TTL (e.g. `4w`, `24h`, `-1` = never) |
| ENABLE_SIGNUP | auth.enable_signup | `true` | Allow new user registration |
| ENABLE_LOGIN_FORM | ui.ENABLE_LOGIN_FORM | `true` | Show email/password login form |
| DEFAULT_USER_ROLE | ui.default_user_role | `"pending"` | Role assigned to new signups: `pending`, `user`, `admin` |
| DEFAULT_GROUP_ID | ui.default_group_id | `""` | Group automatically assigned to new users |
| PENDING_USER_OVERLAY_TITLE | ui.pending_user_overlay_title | `""` | Title shown to users awaiting approval |
| PENDING_USER_OVERLAY_CONTENT | ui.pending_user_overlay_content | `""` | Message shown to users awaiting approval |
| SHOW_ADMIN_DETAILS | auth.admin.show | `true` | Show admin contact info to unauthenticated users |
| ADMIN_EMAIL | auth.admin.email | `""` | Admin email shown on login page |
| ENABLE_LDAP | ldap.enable | `false` | Enable LDAP authentication |
| LDAP_SERVER_LABEL | ldap.server.label | `"LDAP Server"` | Display label for LDAP server |
| LDAP_SERVER_HOST | ldap.server.host | `"localhost"` | LDAP server hostname |
| LDAP_SERVER_PORT | ldap.server.port | `389` | LDAP server port |
| LDAP_ATTRIBUTE_FOR_MAIL | ldap.attributes.mail | `"mail"` | LDAP attribute containing email |
| LDAP_ATTRIBUTE_FOR_USERNAME | ldap.attributes.username | `"uid"` | LDAP attribute containing username |
| LDAP_APP_DN | ldap.app.dn | `""` | LDAP bind DN for app queries |
| LDAP_APP_PASSWORD | ldap.app.password | `""` | LDAP bind password |
| LDAP_SEARCH_BASE | ldap.search.base | `""` | LDAP search base DN |
| LDAP_SEARCH_FILTERS | ldap.search.filters | `""` | Additional LDAP search filters |
| LDAP_USE_TLS | ldap.tls.enable | `false` | Use TLS for LDAP |
| LDAP_CA_CERT_FILE | ldap.tls.ca_cert_file | `""` | Path to CA certificate file |
| LDAP_VALIDATE_CERT | ldap.tls.validate_cert | `true` | Validate LDAP TLS certificate |
| LDAP_CIPHERS | ldap.tls.ciphers | `"ALL"` | Allowed TLS cipher suites |
| ENABLE_LDAP_GROUP_MANAGEMENT | ldap.enable_group_management | `false` | Sync LDAP groups to Open WebUI |
| ENABLE_LDAP_GROUP_CREATION | ldap.enable_group_creation | `false` | Auto-create groups from LDAP |
| LDAP_ATTRIBUTE_FOR_GROUPS | ldap.attributes.groups | `"memberOf"` | LDAP attribute listing group membership |

### OAuth / SSO

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| ENABLE_OAUTH_SIGNUP | oauth.enable_signup | `false` | Allow account creation via OAuth |
| OAUTH_MERGE_ACCOUNTS_BY_EMAIL | oauth.merge_accounts_by_email | `false` | Merge existing account if emails match |
| GOOGLE_CLIENT_ID | oauth.google.client_id | `""` | Google OAuth client ID |
| GOOGLE_CLIENT_SECRET | oauth.google.client_secret | `""` | Google OAuth client secret |
| GOOGLE_OAUTH_SCOPE | oauth.google.scope | `"openid email profile"` | Google OAuth scopes |
| GOOGLE_REDIRECT_URI | oauth.google.redirect_uri | `""` | Google OAuth redirect URI |
| MICROSOFT_CLIENT_ID | oauth.microsoft.client_id | `""` | Microsoft OAuth client ID |
| MICROSOFT_CLIENT_SECRET | oauth.microsoft.client_secret | `""` | Microsoft OAuth client secret |
| MICROSOFT_CLIENT_TENANT_ID | oauth.microsoft.tenant_id | `""` | Azure AD tenant ID |
| MICROSOFT_OAUTH_SCOPE | oauth.microsoft.scope | `"openid email profile"` | Microsoft OAuth scopes |
| MICROSOFT_REDIRECT_URI | oauth.microsoft.redirect_uri | `""` | Microsoft OAuth redirect URI |
| GITHUB_CLIENT_ID | oauth.github.client_id | `""` | GitHub OAuth client ID |
| GITHUB_CLIENT_SECRET | oauth.github.client_secret | `""` | GitHub OAuth client secret |
| GITHUB_CLIENT_SCOPE | oauth.github.scope | `"user:email"` | GitHub OAuth scopes |
| GITHUB_CLIENT_REDIRECT_URI | oauth.github.redirect_uri | `""` | GitHub OAuth redirect URI |
| OAUTH_CLIENT_ID | oauth.oidc.client_id | `""` | Generic OIDC client ID |
| OAUTH_CLIENT_SECRET | oauth.oidc.client_secret | `""` | Generic OIDC client secret |
| OPENID_PROVIDER_URL | oauth.oidc.provider_url | `""` | OIDC discovery endpoint |
| OPENID_REDIRECT_URI | oauth.oidc.redirect_uri | `""` | OIDC redirect URI |
| OAUTH_SCOPES | oauth.oidc.scopes | `"openid email profile"` | OIDC scopes |
| OAUTH_TIMEOUT | oauth.oidc.oauth_timeout | `""` | OAuth request timeout |
| OAUTH_TOKEN_ENDPOINT_AUTH_METHOD | oauth.oidc.token_endpoint_auth_method | `null` | Token endpoint auth method |
| OAUTH_CODE_CHALLENGE_METHOD | oauth.oidc.code_challenge_method | `null` | PKCE challenge method |
| OAUTH_PROVIDER_NAME | oauth.oidc.provider_name | `"SSO"` | Display name for SSO button |
| OAUTH_SUB_CLAIM | oauth.oidc.sub_claim | `null` | JWT claim used as user subject |
| OAUTH_USERNAME_CLAIM | oauth.oidc.username_claim | `"name"` | JWT claim used as display name |
| OAUTH_PICTURE_CLAIM | oauth.oidc.avatar_claim | `"picture"` | JWT claim for avatar URL |
| OAUTH_EMAIL_CLAIM | oauth.oidc.email_claim | `"email"` | JWT claim for email |
| OAUTH_GROUPS_CLAIM | oauth.oidc.group_claim | varies | JWT claim listing groups |
| OAUTH_AUDIENCE | oauth.audience | `""` | Expected JWT audience |
| ENABLE_OAUTH_ROLE_MANAGEMENT | oauth.enable_role_mapping | `false` | Map OAuth roles to Open WebUI roles |
| OAUTH_ROLES_CLAIM | oauth.roles_claim | `"roles"` | JWT claim containing roles |
| OAUTH_ALLOWED_ROLES | oauth.allowed_roles | `["user","admin"]` | Roles allowed to sign in |
| OAUTH_ADMIN_ROLES | oauth.admin_roles | `["admin"]` | Roles mapped to admin |
| OAUTH_ALLOWED_DOMAINS | oauth.allowed_domains | `[]` | Restrict login to these email domains |
| ENABLE_OAUTH_GROUP_MANAGEMENT | oauth.enable_group_mapping | `false` | Sync OAuth groups to Open WebUI |
| ENABLE_OAUTH_GROUP_CREATION | oauth.enable_group_creation | `false` | Auto-create groups from OAuth |
| OAUTH_BLOCKED_GROUPS | oauth.blocked_groups | `[]` | Groups not allowed to sign in |
| OAUTH_GROUP_DEFAULT_SHARE | oauth.group_default_share | varies | Default sharing for OAuth-created groups |
| OAUTH_UPDATE_PICTURE_ON_LOGIN | oauth.update_picture_on_login | `false` | Re-sync avatar on every login |
| FEISHU_CLIENT_ID | oauth.feishu.client_id | `""` | Feishu OAuth client ID |
| FEISHU_CLIENT_SECRET | oauth.feishu.client_secret | `""` | Feishu OAuth client secret |
| FEISHU_OAUTH_SCOPE | oauth.feishu.scope | `"contact:user.base:read"` | Feishu OAuth scopes |
| FEISHU_REDIRECT_URI | oauth.feishu.redirect_uri | `""` | Feishu OAuth redirect URI |

### Models & Connections

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| ENABLE_OLLAMA_API | ollama.enable | `true` | Enable Ollama backend |
| OLLAMA_BASE_URLS | ollama.base_urls | env-derived | Comma-separated Ollama base URLs |
| OLLAMA_API_CONFIGS | ollama.api_configs | `{}` | Per-URL Ollama API settings |
| ENABLE_OPENAI_API | openai.enable | `true` | Enable OpenAI-compatible backend |
| OPENAI_API_KEYS | openai.api_keys | env-derived | OpenAI API keys (per URL) |
| OPENAI_API_BASE_URLS | openai.api_base_urls | env-derived | OpenAI API base URLs |
| OPENAI_API_CONFIGS | openai.api_configs | `{}` | Per-URL OpenAI API settings |
| ENABLE_DIRECT_CONNECTIONS | direct.enable | `false` | Allow user-supplied LLM connections |
| ENABLE_BASE_MODELS_CACHE | models.base_models_cache | `false` | Cache base model list |
| TOOL_SERVER_CONNECTIONS | tool_server.connections | `[]` | External tool server definitions |
| DEFAULT_MODELS | ui.default_models | `null` | Default model IDs (comma-separated) |
| DEFAULT_PINNED_MODELS | ui.default_pinned_models | `null` | Pinned model IDs (comma-separated) |
| MODEL_ORDER_LIST | ui.model_order_list | `[]` | Custom model display order |
| DEFAULT_MODEL_METADATA | models.default_metadata | `{}` | Metadata applied to every model |
| DEFAULT_MODEL_PARAMS | models.default_params | `{}` | Default inference parameters |

### UI & Branding

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| WEBUI_URL | webui.url | `""` | Public URL of this Open WebUI instance |
| DEFAULT_LOCALE | ui.default_locale | `""` | Default UI language (e.g. `en`, `fr`) |
| DEFAULT_PROMPT_SUGGESTIONS | ui.prompt_suggestions | built-in list | Home screen prompt suggestion cards |
| RESPONSE_WATERMARK | ui.watermark | `""` | Text appended to all AI responses |
| ENABLE_COMMUNITY_SHARING | ui.enable_community_sharing | `true` | Show "Share to community" option |
| ENABLE_MESSAGE_RATING | ui.enable_message_rating | `true` | Allow thumbs up/down on messages |
| ENABLE_USER_WEBHOOKS | ui.enable_user_webhooks | `true` | Allow users to configure webhooks |
| WEBHOOK_URL | webhook_url | `""` | System-wide webhook URL for events |
| WEBUI_BANNERS | ui.banners | `[]` | UI announcement banners |
| SHOW_ADMIN_DETAILS | auth.admin.show | `true` | Show admin email on login page |
| ADMIN_EMAIL | auth.admin.email | `""` | Admin contact email |
| ENABLE_FOLDERS | folders.enable | `true` | Enable chat folder organization |
| FOLDER_MAX_FILE_COUNT | folders.max_file_count | `""` | Max files per folder (empty = unlimited) |
| ENABLE_CHANNELS | channels.enable | `false` | Enable group channels feature |
| ENABLE_NOTES | notes.enable | `true` | Enable user notes feature |
| ENABLE_USER_STATUS | users.enable_status | `true` | Show user online/status indicators |

### Tasks & Generation

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| TASK_MODEL | task.model.internal | `""` | Model used for background tasks (internal) |
| TASK_MODEL_EXTERNAL | task.model.external | `""` | Model used for background tasks (external) |
| TITLE_GENERATION_PROMPT_TEMPLATE | task.title.prompt_template | built-in | Prompt template for generating chat titles |
| ENABLE_TITLE_GENERATION | task.title.enable | `true` | Auto-generate chat titles |
| TAGS_GENERATION_PROMPT_TEMPLATE | task.tags.prompt_template | built-in | Prompt template for generating tags |
| ENABLE_TAGS_GENERATION | task.tags.enable | `true` | Auto-generate conversation tags |
| ENABLE_SEARCH_QUERY_GENERATION | task.query.enable | `true` | Auto-generate search queries from messages |
| ENABLE_RETRIEVAL_QUERY_GENERATION | task.retrieval_query.enable | `true` | Auto-generate retrieval queries |
| QUERY_GENERATION_PROMPT_TEMPLATE | task.query.prompt_template | built-in | Prompt template for query generation |
| ENABLE_FOLLOW_UP_GENERATION | task.follow_up.enable | `false` | Auto-generate follow-up questions |
| FOLLOW_UP_GENERATION_PROMPT_TEMPLATE | task.follow_up.prompt_template | built-in | Prompt template for follow-up questions |
| ENABLE_AUTOCOMPLETE_GENERATION | task.autocomplete.enable | `false` | Enable chat autocomplete suggestions |
| AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH | task.autocomplete.input_max_length | `1000` | Max input length for autocomplete |
| AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE | task.autocomplete.prompt_template | built-in | Prompt template for autocomplete |
| IMAGE_PROMPT_GENERATION_PROMPT_TEMPLATE | task.image_prompt.prompt_template | built-in | Prompt template for image prompts |
| ENABLE_IMAGE_PROMPT_GENERATION | task.image_prompt.enable | `true` | Auto-generate image prompts |
| VOICE_MODE_PROMPT_TEMPLATE | task.voice_mode.prompt_template | built-in | System prompt for voice mode |
| TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE | task.tools.prompt_template | built-in | Prompt template for tool/function calling |

### Code Execution

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| ENABLE_CODE_EXECUTION | code_execution.enable | `false` | Enable inline code execution |
| CODE_EXECUTION_ENGINE | code_execution.engine | `"pyodide"` | Engine: `pyodide` or `jupyter` |
| CODE_EXECUTION_JUPYTER_URL | code_execution.jupyter.url | `""` | Jupyter server URL |
| CODE_EXECUTION_JUPYTER_AUTH | code_execution.jupyter.auth | `""` | Auth method: `token` or `password` |
| CODE_EXECUTION_JUPYTER_AUTH_TOKEN | code_execution.jupyter.auth_token | `""` | Jupyter token |
| CODE_EXECUTION_JUPYTER_AUTH_PASSWORD | code_execution.jupyter.auth_password | `""` | Jupyter password |
| CODE_EXECUTION_JUPYTER_TIMEOUT | code_execution.jupyter.timeout | `60` | Execution timeout (seconds) |
| ENABLE_CODE_INTERPRETER | code_interpreter.enable | `false` | Enable AI code interpreter |
| CODE_INTERPRETER_ENGINE | code_interpreter.engine | `"pyodide"` | Interpreter engine |
| CODE_INTERPRETER_PROMPT_TEMPLATE | code_interpreter.prompt_template | built-in | System prompt for code interpreter |
| CODE_INTERPRETER_JUPYTER_URL | code_interpreter.jupyter.url | `""` | Jupyter URL for interpreter |
| CODE_INTERPRETER_JUPYTER_AUTH | code_interpreter.jupyter.auth | `""` | Auth method for interpreter Jupyter |
| CODE_INTERPRETER_JUPYTER_AUTH_TOKEN | code_interpreter.jupyter.auth_token | `""` | Token for interpreter Jupyter |
| CODE_INTERPRETER_JUPYTER_AUTH_PASSWORD | code_interpreter.jupyter.auth_password | `""` | Password for interpreter Jupyter |
| CODE_INTERPRETER_JUPYTER_TIMEOUT | code_interpreter.jupyter.timeout | `60` | Timeout for interpreter Jupyter |

### Evaluations & Permissions

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| ENABLE_EVALUATION_ARENA_MODELS | evaluation.arena.enable | `true` | Enable arena (A/B comparison) mode |
| EVALUATION_ARENA_MODELS | evaluation.arena.models | `[]` | Models available in arena mode |
| USER_PERMISSIONS | user.permissions | built-in object | Granular per-feature permission flags |

### RAG / Retrieval

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| RAG_TEMPLATE | rag.template | built-in | Prompt template injected with retrieved context |
| RAG_OPENAI_API_BASE_URL | rag.openai.api_base_url | `""` | OpenAI API URL for RAG embeddings |
| RAG_OPENAI_API_KEY | rag.openai.api_key | `""` | API key for RAG OpenAI embeddings |
| RAG_AZURE_OPENAI_BASE_URL | rag.azure.api_base_url | `""` | Azure OpenAI URL for RAG |
| RAG_AZURE_OPENAI_API_KEY | rag.azure.api_key | `""` | Azure OpenAI key for RAG |
| RAG_AZURE_OPENAI_API_VERSION | rag.azure.api_version | `""` | Azure OpenAI API version |
| RAG_OLLAMA_BASE_URL | rag.ollama.url | `""` | Ollama URL for RAG embeddings |
| RAG_OLLAMA_API_KEY | rag.ollama.key | `""` | Ollama API key for RAG |
| CHUNK_MIN_SIZE_TARGET | rag.chunk.min_size | `100` | Min target chunk size for document splitting |
| CHUNK_OVERLAP | rag.chunk.overlap | `100` | Chunk overlap for document splitting |

### Web Search

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| ENABLE_WEB_SEARCH | rag.web.search.enable | `false` | Enable web search in RAG |
| WEB_SEARCH_ENGINE | rag.web.search.engine | `""` | Search engine: `searxng`, `google_pse`, `brave`, etc. |
| WEB_SEARCH_RESULT_COUNT | rag.web.search.result_count | `3` | Number of results to fetch per query |
| WEB_SEARCH_DOMAIN_FILTER_LIST | rag.web.search.domain_filter_list | `[]` | Blocked domains for web search |
| WEB_SEARCH_CONCURRENT_REQUESTS | rag.web.search.concurrent_requests | `10` | Max concurrent web search requests |
| WEB_LOADER_ENGINE | rag.web.loader.engine | `""` | Web page loader engine |
| YOUTUBE_LOADER_LANGUAGE | rag.content.youtube.language | `["en"]` | Preferred languages for YouTube transcripts |
| SEARXNG_QUERY_URL | rag.web.search.searxng_query_url | `""` | SearXNG instance query URL |
| GOOGLE_PSE_API_KEY | rag.web.search.google_pse_api_key | `""` | Google PSE API key |
| GOOGLE_PSE_ENGINE_ID | rag.web.search.google_pse_engine_id | `""` | Google PSE engine ID |
| BRAVE_SEARCH_API_KEY | rag.web.search.brave_search_api_key | `""` | Brave Search API key |
| PERPLEXITY_API_KEY | rag.web.search.perplexity_api_key | `""` | Perplexity API key |
| TAVILY_API_KEY | rag.web.search.tavily_api_key | `""` | Tavily API key |
| EXA_API_KEY | rag.web.search.exa_api_key | `""` | Exa search API key |
| SERPER_API_KEY | rag.web.search.serper_api_key | `""` | Serper API key |
| SERPAPI_API_KEY | rag.web.search.serpapi_api_key | `""` | SerpAPI key |
| BING_SEARCH_V7_SUBSCRIPTION_KEY | rag.web.search.bing_search_v7_subscription_key | `""` | Bing Search v7 subscription key |
| JINA_API_KEY | rag.web.search.jina_api_key | `""` | Jina AI search API key |

### Image Generation

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| ENABLE_IMAGE_GENERATION | image_generation.enable | `false` | Enable image generation feature |
| IMAGE_GENERATION_ENGINE | image_generation.engine | `""` | Engine: `openai`, `comfyui`, `automatic1111`, `gemini` |
| IMAGE_GENERATION_MODEL | image_generation.model | `""` | Default model for image generation |
| IMAGE_SIZE | image_generation.image_size | `"512x512"` | Default output image size |
| IMAGE_STEPS | image_generation.steps | `50` | Default diffusion steps |
| AUTOMATIC1111_BASE_URL | image_generation.automatic1111.base_url | `""` | Automatic1111 server URL |
| COMFYUI_BASE_URL | image_generation.comfyui.base_url | `""` | ComfyUI server URL |
| IMAGES_OPENAI_API_BASE_URL | image_generation.openai.api_base_url | `""` | OpenAI Images API URL |
| IMAGES_OPENAI_API_KEY | image_generation.openai.api_key | `""` | OpenAI Images API key |
| IMAGES_GEMINI_API_KEY | image_generation.gemini.api_key | `""` | Gemini image generation API key |

### Audio (STT / TTS)

| Field | Config Path | Default | Description |
|-------|------------|---------|-------------|
| WHISPER_MODEL | audio.stt.whisper_model | `"base"` | Whisper model name for local STT |
| DEEPGRAM_API_KEY | audio.stt.deepgram.api_key | `""` | Deepgram API key |
| AUDIO_STT_ENGINE | audio.stt.engine | `""` | STT engine: `openai`, `deepgram`, `azure`, `whisper` |
| AUDIO_STT_MODEL | audio.stt.model | `"whisper-1"` | STT model identifier |
| AUDIO_STT_OPENAI_API_BASE_URL | audio.stt.openai.api_base_url | `""` | OpenAI STT base URL |
| AUDIO_STT_OPENAI_API_KEY | audio.stt.openai.api_key | `""` | OpenAI STT API key |
| AUDIO_TTS_ENGINE | audio.tts.engine | `""` | TTS engine: `openai`, `azure`, `elevenlabs` |
| AUDIO_TTS_MODEL | audio.tts.model | `"tts-1"` | TTS model identifier |
| AUDIO_TTS_VOICE | audio.tts.voice | `"alloy"` | Default TTS voice |
| AUDIO_TTS_OPENAI_API_BASE_URL | audio.tts.openai.api_base_url | `""` | OpenAI TTS base URL |
| AUDIO_TTS_OPENAI_API_KEY | audio.tts.openai.api_key | `""` | OpenAI TTS API key |
| AUDIO_TTS_AZURE_SPEECH_REGION | audio.tts.azure.speech_region | `""` | Azure Speech region |
| AUDIO_TTS_AZURE_SPEECH_BASE_URL | audio.tts.azure.speech_base_url | `""` | Azure Speech custom endpoint |
