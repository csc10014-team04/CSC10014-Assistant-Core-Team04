# Lab 1 - Setup failure log (homework H1)

Break the setup on purpose (delete `.venv`, move the repository, uninstall pytest, clone fresh), recover
using only the README, and record at least one **real** failure and its fix.

| # | What I broke | Symptom / error message | Fix | README changed? |
|---|---|---|---|---|
| 1 | | | | |

Known issues seen while setting this repository up (add yours above):

- `ruff` is in `requirements.txt` but missing until `pip install -r requirements.txt` is run inside the active `.venv`.
- A leftover `.venv` inside a moved folder can stay locked on Windows while a server is still running: stop uvicorn, then delete it.
