"""Intent router based on simple heuristic rules."""

import sys
import types
from enum import Enum


class Intent(str, Enum):
    """Categorized user intent."""
    GREETING = "greeting"
    FEE = "fee"
    OFFICE = "office"
    RULE = "rule"
    UNKNOWN = "unknown"


# Register alias modules so imports from assistant_core or models work seamlessly
for _pkg in ("assistant", "assistant_core"):
    _models_mod = f"{_pkg}.models"
    if _models_mod not in sys.modules:
        _m = types.ModuleType(_models_mod)
        _m.Intent = Intent
        sys.modules[_models_mod] = _m

if "assistant_core.router" not in sys.modules:
    sys.modules["assistant_core.router"] = sys.modules[__name__]

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao", "chao"})


def route(text: str, office_names: set[str] | None = None) -> Intent:
    """Route user query to an Intent based on keyword heuristic rules."""
    t = text.lower().strip().rstrip("?!.")
    if t in GREETINGS:
        return Intent.GREETING
    if "fee" in t or "tuition" in t:
        return Intent.FEE
    if office_names:
        for name in office_names:
            if name and name.lower() in t:
                return Intent.OFFICE
    return Intent.RULE
