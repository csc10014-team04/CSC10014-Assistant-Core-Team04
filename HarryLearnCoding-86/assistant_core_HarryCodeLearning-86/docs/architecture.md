# Architecture Note: assistant_core

## 1. Module Overview

| Module | Responsibility |
|---|---|
| `config.py` | Read settings from environment variables and `.env`; validate configurations using Pydantic. |
| `errors.py` | Domain-specific named exception hierarchy (`AssistantError`, `ConfigError`, `DataError`, `InvalidRequest`, `ProviderError`). |
| `models.py` | Public data contracts: `Message`, `Response`, `Intent` enum, and `Source` citation model. |
| `router.py` | Heuristic intent classification routing user query into `GREETING`, `FEE`, `OFFICE`, or `RULE`. |
| `knowledge.py` | Read and query domain data sources: `OfficeDirectory` (from CSV) and `Handbook` (from JSON) with keyword search. |
| `tools.py` | Pure, deterministic business logic: parsing credits/retakes and computing tuition fees without I/O or global state. |
| `responder.py` | Response generation behind a `Responder` Protocol (adapter pattern) supporting `TemplateResponder` and `StubLLMResponder`. |
| `service.py` | `AssistantService.handle(Message) -> Response` orchestrator; single entry point tying routing, retrieval, tools, and fallback together. |
| `logging_setup.py` | Structured JSON log formatter writing execution metadata to `stderr`. |
| `__main__.py` | CLI entry point handling interactive loop and single-query arguments. |

## 2. Service Interface

The service exposes a single, unified entry method:

```python
AssistantService.handle(msg: Message) -> Response
```

### Contracts:
- **Input (`Message`)**:
  - `text: str`: Query text with length between 1 and 2,000 characters (validated by Pydantic).
  - `session_id: str`: Session identifier (default: `"local"`).
- **Output (`Response`)**:
  - `answer: str`: Human-readable answer string.
  - `intent: Intent`: Categorized intent (`GREETING`, `FEE`, `OFFICE`, `RULE`, or `UNKNOWN`).
  - `sources: list[Source]`: List of source citations referenced (`id`, `title`).
  - `degraded: bool`: Indicates whether a fallback was triggered due to provider failure.
- **Error Handling**:
  - Invalid input: Rejected at the boundary via Pydantic `ValidationError` or `InvalidRequest`.
  - Startup errors: Missing knowledge files or missing required API keys raise `DataError` or `ConfigError`.
  - Provider errors: If the AI provider fails (e.g. timeout or connection drop), the service catches `ProviderError` internally and falls back to `TemplateResponder`, returning `degraded=True` without exposing internal failures to the caller.

## 3. Key Architectural Decisions

1. **Deterministic Fee Calculation in Pure Python (`tools.py`)**:
   - *Reason*: LLMs are prone to arithmetic errors and hallucination. Calculating fees and validating credit limits deterministically in `tools.py` guarantees 100% accuracy, strict validation, zero API costs, and easy isolated unit testing.
2. **Adapter Pattern with Protocol for LLM Responders (`responder.py`)**:
   - *Reason*: Decoupling the assistant core from third-party LLM providers via a `Responder` Protocol allows running tests, CI/CD pipelines, and local development offline without API keys using `StubLLMResponder`. Switching to an actual LLM provider in Week 4 requires no changes to `AssistantService`.
3. **Twelve-Factor Configuration Management (`config.py` & `.env.example`)**:
   - *Reason*: In accordance with Factor III of The Twelve-Factor App, configuration is strictly decoupled from code and read from environment variables (or `.env`). Using `repr=False` on sensitive fields like `llm_api_key` ensures secrets never leak into logs or error traces.

