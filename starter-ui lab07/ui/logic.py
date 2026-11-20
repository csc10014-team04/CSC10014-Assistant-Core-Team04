"""UI logic without Streamlit, so it can be unit-tested."""
from __future__ import annotations

import time

from ui.api_client import ChatResult

WELCOME = ("Hi! I can answer questions about fees, offices and the student handbook. "
           "Try: “Can I register my thesis with 118 credits?”")
EXAMPLES = ["Can I register my thesis with 118 credits?", "Tuition for 18 credits and 2 retake",
            "Where is the library?", "I lost my student card"]


def word_stream(text: str, delay: float = 0.03):
    """Yield the answer word by word, for a typing effect."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)


def validate_input(text: str) -> str | None:
    """Return an error message for bad input, or None if it is fine."""
    t = text.strip()
    if not t:
        return "Please type a question."
    if len(t) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


def format_sources(sources: list[dict]) -> str:
    """'Sources: H26#5.3 — 5.3 Thesis registration' or '' if none."""
    if not sources:
        return ""
    return "Sources: " + "; ".join(f"{s['id']} — {s['title']}" for s in sources)



def status_note(result: ChatResult) -> str | None:
    """A short note shown under the answer, explaining special situations."""
    if result.escalate:
        return "I could not find this in the official documents. A staff member can help: Training Office, room I.101."
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None


def set_rating(rated: dict, request_id: str, rating: int) -> bool:
    """Remember the user's latest rating. Return True if it changed (so it must be sent to the API)."""
    if rated.get(request_id) == rating:
        return False
    rated[request_id] = rating
    return True
