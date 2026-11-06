# Lab 4 homework - design for an external service that goes down

Service chosen: Open-Meteo weather (no API key)  Base URL: https://api.open-meteo.com/v1/forecast

| Failure | How you simulate it | What your API returns | What the user sees |
|---|---|---|---|
| timeout | transport raises `ConnectTimeout` | after 1 retry: cached (stale) weather, else 503 `weather_service_unavailable` | last known weather marked stale, or "weather unavailable" |
| 500 from upstream | `MockTransport` returns 500 | same as timeout | same as timeout |
| malformed JSON | `MockTransport` returns `{}` (KeyError is caught) | same as timeout | same as timeout |
| rate limited (429) | `MockTransport` returns 429 | same as timeout | same as timeout |

Timeout value and why: 3 s (`WEATHER_TIMEOUT_S`) - the UI must not hang on a side feature.
Retries and why: 1 retry with a short back-off - rides out a blip without doubling the wait.
Cache TTL and why: 600 s - weather changes slowly, and the cache is the backup plan when the upstream fails.
Tests added (file + names): `tests/test_api.py` - `test_weather_ok`, `test_weather_down_returns_503`,
`test_weather_stale_cache_when_upstream_fails`.
