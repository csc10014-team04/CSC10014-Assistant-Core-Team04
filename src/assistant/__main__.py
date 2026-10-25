"""Command line interface for assistant core."""

import logging
import sys
import time

from pydantic import ValidationError

try:
    from assistant.config import load_settings
except ImportError:  # pragma: no cover
    try:
        from assistant_core.config import load_settings  # type: ignore
    except ImportError:
        load_settings = None

try:
    from assistant.errors import AssistantError
except ImportError:  # pragma: no cover
    from assistant_core.errors import AssistantError  # type: ignore

try:
    from assistant.logging_setup import setup_logging
except ImportError:  # pragma: no cover
    from assistant_core.logging_setup import setup_logging  # type: ignore

try:
    from assistant.responder import StubLLMResponder
except ImportError:  # pragma: no cover
    try:
        from assistant_core.responder import StubLLMResponder  # type: ignore
    except ImportError:
        StubLLMResponder = None

try:
    from assistant.knowledge import Handbook, OfficeDirectory
    from assistant.models import Message
    from assistant.service import AssistantService
except ImportError:  # pragma: no cover
    try:
        from assistant_core.knowledge import Handbook, OfficeDirectory  # type: ignore
        from assistant_core.models import Message  # type: ignore
        from assistant_core.service import AssistantService  # type: ignore
    except ImportError:
        Handbook = None  # pending member 4 integration
        OfficeDirectory = None  # pending member 4 integration
        Message = None  # pending member 4 integration
        AssistantService = None  # pending member 1 integration

log = logging.getLogger("assistant")


def build_service() -> AssistantService:
    if load_settings is None or AssistantService is None or OfficeDirectory is None or Handbook is None:
        raise AssistantError("service dependencies not yet integrated")  # wait for other members
    settings = load_settings()
    setup_logging(settings.log_level)
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    responder = StubLLMResponder()
    return AssistantService(settings, offices, handbook, responder)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        service = build_service()
    except AssistantError as err:
        sys.stderr.write(f"Startup error: {err}\n")  # startup error to stderr
        return 1

    if args:
        query = " ".join(args)
        start_time = time.perf_counter()
        try:
            msg = Message(text=query)
            res = service.handle(msg)
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            log.info(
                "handled",
                extra={
                    "intent": res.intent.value,
                    "latency_ms": latency,
                    "session": msg.session_id,
                    "degraded": res.degraded,
                },
            )
            print(res.answer)  # answer to stdout
            return 0
        except (AssistantError, ValidationError, ValueError, KeyError) as err:
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            log.error(str(err), extra={"latency_ms": latency})  # error details to stderr
            print(f"Error: {err}")
            return 1

    print("assistant ready")  # interactive banner to stdout
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip().lower() in ("quit", "exit"):
            break
        if not line.strip():
            continue
        start_time = time.perf_counter()
        try:
            msg = Message(text=line)
            res = service.handle(msg)
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            log.info(
                "handled",
                extra={
                    "intent": res.intent.value,
                    "latency_ms": latency,
                    "session": msg.session_id,
                    "degraded": res.degraded,
                },
            )
            print(res.answer)  # answer to stdout
        except (AssistantError, ValidationError, ValueError, KeyError) as err:
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            log.error(str(err), extra={"latency_ms": latency})  # error details to stderr
            print(f"Error: {err}")
    return 0


# alias for assistant_core compatibility
if "assistant_core.__main__" not in sys.modules:
    sys.modules["assistant_core.__main__"] = sys.modules[__name__]


if __name__ == "__main__":
    sys.exit(main())
