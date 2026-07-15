def _seed_incidents(client, auth_headers):
    logs = [
        b"2026-06-15 10:00:00 ERROR [auth-service] Login failed for user admin",
        b"2026-06-15 10:01:00 ERROR [gateway] API timeout on /api/v1/proxy",
        b"2026-06-15 10:02:00 CRITICAL [database] Connection pool exhausted",
    ]
    for i, content in enumerate(logs):
        upload = client.post(
            "/api/v1/logs/upload",
            headers=auth_headers,
            files={"file": (f"analytics{i}.log", content, "text/plain")},
        )
        log_id = upload.json()["id"]
        client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)


def test_get_analytics_daily(client, auth_headers):
    _seed_incidents(client, auth_headers)

    response = client.get("/api/v1/analytics?period=daily", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "daily"
    assert len(data["incident_trends"]) == 7
    assert data["summary"]["incidents"] >= 1
    assert len(data["severity_distribution"]) >= 1
    assert len(data["top_error_categories"]) >= 1
    assert len(data["resolved_vs_unresolved"]) == 2
    assert len(data["alert_frequency"]) == 7
    assert data["summary"]["alerts"] >= 1


def test_get_analytics_weekly(client, auth_headers):
    _seed_incidents(client, auth_headers)

    response = client.get("/api/v1/analytics?period=weekly", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "weekly"
    assert len(data["incident_trends"]) == 8


def test_get_analytics_monthly(client, auth_headers):
    _seed_incidents(client, auth_headers)

    response = client.get("/api/v1/analytics?period=monthly", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["period"] == "monthly"
    assert len(data["incident_trends"]) == 6


def test_ticket_status_in_analytics(client, auth_headers):
    client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "SSL handshake failure",
            "priority": "High",
            "root_cause": "Expired certificate",
        },
    )

    response = client.get("/api/v1/analytics?period=daily", headers=auth_headers)
    assert response.status_code == 200
    statuses = {s["name"]: s["value"] for s in response.json()["ticket_status"]}
    assert statuses.get("Open", 0) >= 1


def test_analytics_unauthorized(client):
    response = client.get("/api/v1/analytics")
    assert response.status_code == 401
