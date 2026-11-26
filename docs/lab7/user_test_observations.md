# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Minh, Date: 26/11/2026
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Finished asking about thesis credits, then looked through the sidebar trying to clear the conversation before asking about the lost student card. | A "New chat" or "Clear" button in the sidebar to reset history and start a fresh session. | `ui/app.py` only had example-question buttons in the sidebar and provided no way to reset `st.session_state.messages` or start a new `session_id`. | Add a `"New chat"` button in the sidebar backed by `reset_chat_state(st.session_state)` so users can clear messages, ratings, and start a fresh session ID. |
| 2 | Looked at the inline `Sources: H26#5.3 — 5.3 Thesis registration` caption and asked what `H26#5.3` meant. | A human-friendly document name (e.g., "Student Handbook 2026, section 5.3") rather than an internal chunk identifier. | `format_sources()` prints the raw `s['id']` string returned by the RAG chunker (`H26#5.3`) directly alongside the section title. | Map known document prefixes (`H26`, `F26`, `S26`) to readable document names inside `format_sources()` and keep raw IDs secondary. |
| 3 | Tried pasting a long multi-paragraph excerpt from an email into the chat box and hit Enter before noticing any character limit. | A visible character limit hint or counter near the input box before submitting. | `validate_input()` only shows `"Your question is too long (max 2000 characters)."` after submission, with no pre-submit limit hint in the placeholder. | Include `(max 2000 chars)` in the `st.chat_input` placeholder text. |

The one change we made (Fix #1): Added a `"New chat"` button at the top of the sidebar in `ui/app.py` backed by `reset_chat_state()` in `ui/logic.py` (with unit and `AppTest` tests in `tests/test_ui.py`), allowing users to reset conversation history, rating state, and `session_id` in one click.

Before / after summary:
- Before: The sidebar only listed the four example prompts; users had to reload the browser tab (`F5`) to clear the conversation or start a new session.
- After: Clicking **New chat** in the sidebar immediately clears previous messages back to the welcome prompt, resets `rated`, and generates a new 12-character `session_id` without reloading the page.
