def _create_incident(client, auth_headers):
    content = b"2026-06-15 ERROR [auth-service] Login failed for user admin"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("rem.log", content, "text/plain")},
    )
    client.post(f"/api/v1/logs/{upload.json()['id']}/parse", headers=auth_headers)
    incidents = client.get("/api/v1/incidents", headers=auth_headers).json()["incidents"]
    return incidents[0]["incident_id"]


def test_generate_remediation(client, auth_headers):
    incident_id = _create_incident(client, auth_headers)
    response = client.post(
        "/api/v1/ai/remediate",
        headers=auth_headers,
        json={"incident_id": incident_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["remediation_id"].startswith("REM-")
    assert len(data["recommended_fixes"]) >= 1
    assert len(data["troubleshooting_steps"]) >= 1
    assert 0 <= data["confidence_score"] <= 1


def test_remediation_history(client, auth_headers):
    incident_id = _create_incident(client, auth_headers)
    client.post("/api/v1/ai/remediate", headers=auth_headers, json={"incident_id": incident_id})
    response = client.get("/api/v1/ai/remediations", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_get_remediation_by_id(client, auth_headers):
    incident_id = _create_incident(client, auth_headers)
    create = client.post("/api/v1/ai/remediate", headers=auth_headers, json={"incident_id": incident_id})
    rem_id = create.json()["remediation_id"]
    response = client.get(f"/api/v1/ai/remediations/{rem_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["remediation_id"] == rem_id


def test_remediation_unauthorized(client):
    assert client.post("/api/v1/ai/remediate", json={}).status_code == 401
