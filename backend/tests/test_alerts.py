def _get_token(client, auth_headers):
    return auth_headers["Authorization"].split(" ")[1]


def test_list_alerts(client, auth_headers):
    content = b"2026-06-15 10:00:00 CRITICAL [database] Connection pool exhausted"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("alert.log", content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)

    response = client.get("/api/v1/alerts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["unread"] >= 1
    assert data["alerts"][0]["alert_id"].startswith("ALT-")


def test_alert_stats(client, auth_headers):
    content = b"2026-06-15 ERROR [auth-service] Login failed"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("stats.log", content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)

    response = client.get("/api/v1/alerts/stats", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_mark_alert_read(client, auth_headers):
    content = b"2026-06-15 ERROR [network] Network error"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("read.log", content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)

    list_resp = client.get("/api/v1/alerts", headers=auth_headers)
    alert_id = list_resp.json()["alerts"][0]["alert_id"]

    response = client.patch(f"/api/v1/alerts/{alert_id}/read", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_mark_all_read(client, auth_headers):
    content = b"2026-06-15 ERROR [dns] DNS resolution failed"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("allread.log", content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)

    response = client.post("/api/v1/alerts/read-all", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["marked_read"] >= 1

    stats = client.get("/api/v1/alerts/stats", headers=auth_headers)
    assert stats.json()["unread"] == 0


def test_ticket_update_creates_alert(client, auth_headers):
    create_resp = client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "SSL handshake failure",
            "priority": "High",
            "root_cause": "Expired certificate",
        },
    )
    ticket_id = create_resp.json()["ticket_id"]

    client.patch(
        f"/api/v1/tickets/{ticket_id}",
        headers=auth_headers,
        json={"status": "in_progress"},
    )

    alerts = client.get("/api/v1/alerts", headers=auth_headers)
    titles = [a["title"] for a in alerts.json()["alerts"]]
    assert any("updated" in t.lower() for t in titles)


def test_alerts_unauthorized(client):
    response = client.get("/api/v1/alerts")
    assert response.status_code == 401
