"""Block real model requests throughout the automated test suite."""

import pytest
from pydantic_ai.models import override_allow_model_requests


@pytest.fixture(autouse=True)
def no_real_model_requests():
    with override_allow_model_requests(False):
        yield
