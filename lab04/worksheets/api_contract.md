# Lab 4 — API contract worksheet

Fill in one row per endpoint **before** you code it.

| Method | Path | Request body / params | Success (code + body) | Errors (code + error.code) | Who calls it |
|---|---|---|---|---|---|
| GET | /health | — | 200 `{"status": "ok", "version": "1.0.0"}` | — | ops, UI |
| POST | /v1/chat | `{"message": str (1-2000 chars), "session_id"?: str}` | 200 `{"answer", "intent", "sources", "degraded", "request_id"}` | 422 `invalid_request`, 429 `too_many_requests` | UI, tests |
| POST | /v1/feedback | `{"request_id": str, "rating": -1/0/1, "comment"?: str}` | 201 `{"request_id", "rating", "comment", "id", "created_at"}` | 422 `invalid_request` | UI |
| GET | /v1/feedback | header `X-API-Key: <key>` | 200 list of feedback items | 401 `missing_or_invalid_api_key` | staff dashboard |
| GET | /v1/offices | — | 200 list of office objects sorted by name | — | UI, tests |
| GET | /v1/weather | — | 200 `{"temperature_c", "wind_kmh", "description", "observed_at", "stale"}` | 503 `weather_service_unavailable` | UI |

Questions:
1. Which fields are required, and what are their limits?
   - In `/v1/chat`: `message` is required with length between 1 and 2000 characters; `session_id` defaults to "local".
   - In `/v1/feedback`: `request_id` is required; `rating` is required and restricted to -1, 0, or 1; `comment` is optional with maximum length 500 characters.
   - In `GET /v1/feedback`: `X-API-Key` header matching `API_ADMIN_KEY` is required.
2. What does the UI show for each error code?
   - 422: Form validation message indicating the specific invalid field.
   - 429: Rate limit warning informing the user to slow down and retry in a minute.
   - 401: Unauthorized prompt requesting an administrator access token.
   - 503: Service alert indicating external weather data is currently unavailable.
3. What changes would force a `/v2`?
   - Breaking contract modifications such as removing existing response fields, renaming keys, changing data types, or altering endpoint path conventions. Non-breaking additions of optional fields or endpoints do not require a major version bump.
