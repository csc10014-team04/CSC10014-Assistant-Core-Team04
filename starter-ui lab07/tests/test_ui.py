import httpx

from ui.api_client import AssistantClient, ChatResult
from ui.logic import format_sources, status_note, validate_input

OK = {"answer": "Room B.201", "intent": "office", "sources": [{"id": "S26#1", "title": "1 Library borrowing"}],
      "degraded": False, "escalate": False, "path": "deterministic", "request_id": "abc123"}


def client_with(handler) -> AssistantClient:
    return AssistantClient("http://api.test", transport=httpx.MockTransport(handler))


def test_ask_ok():
    r = client_with(lambda req: httpx.Response(200, json=OK)).ask("where is the library", "s1")
    assert r.ok and r.answer == "Room B.201" and r.request_id == "abc123"


def test_ask_backend_down():
    def boom(req):
        raise httpx.ConnectError("refused", request=req)
    r = client_with(boom).ask("hi", "s1")
    assert not r.ok and "backend" in r.error


def test_ask_validation_and_server_errors():
    assert "type a question" in client_with(lambda req: httpx.Response(422)).ask("", "s").error
    assert "error 500" in client_with(lambda req: httpx.Response(500)).ask("x", "s").error


def test_feedback():
    assert client_with(lambda req: httpx.Response(201, json={})).send_feedback("abc123", 1)


def test_validate_input():
    assert validate_input("   ") == "Please type a question."
    assert validate_input("x" * 2001).startswith("Your question is too long")
    assert validate_input("hello") is None


def test_format_sources():
    assert format_sources([]) == ""
    assert format_sources(OK["sources"]) == "Sources: S26#1 — 1 Library borrowing"


def test_status_note():
    assert "Training Office" in status_note(ChatResult(ok=True, escalate=True))
    assert status_note(ChatResult(ok=True)) is None


def test_word_stream():
    from ui.logic import word_stream
    assert "".join(word_stream("a b c", delay=0)).strip() == "a b c"


def test_page_loads_and_shows_answer(monkeypatch):
    """Load the real Streamlit page (catches crashes that unit tests miss)."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    monkeypatch.setattr(AssistantClient, "healthy", lambda self: True)
    monkeypatch.setattr(AssistantClient, "ask", lambda self, m, s: ChatResult(
        ok=True, answer="Room B.201", sources=OK["sources"], request_id="abc123"))
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ui" / "app.py"), default_timeout=10).run()
    assert not at.exception
    at.sidebar.button[0].click().run()   # an example question (the chat box is not reachable in AppTest 1.39)
    assert not at.exception
    assert any("Room B.201" in m.value for m in at.markdown)
    assert at.expander[0].label.startswith("📄 Sources (1)")


def test_set_rating_can_change_opinion():
    from ui.logic import set_rating
    rated = {}
    assert set_rating(rated, "r1", 1) is True      # first vote
    assert set_rating(rated, "r1", 1) is False     # same vote again: nothing to send
    assert set_rating(rated, "r1", -1) is True     # changed mind
    assert rated["r1"] == -1


def test_rating_buttons_stay_and_can_switch(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    sent = []
    monkeypatch.setattr(AssistantClient, "healthy", lambda self: True)
    monkeypatch.setattr(AssistantClient, "send_feedback", lambda self, rid, r, c=None: sent.append(r) or True)
    monkeypatch.setattr(AssistantClient, "ask", lambda self, m, s: ChatResult(ok=True, answer="Room B.201", request_id="abc123"))
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ui" / "app.py"), default_timeout=10).run()
    at.sidebar.button[0].click().run()
    up = [b for b in at.button if b.label == "👍"][0]
    up.click().run()
    assert not at.exception
    down = [b for b in at.button if b.label == "👎"][0]   # still there after voting
    down.click().run()
    assert sent == [1, -1]
