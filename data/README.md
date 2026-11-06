# data/

Data sources of the assistant and who owns them.

| File | Content | Format | Owner |
|---|---|---|---|
| `offices.csv` | office name, room, opening hours | CSV (`name,room,hours`) | Member 3 |
| `handbook.json` | handbook rules: `id`, `title`, `text` | JSON list | Member 3 |

Rules:

- Files are UTF-8. Open them with `encoding="utf-8"`.
- Never commit personal data. Raw dumps go to `data/raw/` (git-ignored).
- A new office or rule needs a test in `tests/`.
