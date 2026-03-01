# SCIM 2.0 API

Base path: `/api/v1/scim/v2`

> **Experimental:** This SCIM 2.0 implementation is subject to change and may not fully comply with all RFC 7643/7644 requirements.

Open WebUI implements SCIM 2.0 (RFC 7643/7644) for enterprise user and group provisioning. This allows identity providers (e.g. Azure AD, Okta, Microsoft Entra ID) to automatically create, update, and deprovision users and groups.

## Authentication

SCIM endpoints use a **dedicated Bearer token** separate from the user JWT.

```
Authorization: Bearer <SCIM_TOKEN>
```

Configuration requires two environment variables:

| Variable | Description |
|----------|-------------|
| `ENABLE_SCIM` | Must be `true` to activate SCIM endpoints |
| `SCIM_TOKEN` | Static bearer token validated on every SCIM request |
| `SCIM_AUTH_PROVIDER` | Identity provider name (e.g. `microsoft`, `oidc`) — required for `externalId` mapping |

**Content-Type:** `application/scim+json` (SCIM-compliant) or `application/json`

**Error format** follows RFC 7644 §3.12:

```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
  "status": "404",
  "scimType": "invalidValue",
  "detail": "User abc not found"
}
```

---

## Discovery Endpoints

### GET /api/v1/scim/v2/ServiceProviderConfig

**Summary:** Get SCIM Service Provider Configuration describing supported features.

**Auth:** Public (no authentication required)

**Response `200`**

```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
  "patch": { "supported": true },
  "bulk": { "supported": false, "maxOperations": 1000, "maxPayloadSize": 1048576 },
  "filter": { "supported": true, "maxResults": 200 },
  "changePassword": { "supported": false },
  "sort": { "supported": false },
  "etag": { "supported": false },
  "authenticationSchemes": [
    {
      "type": "oauthbearertoken",
      "name": "OAuth Bearer Token",
      "description": "Authentication using OAuth 2.0 Bearer Token"
    }
  ]
}
```

| Feature | Supported |
|---------|-----------|
| PATCH (partial update) | Yes |
| Bulk operations | No |
| Filter | Yes (userName eq, externalId eq) |
| Password change | No |
| Sorting | No |
| ETags | No |

---

### GET /api/v1/scim/v2/ResourceTypes

**Summary:** Get the list of SCIM resource types supported by this provider.

**Auth:** Public

**Response `200`**

```json
[
  {
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
    "id": "User",
    "name": "User",
    "endpoint": "/Users",
    "schema": "urn:ietf:params:scim:schemas:core:2.0:User",
    "meta": {
      "location": "https://host/api/v1/scim/v2/ResourceTypes/User",
      "resourceType": "ResourceType"
    }
  },
  {
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
    "id": "Group",
    "name": "Group",
    "endpoint": "/Groups",
    "schema": "urn:ietf:params:scim:schemas:core:2.0:Group",
    "meta": {
      "location": "https://host/api/v1/scim/v2/ResourceTypes/Group",
      "resourceType": "ResourceType"
    }
  }
]
```

---

### GET /api/v1/scim/v2/Schemas

**Summary:** Get the SCIM schema definitions for User and Group resources.

**Auth:** Public

**Response `200`** — array of two schema objects (User and Group) per RFC 7643.

---

## User Endpoints

### SCIM User Object

```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "id": "user-uuid",
  "externalId": "idp-subject-id",
  "userName": "alice@example.com",
  "displayName": "Alice Smith",
  "name": {
    "formatted": "Alice Smith",
    "givenName": "Alice",
    "familyName": "Smith"
  },
  "emails": [
    { "value": "alice@example.com", "type": "work", "primary": true }
  ],
  "active": true,
  "photos": [
    { "value": "https://example.com/photo.png", "type": "photo", "primary": true }
  ],
  "groups": [
    {
      "value": "group-uuid",
      "display": "Engineering",
      "$ref": "https://host/api/v1/scim/v2/Groups/group-uuid",
      "type": "direct"
    }
  ],
  "meta": {
    "resourceType": "User",
    "created": "2024-03-01T12:00:00+00:00",
    "lastModified": "2024-03-15T09:30:00+00:00",
    "location": "https://host/api/v1/scim/v2/Users/user-uuid"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Open WebUI internal user UUID |
| externalId | string\|null | Identity provider subject identifier |
| userName | string | User's email address (used as login) |
| displayName | string | Full display name |
| name.formatted | string | Full formatted name |
| name.givenName | string | First name |
| name.familyName | string | Last name |
| emails | array | Email addresses (primary email used for login) |
| active | boolean | `true` = active user; `false` = pending (cannot log in) |
| photos | array\|null | Profile photo URLs |
| groups | array\|null | Groups the user belongs to |
| meta.resourceType | string | Always `"User"` |
| meta.created | string | ISO 8601 creation timestamp |
| meta.lastModified | string | ISO 8601 last-modified timestamp |
| meta.location | string | Canonical URL of this resource |

---

### GET /api/v1/scim/v2/Users

**Summary:** List SCIM Users with pagination and optional filter.

**Auth:** SCIM Bearer token

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| startIndex | integer | No | 1-based start index (default: 1, min: 1) |
| count | integer | No | Page size (default: 20, max: 100) |
| filter | string | No | SCIM filter expression (see supported filters below) |

**Supported Filters**

| Filter | Example |
|--------|---------|
| `userName eq` | `userName eq "alice@example.com"` |
| `externalId eq` | `externalId eq "sub-12345"` |

**Response `200`**

```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
  "totalResults": 100,
  "itemsPerPage": 20,
  "startIndex": 1,
  "Resources": [ { "...SCIM User objects..." } ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| schemas | array | Always `["urn:ietf:params:scim:api:messages:2.0:ListResponse"]` |
| totalResults | integer | Total matching users |
| itemsPerPage | integer | Number of results in this page |
| startIndex | integer | 1-based start index of this page |
| Resources | array | List of SCIM User objects |

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Missing or invalid SCIM token |
| 403 | SCIM not enabled |

---

### GET /api/v1/scim/v2/Users/{user_id}

**Summary:** Get a SCIM User by their Open WebUI UUID.

**Auth:** SCIM Bearer token

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| user_id | string | Open WebUI user UUID |

**Response `200`** — SCIM User object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 404 | User not found (`scimType: invalidValue`) |

---

### POST /api/v1/scim/v2/Users

**Summary:** Create a new user via SCIM provisioning.

**Auth:** SCIM Bearer token

**Request**

```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName": "alice@example.com",
  "displayName": "Alice Smith",
  "name": { "givenName": "Alice", "familyName": "Smith" },
  "emails": [{ "value": "alice@example.com", "primary": true }],
  "active": true,
  "externalId": "idp-subject-id",
  "photos": [{ "value": "https://example.com/photo.png", "primary": true }]
}
```

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | userName | string | Yes | User's email address (must be unique) |
| Body | displayName | string | Yes | Full display name |
| Body | emails | array | Yes | At least one email; primary email used for login |
| Body | name | object | No | Structured name (used to set displayName if provided) |
| Body | active | boolean | No | `true` = active, `false` = pending (default: true) |
| Body | externalId | string | No | IdP subject identifier to store for account linking |
| Body | password | string | No | Ignored (passwords managed via OAuth/LDAP) |
| Body | photos | array | No | Profile photo URLs |

**Response `201`** — created SCIM User object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 409 | User with same externalId or email already exists (`scimType: uniqueness`) |
| 500 | Internal error creating user |

---

### PUT /api/v1/scim/v2/Users/{user_id}

**Summary:** Fully replace a SCIM User's attributes.

**Auth:** SCIM Bearer token

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| user_id | string | Open WebUI user UUID |

**Request** — same schema as POST `/Users` (all updatable fields).

**Response `200`** — updated SCIM User object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 404 | User not found |
| 500 | Internal error updating user |

---

### PATCH /api/v1/scim/v2/Users/{user_id}

**Summary:** Partially update a SCIM User using SCIM Patch operations.

**Auth:** SCIM Bearer token

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| user_id | string | Open WebUI user UUID |

**Request**

```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [
    { "op": "replace", "path": "active", "value": false },
    { "op": "replace", "path": "displayName", "value": "Alice Johnson" }
  ]
}
```

**Supported Operations**

| Path | Op | Description |
|------|----|-------------|
| `active` | replace | Enable (`true`) or suspend (`false`) the user |
| `userName` | replace | Update email/login |
| `displayName` | replace | Update display name |
| `emails[primary eq true].value` | replace | Update primary email |
| `name.formatted` | replace | Update display name from formatted name |
| `externalId` | replace | Link/update the IdP subject identifier |

**Response `200`** — updated SCIM User object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 404 | User not found |
| 500 | Internal error |

---

### DELETE /api/v1/scim/v2/Users/{user_id}

**Summary:** Permanently delete a user via SCIM deprovisioning.

**Auth:** SCIM Bearer token

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| user_id | string | Open WebUI user UUID |

**Response `204`** — no content.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 404 | User not found |
| 500 | Internal error deleting user |

---

## Group Endpoints

### SCIM Group Object

```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
  "id": "group-uuid",
  "displayName": "Engineering",
  "members": [
    {
      "value": "user-uuid",
      "$ref": "https://host/api/v1/scim/v2/Users/user-uuid",
      "type": "User",
      "display": "Alice Smith"
    }
  ],
  "meta": {
    "resourceType": "Group",
    "created": "2024-03-01T12:00:00+00:00",
    "lastModified": "2024-03-15T09:30:00+00:00",
    "location": "https://host/api/v1/scim/v2/Groups/group-uuid"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Open WebUI group UUID |
| displayName | string | Group display name |
| members | array | List of SCIM group members |
| members[].value | string | Member user UUID |
| members[].$ref | string | Canonical URL of the member user |
| members[].type | string | Always `"User"` |
| members[].display | string | Member's display name |
| meta.resourceType | string | Always `"Group"` |

---

### GET /api/v1/scim/v2/Groups

**Summary:** List SCIM Groups with pagination and optional filter.

**Auth:** SCIM Bearer token

**Query Parameters**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| startIndex | integer | No | 1-based start index (default: 1) |
| count | integer | No | Page size (default: 20, max: 100) |
| filter | string | No | SCIM filter expression (`displayName eq "Engineering"`) |

**Response `200`**

```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
  "totalResults": 10,
  "itemsPerPage": 10,
  "startIndex": 1,
  "Resources": [ { "...SCIM Group objects..." } ]
}
```

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |

---

### GET /api/v1/scim/v2/Groups/{group_id}

**Summary:** Get a SCIM Group by its Open WebUI UUID.

**Auth:** SCIM Bearer token

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| group_id | string | Open WebUI group UUID |

**Response `200`** — SCIM Group object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 404 | Group not found |

---

### POST /api/v1/scim/v2/Groups

**Summary:** Create a new group via SCIM provisioning.

**Auth:** SCIM Bearer token

**Request**

```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
  "displayName": "Engineering",
  "members": [
    { "value": "user-uuid-1" },
    { "value": "user-uuid-2" }
  ]
}
```

| Location | Field | Type | Required | Description |
|----------|-------|------|----------|-------------|
| Body | displayName | string | Yes | Group display name |
| Body | members | array | No | Initial member list (user UUID values) |

**Response `201`** — created SCIM Group object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 500 | Internal error creating group (e.g. no admin user found) |

---

### PUT /api/v1/scim/v2/Groups/{group_id}

**Summary:** Fully replace a SCIM Group's attributes.

**Auth:** SCIM Bearer token

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| group_id | string | Open WebUI group UUID |

**Request** — same schema as POST `/Groups`.

**Response `200`** — updated SCIM Group object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 404 | Group not found |
| 500 | Internal error |

---

### PATCH /api/v1/scim/v2/Groups/{group_id}

**Summary:** Partially update a SCIM Group using SCIM Patch operations.

**Auth:** SCIM Bearer token

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| group_id | string | Open WebUI group UUID |

**Request**

```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [
    { "op": "replace", "path": "displayName", "value": "Platform Engineering" },
    { "op": "add", "path": "members", "value": [{ "value": "user-uuid-3" }] },
    { "op": "remove", "path": "members[value eq \"user-uuid-1\"]" }
  ]
}
```

**Supported Operations**

| Path | Op | Description |
|------|----|-------------|
| `displayName` | replace | Rename the group |
| `members` | replace | Replace entire member list |
| `members` | add | Add members to the group |
| `members[value eq "<id>"]` | remove | Remove a specific member by user ID |

**Response `200`** — updated SCIM Group object.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 404 | Group not found |
| 500 | Internal error |

---

### DELETE /api/v1/scim/v2/Groups/{group_id}

**Summary:** Permanently delete a group via SCIM deprovisioning.

**Auth:** SCIM Bearer token

**Path Parameters**

| Field | Type | Description |
|-------|------|-------------|
| group_id | string | Open WebUI group UUID |

**Response `204`** — no content.

**Error Responses**

| Status | Meaning |
|--------|---------|
| 401 | Invalid SCIM token |
| 403 | SCIM not enabled |
| 404 | Group not found |
| 500 | Internal error deleting group |

---

## SCIM 2.0 Compliance Notes

- **RFC 7643** (Core Schema) — User and Group schemas are implemented; Enterprise User extension is not supported.
- **RFC 7644** (Protocol) — GET, POST, PUT, PATCH, DELETE operations are supported. Bulk and ETag are not.
- **Pagination** — Uses 1-based `startIndex` and `count` per RFC 7644 §3.4.2.4. `startIndex < 1` is clamped to 1; `count < 0` is treated as 0.
- **Filtering** — Only `eq` operator on `userName` and `externalId` for Users; basic `displayName eq` for Groups.
- **User activation** — `active: false` sets the user to `pending` role (cannot log in); `active: true` sets role to `user`.
- **externalId mapping** — Stored per-provider in the user's `scim` JSON field. The `SCIM_AUTH_PROVIDER` env var determines which provider namespace to use.
- **Account linking** — If an `externalId` matches an existing OAuth sub, the account is linked automatically.
