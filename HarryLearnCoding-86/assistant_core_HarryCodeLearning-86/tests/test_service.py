import pytest
from pydantic import ValidationError

from assistant_core.errors import ProviderError
from assistant_core.models import Intent, Message
from assistant_core.responder import StubLLMResponder


def test_service_greeting(service):
    res = service.handle(Message(text="hi"))
    assert res.intent == Intent.GREETING
    assert "Hello! I can help with offices, fees and rules." in res.answer
    assert res.degraded is False


def test_service_fee(service):
    res = service.handle(Message(text="tuition for 18 credits and 2 retake"))
    assert res.intent == Intent.FEE
    assert "9,450,000 VND" in res.answer
    assert res.degraded is False


def test_service_office(service):
    res = service.handle(Message(text="where is the library?"))
    assert res.intent == Intent.OFFICE
    assert "room B.201" in res.answer
    assert res.degraded is False


def test_service_rule(service):
    res = service.handle(Message(text="can I register my thesis with 118 credits"))
    assert res.intent == Intent.RULE
    assert len(res.sources) == 1
    assert res.sources[0].id == "H26-5.3"
    assert "Thesis registration" in res.answer
    assert res.degraded is False


def test_service_unknown_rule(service):
    res = service.handle(Message(text="xyz random question unknown"))
    assert res.intent == Intent.UNKNOWN
    assert "Sorry, I don't know that yet." in res.answer
    assert res.degraded is False


def test_fallback_when_provider_fails(service):
    """Verify that provider failure is intercepted and template fallback is used with degraded=True."""
    service.responder = StubLLMResponder(fail=True)
    res = service.handle(Message(text="thesis registration credits"))
    assert res.degraded is True
    assert len(res.sources) == 1
    assert res.sources[0].id == "H26-5.3"
    assert res.sources[0].title == "Thesis registration"
    assert res.intent == Intent.RULE
    assert "Thesis registration: Students may register a thesis" in res.answer


def test_provider_failure_does_not_raise_to_caller(service):
    """Verify provider failures never escape handle() as an exception."""
    service.responder = StubLLMResponder(fail=True)
    try:
        res = service.handle(Message(text="thesis registration credits"))
        assert res.degraded is True
    except ProviderError:
        pytest.fail("ProviderError should have been caught internally and fallen back gracefully")


def test_empty_message_rejected():
    with pytest.raises(ValidationError):
        Message(text="")


def test_message_max_length_rejected():
    with pytest.raises(ValidationError):
        Message(text="a" * 2001)
