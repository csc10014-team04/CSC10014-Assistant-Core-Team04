"""Deterministic guardrails that run BEFORE retrieval or any LLM call."""

from __future__ import annotations

import re

PRIVATE_PATTERNS = [
    r"\b(my|a) (friend|classmate|roommate)'?s?\b.*\b(grade|score|gpa|result|phone|address)",
    r"\b(grade|score|gpa|result|phone|address)s?\b.*\b(of|for) (another|other) student",
    r"\b(grade|score|gpa|result|phone|address)s?\b.*\b(my|a) (friend|classmate|roommate)",
    r"\b\d{8}\b",  # looks like a student id
    # an unnamed third person ("that girl", "this guy"): we cannot tell who, so never answer about them
    r"\b(that|this|the) (girl|boy|guy|man|woman|person)\b",
    # credentials of someone else / of the system
    r"\bpasswords? (of|for)\b",
    r"\b(admin|administrator|teacher|lecturer|dean)'?s? (password|account|login)\b",
]

# Topics that are NOT in our documents. The nearest chunk would be about something else, so a
# retrieval score alone cannot catch them: escalate to a human instead of quoting the wrong rule.
UNSUPPORTED_PATTERNS = [
    r"\bopen[- ]?book\b",  # exam format is not in the handbook
    r"\bwhen (is|are|will be) (the|my|our) (\w+ )?(exams?|midterms?|finals?)\b",  # exam dates are not in the handbook
    r"\b(dean|lecturer|teacher|professor|advisor|head)'?s? (e-?mail|phone|number|address|office)\b",
    r"\b(e-?mail|phone( number)?|contact) (of|for) (the |my )?(dean|lecturer|teacher|professor|advisor|head)\b",
]


def is_private_request(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in PRIVATE_PATTERNS)


def is_unsupported_request(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in UNSUPPORTED_PATTERNS)


PRIVATE_REPLY = "I can't share information about other students. You can only see your own records after logging in."
