

from typing import Protocol, runtime_checkable

from assistant.errors import InvalidRequest, ProviderError
from assistant.rules import reply


@runtime_checkable
class Responder(Protocol):
    def respond(self, message: str) -> str:
        ...


class TemplateResponder:
    def respond(self, message: str) -> str:
        if not isinstance(message, str) or not message.strip():
            raise InvalidRequest("Message must be a non-empty string")
        return reply(message)


class StubLLMResponder:
    def __init__(self, fail: bool = False):
        self.fail = fail

    def respond(self, message: str) -> str:
        if not isinstance(message, str) or not message.strip():
            raise InvalidRequest("Message must be a non-empty string")
        if self.fail:
            raise ProviderError("Simulated LLM provider failure")
        return f"Stub LLM response to: {message}"
