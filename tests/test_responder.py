
import pytest

from assistant.errors import AssistantError, InvalidRequest, ProviderError
from assistant.responder import Responder, StubLLMResponder, TemplateResponder


def test_template_responder():
    responder = TemplateResponder()
    assert "Hello" in responder.respond("hi")


def test_template_office_lookup():
    responder = TemplateResponder()
    assert "I.101" in responder.respond("Where is the Training Office?")


def test_stub_responder():
    responder = StubLLMResponder()
    assert "Stub LLM response" in responder.respond("Hello")


def test_stub_provider_failure():
    responder = StubLLMResponder(fail=True)
    with pytest.raises(ProviderError):
        responder.respond("Hello")


def test_invalid_request():
    responder = TemplateResponder()
    with pytest.raises(InvalidRequest):
        responder.respond("")


def test_exception_hierarchy():
    assert issubclass(ProviderError, AssistantError)
    assert issubclass(InvalidRequest, AssistantError)


def test_protocol_compatibility():
    assert isinstance(TemplateResponder(), Responder)
    assert isinstance(StubLLMResponder(), Responder)
