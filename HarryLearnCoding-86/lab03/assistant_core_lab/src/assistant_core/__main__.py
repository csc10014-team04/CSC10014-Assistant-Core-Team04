"""Command line interface for assistant_core."""

import logging
import sys
import time

from pydantic import ValidationError

from assistant_core.config import load_settings
from assistant_core.errors import AssistantError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService

log = logging.getLogger("assistant_core")


def build_service() -> AssistantService:
    settings = load_settings()
    setup_logging(settings.log_level)
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    responder = StubLLMResponder()
    return AssistantService(settings, offices, handbook, responder)


def main() -> None:
    try:
        service = build_service()
    except AssistantError as e:
        sys.stderr.write(f"Startup error: {e}\n")
        sys.exit(1)

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        start = time.perf_counter()
        try:
            msg = Message(text=query)
            res = service.handle(msg)
            latency = round((time.perf_counter() - start) * 1000, 1)
            record = logging.LogRecord(
                name="assistant_core",
                level=logging.INFO,
                pathname=__file__,
                lineno=0,
                msg="handled",
                args=(),
                exc_info=None,
            )
            record.intent = res.intent.value
            record.latency_ms = latency
            record.session = msg.session_id
            record.degraded = res.degraded
            log.handle(record)
            print(res.answer)
        except (AssistantError, ValidationError, ValueError, KeyError) as e:
            latency = round((time.perf_counter() - start) * 1000, 1)
            record = logging.LogRecord(
                name="assistant_core",
                level=logging.ERROR,
                pathname=__file__,
                lineno=0,
                msg=str(e),
                args=(),
                exc_info=None,
            )
            record.latency_ms = latency
            log.handle(record)
            print(f"Error: {e}")
            sys.exit(1)
        return

    print("assistant ready")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip().lower() in ("quit", "exit"):
            break
        if not line.strip():
            continue
        start = time.perf_counter()
        try:
            msg = Message(text=line)
            res = service.handle(msg)
            latency = round((time.perf_counter() - start) * 1000, 1)
            record = logging.LogRecord(
                name="assistant_core",
                level=logging.INFO,
                pathname=__file__,
                lineno=0,
                msg="handled",
                args=(),
                exc_info=None,
            )
            record.intent = res.intent.value
            record.latency_ms = latency
            record.session = msg.session_id
            record.degraded = res.degraded
            log.handle(record)
            print(res.answer)
        except (AssistantError, ValidationError, ValueError, KeyError) as e:
            latency = round((time.perf_counter() - start) * 1000, 1)
            record = logging.LogRecord(
                name="assistant_core",
                level=logging.ERROR,
                pathname=__file__,
                lineno=0,
                msg=str(e),
                args=(),
                exc_info=None,
            )
            record.latency_ms = latency
            log.handle(record)
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
