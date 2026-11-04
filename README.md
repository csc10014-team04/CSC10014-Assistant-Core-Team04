# CSC10014 Smart Virtual Assistant - Team 04

A study assistant for university students. It answers questions about offices, tuition fees and
handbook rules. The project grows lab by lab: a rule-based starter (`assistant`), a maintainable
service (`assistant_core`, Lab 3) and a REST API on top of it (`assistant_api`, Lab 4).
The AI part is still a stub.

## Prerequisites

- Python 3.10 or newer
- Git

## Setup

macOS / Linux / Git Bash:

```bash
git clone git@github.com:csc10014-team04/CSC10014-Assistant-Core-Team04.git
cd CSC10014-Assistant-Core-Team04
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
cp .env.example .env
```

Windows PowerShell:

```powershell
git clone git@github.com:csc10014-team04/CSC10014-Assistant-Core-Team04.git
cd CSC10014-Assistant-Core-Team04
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

Check the setup: `python scripts/check_env.py` - every line should be `[ OK ]`.

## Run

Lab 1 rule-based starter:

```bash
python -m assistant "where is the training office?"
# -> Training Office: room I.101, open Mon-Fri 07:30-16:30.
```

Lab 3 service (CLI, logs go to stderr, answers to stdout):

```bash
python -m assistant_core "tuition for 18 credits and 2 retake"
# -> Your tuition is 9,450,000 VND.
```

Lab 4 REST API (interactive docs at http://127.0.0.1:8000/docs):

```bash
uvicorn assistant_api.main:create_app --factory --reload
```

## Test

```bash
pytest -q          # expected: all tests pass (offline, no API key needed)
ruff check .       # expected: All checks passed!
bash api-tests/curl_tests.sh   # manual API checks, needs the server running
```

## API (v1)

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | liveness check |
| POST | `/v1/chat` | `{"message": "...", "session_id": "..."}`; 422 on bad input, 429 when rate limited |
| POST | `/v1/feedback` | rating -1 / 0 / 1; returns 201 |
| GET | `/v1/feedback` | admin only, header `X-API-Key` |
| GET | `/v1/offices` | all offices, sorted by name |
| GET | `/v1/weather` | campus weather; 503 if the upstream is down |

Every error has one shape: `{"error": {"code": "...", "message": "..."}}`.

## Project structure

| Path | Purpose |
|---|---|
| `src/assistant/` | Lab 1 rule-based starter |
| `src/assistant_core/` | Lab 3 service: config, models, router, knowledge, tools, responder, service, logging |
| `src/assistant_api/` | Lab 4 FastAPI app, schemas, rate limiter, weather client |
| `tests/` | pytest tests for all packages |
| `data/` | `offices.csv`, `handbook.json` and their owners (`data/README.md`) |
| `docs/` | architecture note, team page, per-lab worksheets (`docs/lab1` ... `docs/lab4`) |
| `api-tests/` | curl script and Postman collection |
| `practice/` | Lab 4 warm-up API (P1-P5) |
| `scripts/` | `check_env.py` |
| `ui/` | UI plan (Week 7) |
| `.github/` | PR and issue templates |

## Working agreement

Every change starts as an issue, lives on a branch, and merges through a reviewed pull request.
See [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) and [REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md).

## Troubleshooting

- `No module named assistant` / `assistant_core` -> activate `.venv` and run `pip install -e .`.
- PowerShell blocks `Activate.ps1` -> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- `uvicorn: command not found` -> activate `.venv`; run `pip install -r requirements.txt`.
- `Error loading ASGI app` -> run from the repository root and keep `--factory`.
- `Address already in use` -> stop the other server or add `--port 8001`.
- `/v1/weather` always 503 -> the network blocks the weather site; the tests use a fake one.
- `DataError: office file not found` -> run from the repository root or set `ASSISTANT_DATA_DIR`.
