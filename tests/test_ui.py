"""Unit and Streamlit AppTest checks for the Lab 7 UI."""

from pathlib import Path

import httpx
import pytest

from ui.api_client import AssistantClient, ChatResult
from ui.logic import WELCOME, format_sources, reset_chat_state, set_rating, status_note, validate_input, word_stream

OK = {
    "answer": "Room B.201",
    "intent": "office",
    "sources": [{"id": "S26#1", "title": "1 Library borrowing"}],
    "degraded": False,
    "escalate": False,
    "path": "deterministic",
    "request_id": "abc123",
}


def client_with(handler) -> AssistantClient:
    return AssistantClient("http://api.test", transport=httpx.MockTransport(handler))


def test_ask_ok():
    res = client_with(lambda req: httpx.Response(200, json=OK)).ask("where is the library", "s1")
    assert res.ok and res.answer == "Room B.201" and res.request_id == "abc123"


def test_ask_backend_down():
    def boom(req):
        raise httpx.ConnectError("refused", request=req)

    res = client_with(boom).ask("hi", "s1")
    assert not res.ok and "backend" in res.error


def test_ask_timeout():
    def timeout(req):
        raise httpx.ReadTimeout("timed out", request=req)

    res = client_with(timeout).ask("hi", "s1")
    assert not res.ok and "taking too long" in res.error


def test_ask_rate_limit():
    res = client_with(lambda req: httpx.Response(429)).ask("hi", "s1")
    assert not res.ok and "wait a minute" in res.error


def test_ask_validation_and_server_errors():
    assert "type a question" in client_with(lambda req: httpx.Response(422)).ask("", "s").error
    assert "error 500" in client_with(lambda req: httpx.Response(500)).ask("x", "s").error


def test_feedback():
    assert client_with(lambda req: httpx.Response(201, json={})).send_feedback("abc123", 1)
    assert client_with(lambda req: httpx.Response(201, json={})).send_feedback("abc123", -1)


def test_healthy():
    assert client_with(lambda req: httpx.Response(200, json={"status": "ok"})).healthy() is True

    def boom(req):
        raise httpx.ConnectError("down", request=req)

    assert client_with(boom).healthy() is False


def test_validate_input():
    assert validate_input("   ") == "Please type a question."
    assert validate_input("x" * 2001).startswith("Your question is too long")
    assert validate_input("hello") is None


def test_format_sources():
    assert format_sources([]) == ""
    assert format_sources(OK["sources"]) == "Sources: S26#1 — 1 Library borrowing"


def test_status_note():
    assert "Training Office" in status_note(ChatResult(ok=True, escalate=True))
    assert "source document" in status_note(ChatResult(ok=True, degraded=True))
    assert status_note(ChatResult(ok=True)) is None


def test_word_stream():
    assert "".join(word_stream("a b c", delay=0)).strip() == "a b c"


def test_set_rating_can_change_opinion():
    rated = {}
    assert set_rating(rated, "r1", 1) is True
    assert set_rating(rated, "r1", 1) is False  # same vote does not resend
    assert set_rating(rated, "r1", -1) is True
    assert rated["r1"] == -1


def test_page_loads_and_shows_answer(monkeypatch):
    """Verify the Streamlit page renders answers and sources without crashing."""
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(AssistantClient, "healthy", lambda self: True)
    monkeypatch.setattr(
        AssistantClient,
        "ask",
        lambda self, m, s: ChatResult(ok=True, answer="Room B.201", sources=OK["sources"], request_id="abc123"),
    )
    app_path = str(Path(__file__).resolve().parents[1] / "ui" / "app.py")
    at = AppTest.from_file(app_path, default_timeout=10).run()
    assert not at.exception
    at.sidebar.button[1].click().run()
    assert not at.exception
    assert any("Room B.201" in m.value for m in at.markdown)
    assert at.expander[0].label.startswith("📄 Sources (1)")


def test_rating_buttons_stay_and_can_switch(monkeypatch):
    """Verify F1 thumbs-up and thumbs-down buttons send feedback and can switch."""
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    sent = []
    monkeypatch.setattr(AssistantClient, "healthy", lambda self: True)
    monkeypatch.setattr(AssistantClient, "send_feedback", lambda self, rid, r, c=None: sent.append(r) or True)
    monkeypatch.setattr(
        AssistantClient,
        "ask",
        lambda self, m, s: ChatResult(ok=True, answer="Room B.201", request_id="abc123"),
    )
    app_path = str(Path(__file__).resolve().parents[1] / "ui" / "app.py")
    at = AppTest.from_file(app_path, default_timeout=10).run()
    at.sidebar.button[1].click().run()
    up = [b for b in at.button if b.label == "👍"][0]
    up.click().run()
    assert not at.exception
    down = [b for b in at.button if b.label == "👎"][0]
    down.click().run()
    assert sent == [1, -1]


def test_reset_chat_state():
    """Verify H1 reset helper clears messages, ratings, and pending state."""
    state = {
        "session_id": "old_session_1",
        "messages": [{"role": "user", "content": "hi"}],
        "rated": {"r1": 1},
        "pending": "queued",
    }
    new_sid = reset_chat_state(state)
    assert new_sid != "old_session_1" and len(new_sid) == 12
    assert state["session_id"] == new_sid
    assert state["messages"] == [{"role": "assistant", "content": WELCOME}]
    assert state["rated"] == {}
    assert "pending" not in state


def test_new_chat_button_clears_history(monkeypatch):
    """Verify the sidebar New chat button resets the conversation in Streamlit."""
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(AssistantClient, "healthy", lambda self: True)
    monkeypatch.setattr(
        AssistantClient,
        "ask",
        lambda self, m, s: ChatResult(ok=True, answer="Room B.201", request_id="abc123"),
    )
    app_path = str(Path(__file__).resolve().parents[1] / "ui" / "app.py")
    at = AppTest.from_file(app_path, default_timeout=10).run()
    old_sid = at.session_state["session_id"]
    # sidebar.button[0] is "New chat"; button[1] is the first example question
    at.sidebar.button[1].click().run()
    assert any("Room B.201" in m.value for m in at.markdown)
    at.sidebar.button[0].click().run()
    assert not at.exception
    assert at.session_state["session_id"] != old_sid
    assert not any("Room B.201" in m.value for m in at.markdown)
