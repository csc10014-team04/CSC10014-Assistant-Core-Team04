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
    from assistant.errors import InvalidRequest
    from assistant.tools import parse_credits, tuition
except ImportError:  # pragma: no cover
    from assistant_core.errors import InvalidRequest
    from assistant_core.tools import parse_credits, tuition


# --- Original Unit Tests ---


def test_parse_with_retake():
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_parse_without_retake():
    assert parse_credits("tuition for 15 credits") == (15, 0)


def test_parse_no_credits():
    with pytest.raises(InvalidRequest):
        parse_credits("tuition fee calculation")


def test_tuition_value():
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000


def test_tuition_zero_retake():
    assert tuition(10, 0, 450_000, 1.5, 30) == 4_500_000


@pytest.mark.parametrize("credits", [0, 31])
def test_tuition_out_of_range(credits):
    with pytest.raises(InvalidRequest):
        tuition(credits, 0, 450_000, 1.5, 30)


# --- Characterization Tests (Preserving Monolith Legacy Behavior) ---


def test_characterization_legacy_tuition_calculation():
    """Characterize exact legacy tuition calculation: 18 credits + 2 retakes.
    
    18 * 450,000 = 8,100,000 VND
    2 * 450,000 * 1.5 = 1,350,000 VND
    Total expected = 9,450,000 VND.
    """
    c, r = parse_credits("tuition for 18 credits and 2 retake")
    assert (c, r) == (18, 2)
    assert tuition(c, r, 450_000, 1.5, 30) == 9_450_000


def test_characterization_legacy_too_many_credits():
    """Characterize legacy response for 'tuition 40 credits' exceeding max 30 credits."""
    c, r = parse_credits("tuition 40 credits")
    assert c == 40
    assert r == 0
    with pytest.raises(InvalidRequest, match="between 1 and 30"):
        tuition(c, r, 450_000, 1.5, 30)


# --- Comprehensive Unit Tests: parse_credits ---


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("fee for 18 credits and 2 retakes", (18, 2)),
        ("fee for 2 retake and 18 credits", (18, 2)),
        ("TUITION FOR 12 CREDITS AND 1 RETAKE", (12, 1)),
        ("tuition for 1 credit", (1, 0)),
        ("fee 20 credits and 3 retake", (20, 3)),
        ("tuition for 0 credits", (0, 0)),
    ],
)
def test_parse_credits_variations(query, expected):
    assert parse_credits(query) == expected


@pytest.mark.parametrize(
    "invalid_query",
    [
        "",
        "   ",
        "tuition fee without numbers",
        "only 2 retake",  # retake present but no base credits
    ],
)
def test_parse_credits_invalid_inputs(invalid_query):
    with pytest.raises(InvalidRequest):
        parse_credits(invalid_query)


# --- Comprehensive Unit Tests: tuition ---


def test_tuition_default_parameters():
    """Verify default rates (450,000 rate, 1.5 multiplier, 30 max credits)."""
    assert tuition(18, 2) == 9_450_000
    assert tuition(10) == 4_500_000


def test_tuition_boundary_values():
    """Verify boundary conditions for 1 (min) and 30 (max) credits."""
    assert tuition(1, 0, 450_000, 1.5, 30) == 450_000
    assert tuition(30, 0, 450_000, 1.5, 30) == 13_500_000


@pytest.mark.parametrize("invalid_credits", [-10, -1, 0, 31, 50, 100])
def test_tuition_invalid_credits_range(invalid_credits):
    with pytest.raises(InvalidRequest):
        tuition(invalid_credits, 0, 450_000, 1.5, 30)


@pytest.mark.parametrize(
    ("credits", "retake", "rate", "mult"),
    [
        (15, -1, 450_000, 1.5),
        (15, 0, -100, 1.5),
        (15, 0, 450_000, -1.0),
    ],
)
def test_tuition_negative_parameters(credits, retake, rate, mult):
    with pytest.raises(InvalidRequest):
        tuition(credits, retake, rate, mult, 30)


def test_tuition_pure_function_deterministic():
    """Verify that tuition is pure and deterministic across repeated calls."""
    results = [tuition(18, 2, 450_000, 1.5, 30) for _ in range(20)]
    assert len(set(results)) == 1
    assert results[0] == 9_450_000
