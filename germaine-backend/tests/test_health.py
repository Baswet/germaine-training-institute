"""Verifies the one real Step 3 route: GET /api/health."""


def test_health_endpoint_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "germaine-backend"
    assert "time" in data


def test_health_endpoint_does_not_require_auth(client):
    # No Authorization header supplied — should still succeed, since
    # this is explicitly a public liveness check.
    response = client.get("/api/health")
    assert response.status_code == 200
