import sys

# Ensure compatibility whether package is loaded as 'assistant' or 'assistant_core'
if "assistant_core" not in sys.modules:
    try:
        import assistant
        sys.modules["assistant_core"] = assistant
    except ImportError:  # pragma: no cover
        pass

import pytest

try:
    from assistant.router import Intent, route
except ImportError:  # pragma: no cover
    from assistant_core.router import Intent, route

OFFICES = {"library", "training office"}


# --- Original Unit Tests ---


def test_route_greeting():
    assert route("hello", OFFICES) == Intent.GREETING
    assert route("xin chao!", OFFICES) == Intent.GREETING


def test_route_fee():
    assert route("tuition for 18 credits", OFFICES) == Intent.FEE
    assert route("what is the fee?", OFFICES) == Intent.FEE


def test_route_office():
    assert route("where is the library?", OFFICES) == Intent.OFFICE
    assert route("training office opening hours", OFFICES) == Intent.OFFICE


def test_route_rule():
    assert route("can I register my thesis with 118 credits?", OFFICES) == Intent.RULE


# --- Characterization Tests (Preserving Monolith Legacy Behavior) ---


@pytest.mark.parametrize(
    ("query", "expected_intent"),
    [
        ("hi", Intent.GREETING),
        ("tuition for 18 credits and 2 retake", Intent.FEE),
        ("where is the library", Intent.OFFICE),
        ("can I register my thesis with 118 credits", Intent.RULE),
        ("tuition 40 credits", Intent.FEE),
    ],
)
def test_characterization_monolith_queries(query, expected_intent):
    """Characterize intent classification for the monolith's standard test cases."""
    assert route(query, OFFICES) == expected_intent


# --- Comprehensive Unit Tests: Intent Enum ---


def test_intent_enum_values():
    assert Intent.GREETING == "greeting"
    assert Intent.FEE == "fee"
    assert Intent.OFFICE == "office"
    assert Intent.RULE == "rule"
    assert Intent.UNKNOWN == "unknown"


# --- Comprehensive Unit Tests: route ---


@pytest.mark.parametrize(
    "greeting_query",
    [
        "hi",
        "hello",
        "hey",
        "xin chao",
        "chao",
        "HI",
        "Hello!",
        "HEY?",
        "  xin chao.  ",
    ],
)
def test_route_greeting_variations(greeting_query):
    assert route(greeting_query, OFFICES) == Intent.GREETING


@pytest.mark.parametrize(
    "fee_query",
    [
        "tuition",
        "what is the fee?",
        "TUITION FEE",
        "how much fee for 20 credits?",
        "Tuition calculation for retake",
    ],
)
def test_route_fee_variations(fee_query):
    assert route(fee_query, OFFICES) == Intent.FEE


def test_route_office_case_insensitivity():
    assert route("Where is the LIBRARY?", OFFICES) == Intent.OFFICE
    assert route("TRAINING OFFICE location", OFFICES) == Intent.OFFICE
    # Office name itself with mixed case
    assert route("where is the clinic?", {"Clinic", "Dormitory"}) == Intent.OFFICE


@pytest.mark.parametrize(
    "rule_query",
    [
        "how do I apply for graduation?",
        "what are the scholarship requirements?",
        "can I register my thesis with 118 credits?",
        "exam rules and regulations",
    ],
)
def test_route_rule_queries(rule_query):
    assert route(rule_query, OFFICES) == Intent.RULE


def test_route_default_office_names():
    """Verify route operates safely with default/None office_names."""
    assert route("hello") == Intent.GREETING
    assert route("tuition for 15 credits") == Intent.FEE
    assert route("where is the library?", None) == Intent.RULE
    assert route("where is the library?", set()) == Intent.RULE


def test_route_deterministic():
    """Verify deterministic routing across repeated invocations."""
    results = [route("tuition for 18 credits", OFFICES) for _ in range(20)]
    assert len(set(results)) == 1
    assert results[0] == Intent.FEE
