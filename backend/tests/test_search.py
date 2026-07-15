def _seed(client, auth_headers):
    content = b"2026-06-15 ERROR [auth-service] Login failed for user admin"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("search.log", content, "text/plain")},
    )
    client.post(f"/api/v1/logs/{upload.json()['id']}/parse", headers=auth_headers)
    client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={"issue": "Auth failure ticket", "priority": "High", "root_cause": "Invalid credentials"},
    )
    client.post(
        "/api/v1/ai/ask",
        headers=auth_headers,
        json={"question": "Why did authentication fail?"},
    )


def test_global_search(client, auth_headers):
    _seed(client, auth_headers)
    response = client.get("/api/v1/search?q=auth", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["results"]) >= 1
    types = {r["type"] for r in data["results"]}
    assert len(types) >= 1


def test_search_incidents_scope(client, auth_headers):
    _seed(client, auth_headers)
    response = client.get("/api/v1/search?scope=incidents&q=AUTH", headers=auth_headers)
    assert response.status_code == 200
    assert all(r["type"] == "incident" for r in response.json()["results"])


def test_search_pagination(client, auth_headers):
    _seed(client, auth_headers)
    response = client.get("/api/v1/search?page=1&page_size=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["results"]) <= 2


def test_search_filter_severity(client, auth_headers):
    _seed(client, auth_headers)
    response = client.get("/api/v1/search?scope=incidents&severity=High", headers=auth_headers)
    assert response.status_code == 200


def test_search_unauthorized(client):
    assert client.get("/api/v1/search").status_code == 401
