def _create_incident(client, auth_headers, content, filename="rca.log"):
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": (filename, content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)
    list_resp = client.get("/api/v1/incidents", headers=auth_headers)
    for inc in list_resp.json()["incidents"]:
        if inc["log_file_id"] == log_id:
            return inc["incident_id"]
    return list_resp.json()["incidents"][0]["incident_id"]


def test_analyze_incident(client, auth_headers):
    content = b"2026-06-15 ERROR [auth-service] Login failed for user admin"
    incident_id = _create_incident(client, auth_headers, content)

    response = client.post(
        f"/api/v1/analysis/incident/{incident_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == incident_id
    analysis = data["analysis"]
    assert analysis["issue"] == "Authentication Failure"
    assert len(analysis["possible_causes"]) >= 3
    assert analysis["confidence_score"] >= 0.5
    assert analysis["recommended_action"]


def test_get_analysis(client, auth_headers):
    content = b"2026-06-15 CRITICAL [database] Connection pool exhausted"
    incident_id = _create_incident(client, auth_headers, content)

    client.post(f"/api/v1/analysis/incident/{incident_id}", headers=auth_headers)

    response = client.get(
        f"/api/v1/analysis/incident/{incident_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["issue"] == "Database Connection Failure"


def test_get_analysis_not_found(client, auth_headers):
    content = b"2026-06-15 ERROR [dns] DNS resolution failed"
    incident_id = _create_incident(client, auth_headers, content)

    response = client.get(
        f"/api/v1/analysis/incident/{incident_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_list_analyses(client, auth_headers):
    content = b"2026-06-15 ERROR [gateway] API timeout on endpoint"
    incident_id = _create_incident(client, auth_headers, content)
    client.post(f"/api/v1/analysis/incident/{incident_id}", headers=auth_headers)

    response = client.get("/api/v1/analysis", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_reanalyze_updates_existing(client, auth_headers):
    content = b"2026-06-15 ERROR [auth-service] Login failed"
    incident_id = _create_incident(client, auth_headers, content)

    client.post(f"/api/v1/analysis/incident/{incident_id}", headers=auth_headers)
    response = client.post(
        f"/api/v1/analysis/incident/{incident_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200

    list_resp = client.get("/api/v1/analysis", headers=auth_headers)
    matching = [a for a in list_resp.json()["analyses"] if a["incident_ref"] == incident_id]
    assert len(matching) == 1


def test_analyze_incident_not_found(client, auth_headers):
    response = client.post(
        "/api/v1/analysis/incident/INC-9999",
        headers=auth_headers,
    )
    assert response.status_code == 404
