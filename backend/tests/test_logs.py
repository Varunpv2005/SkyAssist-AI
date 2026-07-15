def test_upload_log_success(client, auth_headers):
    content = b"2026-06-15 10:00:00 ERROR Auth failure from 192.168.1.1"
    response = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("proxy_error.log", content, "text/plain")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "proxy_error.log"
    assert data["file_type"] == "log"
    assert data["status"] == "uploaded"
    assert data["file_size"] == len(content)
    assert data["message"] == "File uploaded successfully"


def test_upload_txt_file(client, auth_headers):
    response = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("access.txt", b"INFO connection established", "text/plain")},
    )
    assert response.status_code == 201
    assert response.json()["file_type"] == "txt"


def test_upload_csv_file(client, auth_headers):
    response = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("events.csv", b"timestamp,severity,message\n", "text/csv")},
    )
    assert response.status_code == 201
    assert response.json()["file_type"] == "csv"


def test_upload_invalid_extension(client, auth_headers):
    response = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("malware.exe", b"bad", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_upload_empty_file(client, auth_headers):
    response = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("empty.log", b"", "text/plain")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_unauthorized(client):
    response = client.post(
        "/api/v1/logs/upload",
        files={"file": ("test.log", b"data", "text/plain")},
    )
    assert response.status_code == 401


def test_list_logs(client, auth_headers):
    client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("app.log", b"ERROR timeout", "text/plain")},
    )
    client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("api.log", b"WARNING slow", "text/plain")},
    )

    response = client.get("/api/v1/logs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["logs"]) == 2
    assert data["logs"][0]["filename"] in ("app.log", "api.log")


def test_list_logs_unauthorized(client):
    response = client.get("/api/v1/logs")
    assert response.status_code == 401


def test_parse_log_success(client, auth_headers):
    content = b"2026-06-15 10:00:00 ERROR [auth-service] Login failed\n2026-06-15 10:01:00 WARNING [proxy] Slow response"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("security.log", content, "text/plain")},
    )
    log_id = upload.json()["id"]

    response = client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_entries"] == 2
    assert data["filename"] == "security.log"
    assert data["severity_summary"]["ERROR"] == 1
    assert data["severity_summary"]["WARNING"] == 1
    assert data["entries"][0]["severity"] == "ERROR"
    assert data["entries"][0]["source"] == "auth-service"


def test_parse_log_csv(client, auth_headers):
    csv_content = b"timestamp,severity,message,source\n2026-06-15 10:00:00,CRITICAL,DB down,database"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("events.csv", csv_content, "text/csv")},
    )
    log_id = upload.json()["id"]

    response = client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_entries"] == 1
    assert data["entries"][0]["severity"] == "CRITICAL"


def test_get_parsed_entries(client, auth_headers):
    content = b"2026-06-15 10:00:00 INFO [api] Request OK"
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("api.log", content, "text/plain")},
    )
    log_id = upload.json()["id"]
    client.post(f"/api/v1/logs/{log_id}/parse", headers=auth_headers)

    response = client.get(f"/api/v1/logs/{log_id}/entries", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total_entries"] == 1


def test_parse_log_not_found(client, auth_headers):
    response = client.post("/api/v1/logs/9999/parse", headers=auth_headers)
    assert response.status_code == 404


def test_get_entries_before_parse(client, auth_headers):
    upload = client.post(
        "/api/v1/logs/upload",
        headers=auth_headers,
        files={"file": ("raw.log", b"2026-06-15 ERROR test", "text/plain")},
    )
    log_id = upload.json()["id"]

    response = client.get(f"/api/v1/logs/{log_id}/entries", headers=auth_headers)
    assert response.status_code == 404
