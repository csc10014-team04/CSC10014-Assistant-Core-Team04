
class AssistantError(Exception):
    pass


class ProviderError(AssistantError):
    pass


class InvalidRequest(AssistantError):
    pass
