import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.api.routes.health import health_check
from app.main import app

def test_health_check_endpoint():
    """Verify that the health check endpoint returns expected status and metadata."""
    response = health_check()
    assert response["status"] == "healthy"
    assert response["service"] == "KrishiInsights API"
    assert response["version"] == "0.1.0"
    assert "timestamp" in response
    print("✓ test_health_check_endpoint passed: ", response)

def test_app_routes():
    """Verify that the FastAPI application initializes with configured routes."""
    paths = list(app.openapi()["paths"].keys())
    assert "/api/health" in paths
    assert "/" in paths
    print("✓ test_app_routes passed: ", paths)

if __name__ == "__main__":
    test_health_check_endpoint()
    test_app_routes()
    print("All backend tests completed successfully!")
