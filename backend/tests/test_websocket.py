def _get_token(auth_headers):
    return auth_headers["Authorization"].split(" ")[1]


def test_websocket_connects_with_valid_token(client, auth_headers):
    token = _get_token(auth_headers)
    with client.websocket_connect(f"/ws?token={token}") as ws:
        data = ws.receive_json()
        assert data["event"] == "connected"


def test_websocket_rejects_invalid_token(client):
    try:
        with client.websocket_connect("/ws?token=invalid-token") as ws:
            ws.receive_json()
            assert False, "Should have closed connection"
    except Exception:
        pass


def test_alert_broadcast_payload(client, auth_headers):
    """Verify alert payloads are valid for WebSocket broadcast."""
    content = b"2026-06-15 CRITICAL [database] Connection pool exhausted"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("broadcast.log", content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)

    alerts = client.get("/api/v1/alerts", headers=auth_headers).json()["alerts"]
    assert len(alerts) >= 1
    alert = alerts[0]
    assert "alert_id" in alert
    assert alert["severity"] in ("critical", "high", "medium", "low", "info")
    assert alert["alert_type"] in ("incident", "ticket", "system")
