import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))
# Tests must never hit a real provider or the developer's database.
os.environ["LLM_PROVIDER"] = "mock"

from app.llm import MockProvider  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def db_url(tmp_path):
    return f"sqlite:///{(tmp_path / 'test.db').as_posix()}"


@pytest.fixture
def client(db_url):
    app = create_app(database_url=db_url, provider_factory=MockProvider)
    with TestClient(app) as c:
        yield c
