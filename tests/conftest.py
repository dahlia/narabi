from os import environ

import pytest

from narabi.backends.base import Backend, from_url


@pytest.fixture
def backend_url() -> str:
    return environ.get("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture
def backend(backend_url: str) -> Backend:
    return from_url(backend_url)
