"""Test configuration.

Force the offline template answerer for the whole suite so tests are hermetic:
they must not depend on ambient ``OPENAI_API_KEY`` values or network access.
"""

import os


os.environ["EVIDENCEQA_ANSWER_PROVIDER"] = "template"

import pytest

from app.main import app


@pytest.fixture(autouse=True)
def reset_shared_app_state() -> None:
    """Tests share the module-level FastAPI app; reset mutable state each time."""
    app.state.api_key = None
    yield
