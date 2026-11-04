# Review checklist

Leave at least three labelled comments: `Blocking:`, `Question:`, `Suggestion:`, `Praise:`.

- [ ] **Correctness** - does it meet the acceptance criteria of the linked issue?
- [ ] **Readability** - clear names, small functions, no dead code.
- [ ] **Tests** - new behaviour has a test; `pytest -q` passes.
- [ ] **Security** - no secrets or personal data; user input validated; nothing sensitive logged.
- [ ] **Maintainability** - respects `route -> service -> responder`; no new globals; no blind `except`.
- [ ] **Scope** - one change per PR; no unrelated edits.
- [ ] **Docs** - README / docs updated when setup or behaviour changed.
- [ ] **AI use** - disclosed in the PR; every generated line understood by the author.
