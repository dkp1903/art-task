import pytest
from fastapi.testclient import TestClient
from src.main import api  # Import the FastAPI instance

# Create a TestClient instance
client = TestClient(api)

@pytest.fixture(scope="module")
def test_client():
    # Setup code before running tests
    yield client
    # Teardown code after running tests

# Test for the /test endpoint
def test_api_online(test_client):
    response = test_client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"msg": "API is Online"}

# Test for CORS headers
def test_cors_headers(test_client):
    response = test_client.options("/test")
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"
    assert "access-control-allow-methods" in response.headers
    assert response.headers["access-control-allow-methods"] == "*"

# You can also add tests to ensure that the application respects the environment variable configurations
def test_dev_environment_config(monkeypatch):
    monkeypatch.setenv('APP_ENV', 'development')
    assert os.environ.get('APP_ENV') == 'development'
