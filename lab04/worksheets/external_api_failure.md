# Lab 4 homework — design for an external service that goes down

Service chosen (weather / maps / news / other approved): Open-Meteo Weather API  Base URL: https://api.open-meteo.com/v1/forecast

| Failure | How you simulate it | What your API returns | What the user sees |
|---|---|---|---|
| timeout | transport raises `httpx.ConnectTimeout` | after retry: stale cache if present, otherwise 503 `weather_service_unavailable` | cached weather with stale flag, or error notification "Weather service unavailable" |
| 500 from upstream | `MockTransport` returns HTTP 500 | after retry: stale cache if present, otherwise 503 `weather_service_unavailable` | cached weather or error notification |
| malformed JSON | `MockTransport` returns `{}` causing `KeyError` | caught as `ExternalServiceError`, returns 503 | error notification "Weather service unavailable" |
| rate limited (429) | `MockTransport` returns HTTP 429 | caught as `ExternalServiceError`, returns 503 | error notification "Weather service unavailable" |

Timeout value and why: 3 seconds (`WEATHER_TIMEOUT_S`), preventing external slowdowns from blocking client requests.  
Retries and why: 1 retry with exponential backoff, recovering from momentary network spikes without prolonging response latency.  
Cache TTL and why: 600 seconds, since campus weather metrics update periodically and local caching acts as a resilient fallback.  
Tests added (file + names): `lab04/starter/tests/test_api.py` (`test_weather_ok`, `test_weather_down_returns_503`, `test_weather_stale_cache_when_upstream_fails`).
