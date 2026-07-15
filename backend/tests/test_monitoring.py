def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "skyassist-ai"
    assert "database" in data
    assert "status" in data


def test_metrics_endpoint(client, db_session):
    from models.user import User, UserRole

    client.post(
        "/api/v1/auth/register",
        json={
            "username": "metricsadmin",
            "email": "metrics@example.com",
            "password": "securepass123",
        },
    )
    user = db_session.query(User).filter(User.username == "metricsadmin").first()
    user.role = UserRole.ADMIN
    db_session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"username": "metricsadmin", "password": "securepass123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.get("/health")
    response = client.get("/metrics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "request_count" in data
    assert "error_count" in data
    assert "avg_duration_ms" in data
    assert data["request_count"] >= 1


def test_security_headers(client):
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "X-Response-Time-Ms" in response.headers


def test_metrics_unauthenticated(client):
    response = client.get("/metrics")
    assert response.status_code == 401
