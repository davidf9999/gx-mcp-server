import pytest
from fastapi.testclient import TestClient

from main import app as main_app


@pytest.fixture(scope="module")
def test_client():
    with TestClient(main_app) as client:
        yield client


def test_health_endpoint(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
