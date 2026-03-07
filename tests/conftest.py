from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.k8s_client import get_k8s_client
from api.main import app


@pytest.fixture
def mock_k8s():
    mock = MagicMock()
    mock.check_connection.return_value = (True, None)
    return mock


@pytest.fixture
def client(mock_k8s):
    app.dependency_overrides[get_k8s_client] = lambda: mock_k8s
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
