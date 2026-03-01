# Authentication API Reference

Base path: `/api/v1/auths`

---

### GET /api/v1/auths/

**Summary:** Returns the current session user's profile, token, and permissions.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

**Response `200`**

```json
{
  "token": "eyJ...",
  "token_type": "Bearer",
  "expires_at": 1700000000,
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "profile_image_url": "/api/v1/users/user_id/profile/image",
  "bio": null,
  "gender": null,
  "date_of_birth": null,
  "status_emoji": null,
  "status_message": null,
  "status_expires_at": null,
  "permissions": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| token | string | JWT access token |
| token_type | string | Always `"Bearer"` |
| expires_at | integer \| null | Unix epoch expiry; null if no expiry |
| id | string | User ID |
| email | string | User email |
| name | string | Display name |
| role | string | User role (`admin`, `user`, `pending`) |
| profile_image_url | string | Profile image path or URL |
| bio | string \| null | Optional bio |
| gender | string \| null | Optional gender |
| date_of_birth | string \| null | ISO date (YYYY-MM-DD) |
| status_emoji | string \| null | Status emoji |
| status_message | string \| null | Status message text |
| status_expires_at | integer \| null | Status expiry (epoch) |
| permissions | object | User permission map |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Token invalid or expired |

---

### POST /api/v1/auths/update/profile

**Summary:** Updates the current user's display name and profile image.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | profile_image_url | string | Yes | New profile image URL or base64 data URI |
| Body | name | string | Yes | New display name |
| Body | bio | string | No | User bio |
| Body | gender | string | No | Gender |
| Body | date_of_birth | string | No | ISO date (YYYY-MM-DD) |

**Response `200`**

```json
{
  "id": "user_id",
  "name": "Jane Doe",
  "role": "user",
  "email": "user@example.com",
  "profile_image_url": "/api/v1/users/user_id/profile/image"
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | User ID |
| name | string | Updated display name |
| role | string | User role |
| email | string | User email |
| profile_image_url | string | Profile image path |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid credentials or update failed |
| 401 | Not authenticated |

---

### POST /api/v1/auths/update/timezone

**Summary:** Updates the current user's timezone setting.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | timezone | string | Yes | IANA timezone string (e.g. `"America/New_York"`) |

**Response `200`**

```json
{
  "status": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | boolean | `true` on success |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid credentials |
| 401 | Not authenticated |

---

### POST /api/v1/auths/update/password

**Summary:** Changes the current user's password.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | password | string | Yes | Current password |
| Body | new_password | string | Yes | New password (must pass validation rules) |

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
| 400 | Incorrect current password, validation error, or action prohibited (trusted header mode) |
| 401 | Not authenticated |

---

### POST /api/v1/auths/ldap

**Summary:** Authenticates a user via LDAP and returns a session token.

**Auth:** Public

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | user | string | Yes | LDAP username |
| Body | password | string | Yes | LDAP password |

**Response `200`**

```json
{
  "token": "eyJ...",
  "token_type": "Bearer",
  "expires_at": 1700000000,
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "profile_image_url": "/api/v1/users/user_id/profile/image",
  "permissions": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| token | string | JWT access token |
| token_type | string | Always `"Bearer"` |
| expires_at | integer \| null | Unix epoch expiry |
| id | string | User ID |
| email | string | User email |
| name | string | Display name |
| role | string | User role |
| profile_image_url | string | Profile image path |
| permissions | object | User permission map |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | LDAP not enabled, authentication failed, or user not found in LDAP |
| 403 | Password authentication disabled |

---

### POST /api/v1/auths/signin

**Summary:** Authenticates a user with email and password and returns a session token.

**Auth:** Public

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | email | string | Yes | User email address |
| Body | password | string | Yes | User password |

**Response `200`**

```json
{
  "token": "eyJ...",
  "token_type": "Bearer",
  "expires_at": 1700000000,
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "profile_image_url": "/api/v1/users/user_id/profile/image",
  "permissions": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| token | string | JWT access token |
| token_type | string | Always `"Bearer"` |
| expires_at | integer \| null | Unix epoch expiry |
| id | string | User ID |
| email | string | User email |
| name | string | Display name |
| role | string | User role |
| profile_image_url | string | Profile image path |
| permissions | object | User permission map |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid credentials or missing trusted header |
| 403 | Password authentication disabled |
| 429 | Rate limit exceeded (5 attempts per 3 minutes) |

---

### POST /api/v1/auths/signup

**Summary:** Registers a new user account.

**Auth:** Public

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | name | string | Yes | Display name |
| Body | email | string | Yes | Email address |
| Body | password | string | Yes | Password (must pass validation rules) |
| Body | profile_image_url | string | No | Profile image URL or data URI (defaults to `"/user.png"`) |

**Response `200`**

```json
{
  "token": "eyJ...",
  "token_type": "Bearer",
  "expires_at": 1700000000,
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "profile_image_url": "/api/v1/users/user_id/profile/image",
  "permissions": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| token | string | JWT access token |
| token_type | string | Always `"Bearer"` |
| expires_at | integer \| null | Unix epoch expiry |
| id | string | New user ID |
| email | string | User email |
| name | string | Display name |
| role | string | Assigned role (`admin` for first user, otherwise default role) |
| profile_image_url | string | Profile image path |
| permissions | object | User permission map |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Email taken, invalid email format, or password validation failed |
| 403 | Signup disabled or access prohibited |
| 500 | Internal error during user creation |

---

### GET /api/v1/auths/signout

**Summary:** Signs out the current user by invalidating the token and clearing auth cookies.

**Auth:** Public

**Request**

No additional parameters.

**Response `200`**

```json
{
  "status": true
}
```

Or if an OAuth OIDC logout URL is found or a redirect URL is configured:

```json
{
  "status": true,
  "redirect_url": "https://provider.example.com/logout?..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | boolean | `true` on success |
| redirect_url | string \| null | Client-side logout redirect URL if applicable |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 500 | Failed to sign out from OpenID provider |

---

### POST /api/v1/auths/add

**Summary:** Creates a new user account as an admin.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | name | string | Yes | Display name |
| Body | email | string | Yes | Email address |
| Body | password | string | Yes | Password |
| Body | profile_image_url | string | No | Profile image URL (defaults to `"/user.png"`) |
| Body | role | string | No | User role (`pending`, `user`, `admin`; defaults to `"pending"`) |

**Response `200`**

```json
{
  "token": "eyJ...",
  "token_type": "Bearer",
  "id": "user_id",
  "email": "user@example.com",
  "name": "New User",
  "role": "pending",
  "profile_image_url": "/api/v1/users/user_id/profile/image"
}
```

| Field | Type | Description |
|-------|------|-------------|
| token | string | JWT access token for the new user |
| token_type | string | Always `"Bearer"` |
| id | string | New user ID |
| email | string | User email |
| name | string | Display name |
| role | string | Assigned role |
| profile_image_url | string | Profile image path |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid email format, email taken, or password validation failed |
| 401 | Not authenticated |
| 403 | Insufficient permissions |
| 500 | Internal error during user creation |

---

### GET /api/v1/auths/admin/details

**Summary:** Returns the primary admin user's name and email.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

**Response `200`**

```json
{
  "name": "Admin User",
  "email": "admin@example.com"
}
```

| Field | Type | Description |
|-------|------|-------------|
| name | string \| null | Admin display name |
| email | string \| null | Admin email |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | `SHOW_ADMIN_DETAILS` is disabled |
| 401 | Not authenticated |

---

### GET /api/v1/auths/admin/config

**Summary:** Returns the current global admin configuration.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

**Response `200`**

```json
{
  "SHOW_ADMIN_DETAILS": true,
  "ADMIN_EMAIL": "admin@example.com",
  "WEBUI_URL": "https://example.com",
  "ENABLE_SIGNUP": true,
  "ENABLE_API_KEYS": true,
  "ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS": false,
  "API_KEYS_ALLOWED_ENDPOINTS": "",
  "DEFAULT_USER_ROLE": "user",
  "DEFAULT_GROUP_ID": "",
  "JWT_EXPIRES_IN": "-1",
  "ENABLE_COMMUNITY_SHARING": true,
  "ENABLE_MESSAGE_RATING": true,
  "ENABLE_FOLDERS": true,
  "FOLDER_MAX_FILE_COUNT": null,
  "ENABLE_CHANNELS": false,
  "ENABLE_MEMORIES": true,
  "ENABLE_NOTES": true,
  "ENABLE_USER_WEBHOOKS": false,
  "ENABLE_USER_STATUS": false,
  "PENDING_USER_OVERLAY_TITLE": null,
  "PENDING_USER_OVERLAY_CONTENT": null,
  "RESPONSE_WATERMARK": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| SHOW_ADMIN_DETAILS | boolean | Whether admin details are shown to users |
| ADMIN_EMAIL | string \| null | Admin email override |
| WEBUI_URL | string | Public URL of the WebUI |
| ENABLE_SIGNUP | boolean | Whether new signups are allowed |
| ENABLE_API_KEYS | boolean | Whether API key generation is allowed |
| ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS | boolean | Whether API key endpoint restrictions are enabled |
| API_KEYS_ALLOWED_ENDPOINTS | string | Comma-separated allowed endpoints for API keys |
| DEFAULT_USER_ROLE | string | Default role for new users |
| DEFAULT_GROUP_ID | string | Default group assigned to new users |
| JWT_EXPIRES_IN | string | JWT expiry duration (e.g. `"1h"`, `"-1"` for no expiry) |
| ENABLE_COMMUNITY_SHARING | boolean | Whether community sharing is enabled |
| ENABLE_MESSAGE_RATING | boolean | Whether message rating is enabled |
| ENABLE_FOLDERS | boolean | Whether folders are enabled |
| FOLDER_MAX_FILE_COUNT | integer \| null | Max files per folder |
| ENABLE_CHANNELS | boolean | Whether channels are enabled |
| ENABLE_MEMORIES | boolean | Whether memories are enabled |
| ENABLE_NOTES | boolean | Whether notes are enabled |
| ENABLE_USER_WEBHOOKS | boolean | Whether user webhooks are enabled |
| ENABLE_USER_STATUS | boolean | Whether user status is enabled |
| PENDING_USER_OVERLAY_TITLE | string \| null | Custom title for pending user overlay |
| PENDING_USER_OVERLAY_CONTENT | string \| null | Custom content for pending user overlay |
| RESPONSE_WATERMARK | string \| null | Response watermark text |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/auths/admin/config

**Summary:** Updates the global admin configuration.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | SHOW_ADMIN_DETAILS | boolean | Yes | Show admin details to users |
| Body | ADMIN_EMAIL | string | No | Admin email override |
| Body | WEBUI_URL | string | Yes | Public URL of the WebUI |
| Body | ENABLE_SIGNUP | boolean | Yes | Allow new signups |
| Body | ENABLE_API_KEYS | boolean | Yes | Allow API key generation |
| Body | ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS | boolean | Yes | Enable API key endpoint restrictions |
| Body | API_KEYS_ALLOWED_ENDPOINTS | string | Yes | Allowed endpoints for API keys |
| Body | DEFAULT_USER_ROLE | string | Yes | Default role for new users (`pending`, `user`, `admin`) |
| Body | DEFAULT_GROUP_ID | string | Yes | Default group ID for new users |
| Body | JWT_EXPIRES_IN | string | Yes | JWT expiry (e.g. `"1h"`, `"-1"`) |
| Body | ENABLE_COMMUNITY_SHARING | boolean | Yes | Enable community sharing |
| Body | ENABLE_MESSAGE_RATING | boolean | Yes | Enable message rating |
| Body | ENABLE_FOLDERS | boolean | Yes | Enable folders |
| Body | FOLDER_MAX_FILE_COUNT | integer \| string | No | Max files per folder |
| Body | ENABLE_CHANNELS | boolean | Yes | Enable channels |
| Body | ENABLE_MEMORIES | boolean | Yes | Enable memories |
| Body | ENABLE_NOTES | boolean | Yes | Enable notes |
| Body | ENABLE_USER_WEBHOOKS | boolean | Yes | Enable user webhooks |
| Body | ENABLE_USER_STATUS | boolean | Yes | Enable user status |
| Body | PENDING_USER_OVERLAY_TITLE | string | No | Title for pending user overlay |
| Body | PENDING_USER_OVERLAY_CONTENT | string | No | Content for pending user overlay |
| Body | RESPONSE_WATERMARK | string | No | Response watermark text |

**Response `200`**

Returns the updated configuration object (same schema as GET `/admin/config`).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/auths/admin/config/ldap/server

**Summary:** Returns the current LDAP server configuration.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

**Response `200`**

```json
{
  "label": "LDAP Server",
  "host": "ldap.example.com",
  "port": 389,
  "attribute_for_mail": "mail",
  "attribute_for_username": "uid",
  "app_dn": "cn=app,dc=example,dc=com",
  "app_dn_password": "secret",
  "search_base": "dc=example,dc=com",
  "search_filters": "",
  "use_tls": true,
  "certificate_path": null,
  "validate_cert": true,
  "ciphers": "ALL"
}
```

| Field | Type | Description |
|-------|------|-------------|
| label | string | Display label for the LDAP server |
| host | string | LDAP server hostname |
| port | integer \| null | LDAP server port |
| attribute_for_mail | string | LDAP attribute containing the email address |
| attribute_for_username | string | LDAP attribute containing the username |
| app_dn | string | Application bind DN |
| app_dn_password | string | Application bind password |
| search_base | string | LDAP search base DN |
| search_filters | string | Additional LDAP search filters |
| use_tls | boolean | Whether to use TLS |
| certificate_path | string \| null | Path to CA certificate file |
| validate_cert | boolean | Whether to validate TLS certificate |
| ciphers | string \| null | TLS cipher string |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/auths/admin/config/ldap/server

**Summary:** Updates the LDAP server configuration.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | label | string | Yes | Display label for the LDAP server |
| Body | host | string | Yes | LDAP server hostname |
| Body | port | integer | No | LDAP server port |
| Body | attribute_for_mail | string | Yes | LDAP attribute for email (default `"mail"`) |
| Body | attribute_for_username | string | Yes | LDAP attribute for username (default `"uid"`) |
| Body | app_dn | string | Yes | Application bind DN |
| Body | app_dn_password | string | Yes | Application bind password |
| Body | search_base | string | Yes | LDAP search base DN |
| Body | search_filters | string | No | Additional search filters (default `""`) |
| Body | use_tls | boolean | No | Use TLS (default `true`) |
| Body | certificate_path | string | No | Path to CA certificate file |
| Body | validate_cert | boolean | No | Validate TLS certificate (default `true`) |
| Body | ciphers | string | No | TLS cipher string (default `"ALL"`) |

**Response `200`**

Returns the updated LDAP server configuration object (same schema as GET response).

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Required field is empty |
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### GET /api/v1/auths/admin/config/ldap

**Summary:** Returns whether LDAP authentication is enabled.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

**Response `200`**

```json
{
  "ENABLE_LDAP": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| ENABLE_LDAP | boolean | Whether LDAP is enabled |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/auths/admin/config/ldap

**Summary:** Enables or disables LDAP authentication.

**Auth:** Admin only

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |
| Body | enable_ldap | boolean | No | Set to `true` to enable LDAP |

**Response `200`**

```json
{
  "ENABLE_LDAP": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| ENABLE_LDAP | boolean | Updated LDAP enabled state |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 403 | Insufficient permissions |

---

### POST /api/v1/auths/api_key

**Summary:** Generates a new API key for the current user.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
{
  "api_key": "sk-..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| api_key | string \| null | The generated API key |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 403 | API key creation not allowed (feature disabled or no permission) |
| 401 | Not authenticated |
| 500 | Failed to create API key |

---

### DELETE /api/v1/auths/api_key

**Summary:** Deletes the current user's API key.

**Auth:** Verified user

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

---

### GET /api/v1/auths/api_key

**Summary:** Returns the current user's API key.

**Auth:** Verified user

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Header | Authorization | Bearer token | Yes | JWT token |

*No additional parameters.*

**Response `200`**

```json
{
  "api_key": "sk-..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| api_key | string \| null | The user's API key |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Not authenticated |
| 404 | No API key found for this user |

---

### POST /api/v1/auths/oauth/{provider}/token/exchange

**Summary:** Exchange an external OAuth provider access token for an OpenWebUI JWT.

**Auth:** Public

**Request**

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Path | provider | string | Yes | OAuth provider name (e.g. `"google"`, `"github"`) |
| Body | token | string | Yes | OAuth access token from the external provider |

**Response `200`**

```json
{
  "token": "eyJ...",
  "token_type": "Bearer",
  "expires_at": 1700000000,
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "profile_image_url": "/api/v1/users/user_id/profile/image",
  "permissions": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| token | string | OpenWebUI JWT access token |
| token_type | string | Always `"Bearer"` |
| expires_at | integer \| null | Unix epoch expiry |
| id | string | User ID |
| email | string | User email |
| name | string | Display name |
| role | string | User role |
| profile_image_url | string | Profile image path |
| permissions | object | User permission map |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid token or unable to validate with provider |
| 403 | Token exchange disabled or user not found |
| 404 | Provider not configured |
