# Lab 03 — Part A: Read the Monolith Analysis

## A.2 Hunt the Smells

The following table documents 10 architectural and code quality issues identified in `lab03/monolith/assistant_monolith.py`, why they hurt maintainability/reliability, and which module in the refactored `assistant_core` architecture owns the fix:

| # | Smell | Where (in monolith) | Why it hurts | Owning Module in `assistant_core` |
|---|---|---|---|---|
| 1 | Hard-coded secret, printed in debug output | Lines 6, 37 (`API_KEY`, `llm()`) | Leaks the secret key into terminal logs, files, and Git version control. | `config.py` (reads from `.env` with `repr=False`), `responder.py`, `logging_setup.py` |
| 2 | Configuration mixed with code | Lines 7–10 (`RATE`, `RETAKE_RATE`, `MODEL`, `DEBUG`) | Changing tuition rates, models, or debug toggles requires modifying production source code and redeploying. | `config.py` (Settings model loaded from environment variables / `.env`) |
| 3 | Global mutable state | Lines 11–13 (`history`, `offices`, `handbook`) | Causes hidden coupling between functions, side effects across queries, and makes concurrent access and unit testing difficult. | `knowledge.py` (`OfficeDirectory`, `Handbook` classes) & `service.py` (dependency injection) |
| 4 | Bare `except:` blocks | Lines 26, 30, 136 (`load()`, `main()`) | Silently suppresses critical errors (syntax errors, missing files, KeyboardInterrupt/Ctrl+C) leaving bugs undetected. | `errors.py` (named domain exceptions like `DataError`, `AssistantError`), and handling specific exceptions |
| 5 | Monolithic function doing everything | Lines 44–99 (`handle()`) | Violates Single Responsibility Principle: mixes input sanitization, routing, arithmetic calculations, handbook search, and LLM orchestration in a ~60 line function. | `router.py`, `tools.py`, `knowledge.py`, `responder.py`, coordinated by `service.py` |
| 6 | Magic strings / error return values | Lines 49, 58, 71, 73, 99 (`"empty"`, `"saved"`, `"too many credits"`, `"Sorry I dont know"`) | Callers cannot differentiate between success, missing data, or validation failures without brittle string matching. | `models.py` (`Message`, `Response`, `Intent`), `errors.py` (`InvalidRequest`, `ValidationError`) |
| 7 | `print()` statements instead of structured logging | Lines 27, 31, 37, 97, 124, 144 | No log levels, unparsable by log analyzers, pollutes stdout, and cannot separate diagnostic logs from user responses. | `logging_setup.py` (`JsonFormatter` writing structured JSON logs to stderr) |
| 8 | Hand-made tests that print to console | Lines 148–156 (`test()`) | Manual verification required; assertions are not automated and CI cannot automatically detect regressions. | `tests/` automated test suite using `pytest` (`test_tools.py`, `test_router.py`, `test_service.py`) |
| 9 | File paths constructed with string concatenation | Lines 20, 29, 119 (`BASE + "/data/..."`) | Prone to failure across operating systems (POSIX vs Windows path separators) and directory traversal issues. | `pathlib.Path` in `config.py` and `knowledge.py` |
| 10 | Non-deterministic behaviour in mock LLM | Line 39 (`random.random() < 0.1` in `llm()`) | Introduces flaky test runs and unreliable debugging due to artificial random timeouts. | `responder.py` (`StubLLMResponder` with explicit deterministic test flags) |

---

## A.3 What We Keep (Preserved Behavior)

Refactoring changes internal software structure without altering external observable behavior. The following capabilities of the monolith are strictly preserved:

1. **Greetings**:
   - Responds to standard greeting triggers: `"hi"`, `"hello"`, `"hey"`, `"xin chao"`.
   - Returns friendly welcome: `"Hello! I can help with offices, fees and rules."`

2. **Deterministic Tuition & Fee Calculation**:
   - Parses enrolled credits and retake credits from queries like `"tuition for 18 credits and 2 retake"`.
   - Preserves formula: `credits * RATE + retake * RATE * RETAKE_RATE` (with default rate = 450,000 VND and retake multiplier = 1.5).
   - Validates that credit count is within reasonable bounds (between 1 and 30 credits).

3. **Office Directory Lookup**:
   - Matches office names (e.g., `"library"`, `"training office"`) case-insensitively against directory data.
   - Outputs room number and opening hours: `"{name}: room {room}, open {hours}."`

4. **Handbook Rule Search & Source Citation**:
   - Searches regulations in handbook data via keyword overlap.
   - Generates contextual answers referencing official regulation codes (e.g., `(source: H26-5.3)`).

5. **Graceful Fallback on Provider Failure**:
   - In case of provider unavailability, gracefully falls back to deterministic template responder without crashing.

