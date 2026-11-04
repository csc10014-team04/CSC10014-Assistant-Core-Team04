# Lab 3 — AI extension review

1. Ask an AI coding assistant to extend your service with ONE feature, e.g.
   "Add an 'exam absence' answer that tells students the deadline from the handbook."

2. Paste the prompt you used:
   ```text
   Please extend the assistant_core service to handle queries about final exam absences, specifically returning the 3-day medical evidence deadline specified in rule H26-7.2 of the handbook.
   ```

3. Review the generated code manually. Document **at least three changes** you made:

| # | What the AI generated | Problem you found | What you changed | Why |
|---|---|---|---|---|
| 1 | Hardcoded response string `"You must submit evidence within 3 working days."` directly in a new method inside `service.py`. | Bypassed the `Handbook` knowledge retrieval module and `Responder` interface abstraction, breaking the architecture. | Routed the query to search `handbook.search("exam absence medical evidence")` and formatted via `self.responder.explain()`. | Preserves single responsibility and maintains consistent rule citation (`H26-7.2`) and fallback capabilities. |
| 2 | Logged the full incoming user query message string: `log.info(f"Processing query: {msg.text}")`. | Privacy/security risk: violates the lab rule "never log the full user message" (potential PII / sensitive queries). | Changed log to record only structured metadata (`intent`, `latency_ms`, `session`, `degraded`). | Protects user privacy and complies with Twelve-Factor logging standards and project guidelines. |
| 3 | Added a unit test using a real network call to a live external LLM API without mocking. | Tests fail in CI / offline environments and depend on external API keys and network access. | Replaced with unit tests in `test_service.py` using `StubLLMResponder` and offline fixtures. | Ensures the test suite remains fast (<0.1s), 100% deterministic, and runnable without network or credentials. |

Checklist:
- [x] Interfaces respected (`route` -> `service` -> `responder`)
- [x] No unnecessary new dependencies added
- [x] No secrets leaked or hardcoded
- [x] No user personal data logged
- [x] Deterministic unit tests added and passing

