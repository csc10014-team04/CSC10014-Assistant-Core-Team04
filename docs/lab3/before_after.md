# Lab 3 — Before / after maintainability comparison

Fill in for the monolith (before) and your refactored package (after).

| Question | Before | After |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant hardcoded in python source code (`RATE = 450000`). | 1 environment variable in `.env` (`CREDIT_RATE_VND=450000`) without editing any code. |
| Can you run the tests without internet or an API key? | No. The hand-crafted `test()` calls a pseudo `llm()` that simulates network timeouts with random failures and logs a dummy API key. | Yes. All tests run offline, deterministically, and fast using `StubLLMResponder` and pytest fixtures. |
| What happens if `handbook.json` is missing? | Prints `"could not load handbook"` to stdout and continues silently; later queries crash or return wrong responses. | Raises a clear, explicit `DataError("handbook file not found: ...")` at startup. |
| Is any secret printed or logged? | Yes. `API_KEY` is printed in plain text to console on line 37 during debug calls. | No. `llm_api_key` has `repr=False`, and JSON logging only records safe metadata (`intent`, `latency_ms`, `session`, `degraded`). |
| How long does it take a new teammate to find the fee logic? | Minutes to read through the 163-line script and locate embedded parsing logic in `handle()`. | Seconds: modular structure clearly isolates fee parsing and calculation in `src/assistant_core/tools.py`. |
| Number of global variables | 9 module globals (`API_KEY`, `MODEL`, `RATE`, `RETAKE_RATE`, `DEBUG`, `BASE`, plus mutable `history`, `offices`, `handbook`). | 0 module globals (all state is properly encapsulated in classes and dependency-injected). |
| Number of bare `except:` blocks | 3 bare `except:` blocks in `load()` and `main()`. | 0 bare `except:` blocks. All exceptions caught are specific (`FileNotFoundError`, `AssistantError`, `ValidationError`). |
| Lines in the longest function | ~65 lines (`handle()`). | ~18 lines (`AssistantService.handle()` and `_rule()`). |
| `ruff check` issues | >15 issues (unused globals, bare excepts, missing formatting, lines exceeding length limits). | 0 issues (`ruff check .` clean, `ruff check --select BLE .` clean). |
| Can you swap the LLM without touching the service? | No. The `llm()` function is coupled directly inside the `handle()` function. | Yes. The service depends on the `Responder` Protocol; any provider can be injected at runtime without changing service code. |

**Three sentences:** what improved most, what got more complex, and what you would still change.
- **What improved most:** Testability and maintainability improved significantly through modular single-responsibility components, dependency injection, pure calculation functions, and clean exception handling.
- **What got more complex:** The project structure has more files, type models, and configuration boilerplate compared to a single monolithic script.
- **What you would still change:** I would introduce persistent conversation session memory and integrate a live OpenAI/Gemini provider implementing the `Responder` protocol for the Week 4 milestone.

