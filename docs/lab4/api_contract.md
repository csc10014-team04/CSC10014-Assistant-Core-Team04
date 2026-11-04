# Lab 4 - API contract worksheet

| Method | Path | Request body / params | Success (code + body) | Errors (code + error.code) | Who calls it |
|---|---|---|---|---|---|
| GET | /health | - | 200 `{status, version}` | - | ops, UI |
| POST | /v1/chat | `{message: str 1-2000, session_id?: str <=64}` | 200 `{answer, intent, sources[], degraded, request_id}` | 422 `invalid_request`; 429 `too_many_requests` | UI, tests |
| POST | /v1/feedback | `{request_id: str 1-64, rating: -1/0/1, comment?: str <=500}` | 201 `{request_id, rating, comment, id, created_at}` | 422 `invalid_request` | UI |
| GET | /v1/feedback | header `X-API-Key` | 200 list of feedback | 401 `missing_or_invalid_api_key` | staff dashboard |
| GET | /v1/offices | - | 200 `[{name, room, hours}]` sorted by name | - | UI |
| GET | /v1/weather | - | 200 `{temperature_c, wind_kmh, description, observed_at, stale}` | 503 `weather_service_unavailable` | UI |

Questions:

1. **Required fields and limits.** Chat: `message` is required, 1-2000 characters. Feedback: `request_id` and
   `rating` are required; `rating` is only -1, 0 or 1; `comment` is optional, up to 500 characters.
2. **What the UI shows.** 422: highlight the field named in the message. 429: "Too many requests, try again in a
   minute". 401: hide the staff page. 503: "Weather is unavailable right now" (or the stale value if `stale` is true).
3. **What forces `/v2`.** Renaming or removing a response field, changing a field type, or changing the meaning of
   `rating`. Adding an optional field does not.
