def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user(client):
    payload = {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "securepass123",
        "role": "analyst",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "johndoe"
    assert data["email"] == "john@example.com"
    assert data["role"] == "user"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data


def test_register_duplicate_username(client):
    payload = {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "securepass123",
    }
    client.post("/api/v1/auth/register", json=payload)

    duplicate = {
        "username": "johndoe",
        "email": "jane@example.com",
        "password": "securepass123",
    }
    response = client.post("/api/v1/auth/register", json=duplicate)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "analyst1",
            "email": "analyst@example.com",
            "password": "securepass123",
            "role": "analyst",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "analyst1", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_me_authenticated(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin1",
            "email": "admin@example.com",
            "password": "securepass123",
            "role": "admin",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin1", "password": "securepass123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin1"
    assert data["role"] == "user"


def test_get_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
