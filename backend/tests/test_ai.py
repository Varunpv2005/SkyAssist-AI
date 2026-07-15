def test_ask_ai_fallback(client, auth_headers):
    response = client.post(
        "/api/v1/ai/ask",
        headers=auth_headers,
        json={
            "question": "Why did this error occur?",
            "log_snippet": "2026-06-15 ERROR [auth-service] Login failed for user admin",
            "severity": "High",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["root_cause"]
    assert data["explanation"]
    assert len(data["resolution_steps"]) >= 2
    assert 0 < data["confidence_score"] <= 1
    assert data["source"] in ("ollama", "fallback")
    assert data["question"] == "Why did this error occur?"


def test_ask_ai_with_incident(client, auth_headers):
    content = b"2026-06-15 ERROR [auth-service] Login failed"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("ai_test.log", content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)
    inc_resp = client.get("/api/v1/incidents", headers=auth_headers)
    incident_id = inc_resp.json()["incidents"][0]["incident_id"]

    response = client.post(
        "/api/v1/ai/ask",
        headers=auth_headers,
        json={
            "question": "Suggest a fix for this issue",
            "incident_id": incident_id,
        },
    )
    assert response.status_code == 200
    assert response.json()["resolution_steps"]


def test_ai_history(client, auth_headers):
    client.post(
        "/api/v1/ai/ask",
        headers=auth_headers,
        json={
            "question": "How can I resolve this issue?",
            "log_snippet": "ERROR database connection refused",
        },
    )

    response = client.get("/api/v1/ai/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["history"][0]["question"]


def test_ai_status(client, auth_headers):
    response = client.get("/api/v1/ai/status", headers=auth_headers)
    assert response.status_code == 200
    assert "available" in response.json()


def test_ask_ai_unauthorized(client):
    response = client.post(
        "/api/v1/ai/ask",
        json={"question": "Test question"},
    )
    assert response.status_code == 401
