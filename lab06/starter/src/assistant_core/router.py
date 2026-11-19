from __future__ import annotations

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})
FEE_WORDS = ("fee", "tuition")
CREDIT_WORDS = ("credit", "credits")
OFFICE_WORDS = ("where", "room", "located", "location", "address", "hours", "open", "contact")


def route(text: str, office_names: set[str]) -> Intent:
    t = text.lower().strip().rstrip("?!.")
    if t in GREETINGS:
        return Intent.GREETING
    if any(w in t for w in FEE_WORDS) and any(w in t for w in CREDIT_WORDS):
        return Intent.FEE
    if any(name in t for name in office_names) and any(w in t for w in OFFICE_WORDS):
        return Intent.OFFICE
    return Intent.RULE