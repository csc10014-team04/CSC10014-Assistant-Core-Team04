"""Deterministic tools for calculation."""

import re
import sys
import types

try:
    from assistant.errors import InvalidRequest
except ImportError:  # pragma: no cover
    from assistant_core.errors import InvalidRequest  # type: ignore

# Expose assistant_core.tools and assistant_core.errors aliases for compatibility
if "assistant_core.errors" not in sys.modules:
    _err_mod = types.ModuleType("assistant_core.errors")
    _err_mod.InvalidRequest = InvalidRequest
    sys.modules["assistant_core.errors"] = _err_mod

if "assistant_core.tools" not in sys.modules:
    sys.modules["assistant_core.tools"] = sys.modules[__name__]


def parse_credits(text: str) -> tuple[int, int]:
    """Extract (credits, retake_credits) from 'fee for 18 credits and 2 retake'.

    Raises InvalidRequest if no standard credits number is found.
    """
    retake = re.search(r"(\d+)\s*retake", text, re.IGNORECASE)
    numbers = [int(n) for n in re.findall(r"\d+", text)]
    retake_n = int(retake.group(1)) if retake else 0
    others = numbers.copy()
    if retake:
        others.remove(retake_n)
    if not others:
        raise InvalidRequest("How many credits?")
    return others[0], retake_n


def tuition(
    credits: int,
    retake: int = 0,
    rate: int = 450_000,
    retake_multiplier: float = 1.5,
    max_credits: int = 30,
) -> int:
    """Calculate total tuition fee deterministically without I/O or side-effects.

    Formula: credits * rate + retake * rate * retake_multiplier
    Validates that credits are between 1 and max_credits (inclusive),
    and retake credits, rate, and multiplier are non-negative.
    """
    if not 1 <= credits <= max_credits:
        raise InvalidRequest(f"Credits must be between 1 and {max_credits}.")
    if retake < 0:
        raise InvalidRequest("Retake credits cannot be negative.")
    if rate < 0:
        raise InvalidRequest("Rate cannot be negative.")
    if retake_multiplier < 0:
        raise InvalidRequest("Retake multiplier cannot be negative.")
    return int(credits * rate + retake * rate * retake_multiplier)
