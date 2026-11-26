"""HTTP client wrapper for talking to the assistant API."""

from __future__ import annotations

from dataclasses import dataclass, field

import httpx


@dataclass
class ChatResult:
    """Normalized outcome returned by the API client."""

    ok: bool
    answer: str = ""
    intent: str = ""
    sources: list[dict] = field(default_factory=list)
    path: str = ""
    escalate: bool = False
    degraded: bool = False
    request_id: str = ""
    error: str = ""  # friendly message when ok is False


class AssistantClient:
    """Thin HTTP client connecting the UI to FastAPI endpoints."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout_s: float = 20.0,
        transport: httpx.BaseTransport | None = None,
    ):
        self._http = httpx.Client(base_url=base_url, timeout=timeout_s, transport=transport)

    def ask(self, message: str, session_id: str) -> ChatResult:
        """Send a chat question and map any HTTP or network failure to ChatResult."""
        try:
            res = self._http.post("/v1/chat", json={"message": message, "session_id": session_id})
        except httpx.TimeoutException:
            return ChatResult(ok=False, error="The assistant is taking too long. Please try again.")
        except httpx.HTTPError:
            return ChatResult(ok=False, error="Cannot reach the assistant. Is the backend running?")
        if res.status_code == 422:
            return ChatResult(ok=False, error="Please type a question (1-2000 characters).")
        if res.status_code == 429:
            return ChatResult(ok=False, error="Too many questions in a short time. Please wait a minute.")
        if res.status_code != 200:
            return ChatResult(ok=False, error=f"Something went wrong on our side (error {res.status_code}).")
        data = res.json()
        return ChatResult(
            ok=True,
            answer=data["answer"],
            intent=data["intent"],
            sources=data.get("sources", []),
            path=data.get("path", ""),
            escalate=data.get("escalate", False),
            degraded=data.get("degraded", False),
            request_id=data["request_id"],
        )

    def send_feedback(self, request_id: str, rating: int, comment: str | None = None) -> bool:
        """Submit thumbs-up or thumbs-down feedback for a response."""
        try:
            res = self._http.post("/v1/feedback", json={"request_id": request_id, "rating": rating, "comment": comment})
        except httpx.HTTPError:
            return False
        return res.status_code == 201

    def healthy(self) -> bool:
        """Check whether the backend API is reachable."""
        try:
            return self._http.get("/health").status_code == 200
        except httpx.HTTPError:
            return False
