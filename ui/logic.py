"""Pure UI helper functions decoupled from Streamlit for unit testing."""

from __future__ import annotations

import time

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I can answer questions about fees, offices and the student handbook. "
    'Try: "Can I register my thesis with 118 credits?"'
)
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retake",
    "Where is the library?",
    "I lost my student card",
]


def word_stream(text: str, delay: float = 0.03):
    """Yield the answer word by word for a typing effect."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)


def validate_input(text: str) -> str | None:
    """Return an error message for invalid input, or None when valid."""
    cleaned = text.strip()
    if not cleaned:
        return "Please type a question."
    if len(cleaned) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


def format_sources(sources: list[dict]) -> str:
    """Format source citations as a single summary line, or empty string if none."""
    if not sources:
        return ""
    return "Sources: " + "; ".join(f"{src['id']} — {src['title']}" for src in sources)


def status_note(result: ChatResult) -> str | None:
    """Return a short status note explaining escalation or degraded fallback."""
    if result.escalate:
        return "I could not find this in the official documents. A staff member can help: Training Office, room I.101."
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None


def set_rating(rated: dict, request_id: str, rating: int) -> bool:
    """Store latest rating and return True only if it changed."""
    if rated.get(request_id) == rating:
        return False
    rated[request_id] = rating
    return True
