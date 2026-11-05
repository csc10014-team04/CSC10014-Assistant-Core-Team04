# Lab 4 - Reflection (H2)

Calling `service.handle()` in Lab 3 is an in-process Python function call requiring the caller to run in Python, reside on the same machine, and import the package directly. In contrast, calling `POST /v1/chat` today invokes the service over HTTP using standard JSON payloads, completely decoupling the client implementation from the backend technology stack.

A multidisciplinary team often prefers the HTTP web API approach for several reasons:
1. Cross-platform language independence: Web browsers, mobile applications (iOS/Android), and external microservices can query the assistant without needing a Python runtime environment.
2. Parallel development: Teams can develop frontend and client applications concurrently against an explicit OpenAPI contract (`/docs`) without depending on local library code.
3. Centralized cross-cutting concerns: Shared capabilities such as input validation, rate limiting, authentication, and uniform error formats are managed at the API boundary.
4. Independent lifecycle and scaling: The backend service can be scaled horizontally and updated behind a stable endpoint without requiring client redeployment.
