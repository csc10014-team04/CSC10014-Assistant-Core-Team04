"""Structured logging configuration."""

import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """Format log records as single-line json objects."""

    def format(self, record: logging.LogRecord) -> str:
        data = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("intent", "latency_ms", "session", "degraded"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Configure json structured logging to stderr."""
    handler = logging.StreamHandler(sys.stderr)  # send logs to stderr
    handler.setFormatter(JsonFormatter())
    for name in ("assistant", "assistant_core"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(level)


# alias for assistant_core compatibility
if "assistant_core.logging_setup" not in sys.modules:
    sys.modules["assistant_core.logging_setup"] = sys.modules[__name__]
