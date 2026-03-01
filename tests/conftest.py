import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from api.main import app
from api.k8s_client import get_k8s_client


@pytest.fixture
def mock_k8s():
    return MagicMock()


@pytest.fixture
def client(mock_k8s):
    app.dependency_overrides[get_k8s_client] = lambda: mock_k8s
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
