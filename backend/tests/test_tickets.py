def _upload_and_parse(client, auth_headers, filename, content):
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": (filename, content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)
    return log_id


def test_create_ticket_manually(client, auth_headers):
    response = client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "API Gateway timeout on /proxy",
            "priority": "High",
            "root_cause": "Upstream service unresponsive",
            "assigned_to": "analyst1",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"].startswith("TKT-")
    assert data["issue"] == "API Gateway timeout on /proxy"
    assert data["priority"] == "High"
    assert data["status"] == "open"
    assert data["assigned_to"] == "analyst1"


def test_auto_generate_ticket_on_incident(client, auth_headers):
    content = b"2026-06-15 10:00:00 ERROR [auth-service] Login failed for user admin"
    _upload_and_parse(client, auth_headers, "ticket_auto.log", content)

    tickets_resp = client.get("/api/v1/tickets", headers=auth_headers)
    assert tickets_resp.status_code == 200
    tickets = tickets_resp.json()["tickets"]
    assert len(tickets) >= 1
    assert tickets[0]["ticket_id"].startswith("TKT-")
    assert tickets[0]["incident_ref"] is not None


def test_list_tickets(client, auth_headers):
    client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "SMTP delivery failure",
            "priority": "Medium",
            "root_cause": "Mail relay rejected connection",
        },
    )

    response = client.get("/api/v1/tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert "root_cause" in data["tickets"][0]


def test_get_ticket_by_id(client, auth_headers):
    create_resp = client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "DNS resolution failure",
            "priority": "Low",
            "root_cause": "Stale DNS cache",
        },
    )
    ticket_id = create_resp.json()["ticket_id"]

    response = client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["ticket_id"] == ticket_id


def test_update_ticket_status(client, auth_headers):
    create_resp = client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "SSL handshake failure",
            "priority": "Critical",
            "root_cause": "Expired certificate",
        },
    )
    ticket_id = create_resp.json()["ticket_id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket_id}",
        headers=auth_headers,
        json={"status": "in_progress", "assigned_to": "support-team"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["assigned_to"] == "support-team"


def test_delete_ticket(client, auth_headers):
    create_resp = client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "Test ticket for deletion",
            "priority": "Low",
            "root_cause": "Temporary test",
        },
    )
    ticket_id = create_resp.json()["ticket_id"]

    delete_resp = client.delete(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_ticket_stats(client, auth_headers):
    client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "Network error",
            "priority": "High",
            "root_cause": "Connection refused",
        },
    )

    response = client.get("/api/v1/tickets/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["open"] >= 1


def test_create_ticket_from_incident(client, auth_headers):
    content = b"2026-06-15 ERROR [database] Connection pool exhausted"
    _upload_and_parse(client, auth_headers, "db_ticket.log", content)

    incidents_resp = client.get("/api/v1/incidents", headers=auth_headers)
    incident_ref = incidents_resp.json()["incidents"][0]["incident_id"]

    # Auto ticket already created; manual link should fail
    response = client.post(
        "/api/v1/tickets",
        headers=auth_headers,
        json={
            "issue": "Duplicate ticket attempt",
            "priority": "Critical",
            "root_cause": "DB down",
            "incident_id": incident_ref,
        },
    )
    assert response.status_code == 400


def test_tickets_unauthorized(client):
    response = client.get("/api/v1/tickets")
    assert response.status_code == 401
