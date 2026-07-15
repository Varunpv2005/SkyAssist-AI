import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient

from database.session import Base, SessionLocal, engine, get_db
from main import app


@pytest.fixture(autouse=True)
def setup_database(tmp_path, monkeypatch):
    logs_dir = str(tmp_path / "logs")
    monkeypatch.setenv("LOGS_DIR", logs_dir)
    from database.config import settings

    settings.LOGS_DIR = logs_dir

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "loguser",
            "email": "loguser@example.com",
            "password": "securepass123",
            "role": "analyst",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "loguser", "password": "securepass123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
