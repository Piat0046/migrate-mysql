"""Health check endpoint tests."""


def test_health_check(client):
    """Test health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
