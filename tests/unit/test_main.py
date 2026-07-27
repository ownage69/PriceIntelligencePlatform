import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.router import api_router

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_action_logging_middleware_bypass():
    response = client.get("/docs")
    assert response.status_code == 200

@pytest.mark.parametrize("method,path", [
    ("GET", "/health"),
    ("POST", "/health"),
    ("PUT", "/health"),
    ("PATCH", "/health"),
    ("DELETE", "/health"),
    ("OPTIONS", "/health"),  
])
def test_action_logging_middleware_methods(method, path):
    response = client.request(method, path)
    assert response.status_code in (200, 405)

def test_router_includes():
    assert len(api_router.routes) > 0
