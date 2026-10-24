from assistant_core.models import Intent
from assistant_core.router import route

OFFICES = {"library", "training office"}


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
