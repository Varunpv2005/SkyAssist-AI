SAMPLE = {
    "title": "Resolving AUTH_FAILURE incidents",
    "content": "## Overview\n\nAuthentication failures occur when credentials are invalid.\n\n## Steps\n1. Verify user account status\n2. Check auth service logs",
    "category": "Authentication",
    "tags": ["auth", "login", "security"],
}


def test_create_knowledge_article(client, auth_headers):
    response = client.post("/api/v1/knowledge", headers=auth_headers, json=SAMPLE)
    assert response.status_code == 201
    data = response.json()
    assert data["article_id"].startswith("KB-")
    assert data["tags"] == ["auth", "login", "security"]


def test_list_knowledge(client, auth_headers):
    client.post("/api/v1/knowledge", headers=auth_headers, json=SAMPLE)
    response = client.get("/api/v1/knowledge", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_get_knowledge(client, auth_headers):
    create = client.post("/api/v1/knowledge", headers=auth_headers, json=SAMPLE)
    article_id = create.json()["article_id"]
    response = client.get(f"/api/v1/knowledge/{article_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "Authentication failures" in response.json()["content"]


def test_update_knowledge(client, auth_headers):
    create = client.post("/api/v1/knowledge", headers=auth_headers, json=SAMPLE)
    article_id = create.json()["article_id"]
    response = client.patch(
        f"/api/v1/knowledge/{article_id}",
        headers=auth_headers,
        json={"title": "Updated AUTH guide"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated AUTH guide"


def test_delete_knowledge(client, auth_headers):
    create = client.post("/api/v1/knowledge", headers=auth_headers, json=SAMPLE)
    article_id = create.json()["article_id"]
    assert client.delete(f"/api/v1/knowledge/{article_id}", headers=auth_headers).status_code == 204


def test_search_knowledge(client, auth_headers):
    client.post("/api/v1/knowledge", headers=auth_headers, json=SAMPLE)
    response = client.get("/api/v1/knowledge/search?q=authentication", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_knowledge_in_global_search(client, auth_headers):
    client.post("/api/v1/knowledge", headers=auth_headers, json=SAMPLE)
    response = client.get("/api/v1/search?scope=knowledge&q=AUTH", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_ai_knowledge_retrieve(client, auth_headers):
    client.post("/api/v1/knowledge", headers=auth_headers, json=SAMPLE)
    response = client.get("/api/v1/ai/knowledge?q=authentication", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1
