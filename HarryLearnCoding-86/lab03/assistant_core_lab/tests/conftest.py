from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, Office, OfficeDirectory, Rule
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


@pytest.fixture
def settings():
    return Settings(
        data_dir=Path("data"),
        llm_provider="stub",
        credit_rate_vnd=450_000,
        retake_multiplier=1.5,
        max_credits=30,
        log_level="INFO",
    )


@pytest.fixture
def offices():
    return OfficeDirectory(
        {
            "library": Office("Library", "B.201", "Mon-Sat 07:00-20:00"),
            "training office": Office("Training Office", "A.101", "Mon-Fri 07:30-16:30"),
        }
    )


@pytest.fixture
def handbook():
    return Handbook(
        [
            Rule(
                id="H26-5.3",
                title="Thesis registration",
                text=(
                    "Students may register a thesis when they have at least 120 "
                    "accumulated credits and a GPA of at least 2.0."
                ),
            ),
            Rule(
                id="H26-4.2",
                title="Retaking a course",
                text=(
                    "Students may retake a course they failed. Retake credits are charged at "
                    "1.5 times the normal rate. Final-year students must register retakes before week 2."
                ),
            ),
        ]
    )


@pytest.fixture
def responder():
    return StubLLMResponder()


@pytest.fixture
def service(settings, offices, handbook, responder):
    return AssistantService(settings, offices, handbook, responder)
