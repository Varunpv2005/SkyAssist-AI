def _upload_and_parse(client, auth_headers, filename, content):
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": (filename, content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)
    return log_id


def test_detect_incidents_from_parsed_log(client, auth_headers):
    content = b"""\
2026-06-15 10:00:00 ERROR [auth-service] Login failed for user admin
2026-06-15 10:01:00 ERROR [gateway] API timeout on /api/v1/proxy
2026-06-15 10:02:00 CRITICAL [database] Connection pool exhausted
"""
    log_id = _upload_and_parse(client, auth_headers, "security.log", content)

    # Incidents auto-detected on parse; second detect returns 0 new (deduped)
    response = client.post(f"/api/v1/incidents/detect/{log_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["incidents_detected"] == 0

    list_resp = client.get("/api/v1/incidents", headers=auth_headers)
    issue_types = {i["issue_type"] for i in list_resp.json()["incidents"] if i["log_file_id"] == log_id}
    assert "AUTH_FAILURE" in issue_types
    assert len(issue_types) >= 2


def test_auto_detect_on_parse(client, auth_headers):
    content = b"2026-06-15 10:00:00 ERROR [auth-service] Login failed"
    log_id = _upload_and_parse(client, auth_headers, "auto.log", content)

    response = client.get("/api/v1/incidents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(i["log_file_id"] == log_id for i in data["incidents"])


def test_list_incidents(client, auth_headers):
    content = b"2026-06-15 ERROR [dns] DNS resolution failed for api.internal"
    _upload_and_parse(client, auth_headers, "dns.log", content)

    response = client.get("/api/v1/incidents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    incident = data["incidents"][0]
    assert incident["incident_id"].startswith("INC-")
    assert "root_cause" in incident
    assert "recommendation" in incident


def test_get_incident_by_id(client, auth_headers):
    content = b"2026-06-15 ERROR [smtp] SMTP error sending notification"
    _upload_and_parse(client, auth_headers, "email.log", content)

    list_resp = client.get("/api/v1/incidents", headers=auth_headers)
    incident_id = list_resp.json()["incidents"][0]["incident_id"]

    response = client.get(f"/api/v1/incidents/{incident_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["incident_id"] == incident_id


def test_update_incident_status(client, auth_headers):
    content = b"2026-06-15 ERROR [network] Network error connection refused"
    _upload_and_parse(client, auth_headers, "net.log", content)

    list_resp = client.get("/api/v1/incidents", headers=auth_headers)
    incident_id = list_resp.json()["incidents"][0]["incident_id"]

    response = client.patch(
        f"/api/v1/incidents/{incident_id}",
        headers=auth_headers,
        json={"status": "resolved"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_incident_stats(client, auth_headers):
    content = b"2026-06-15 CRITICAL [database] Database connection failed"
    _upload_and_parse(client, auth_headers, "db.log", content)

    response = client.get("/api/v1/incidents/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert "critical" in data
    assert "open" in data


def test_detect_unparsed_log_fails(client, auth_headers):
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("raw.log", b"ERROR test", "text/plain")},
    )
    log_id = upload.json()["id"]

    response = client.post(f"/api/v1/incidents/detect/{log_id}", headers=auth_headers)
    assert response.status_code == 400
