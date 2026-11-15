import pytest

pytest.importorskip("rq")
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.main import app, current_user
from backend.security import UserIdentity


def test_health_is_public():
    assert TestClient(app).get("/health").json() == {"status": "ok"}


def test_jobs_require_a_session():
    client = TestClient(app)
    assert client.get("/jobs/unknown").status_code == 401
    assert client.post("/jobs", json={"kind": "matrix", "size": 4}).status_code == 401
    assert client.get("/history").status_code == 401


def test_auth_endpoints_require_server_side_api_key(monkeypatch):
    monkeypatch.setenv("HPC_API_KEY", "test-internal-secret")
    response = TestClient(app).post(
        "/auth/register",
        json={"email": "private@example.test", "password": "a-long-test-password"},
    )
    assert response.status_code == 401


def test_user_cannot_read_another_users_job(monkeypatch):
    from backend import main

    class OtherUsersJob:
        id = "job-1"
        result = {"private": True}
        meta = {"owner_id": "user-b"}

        @staticmethod
        def get_status():
            class Status:
                value = "finished"

            return Status()

    monkeypatch.setattr(main.Job, "fetch", lambda *args, **kwargs: OtherUsersJob())
    app.dependency_overrides[current_user] = lambda: UserIdentity(id="user-a", email="a@example.test")
    try:
        response = TestClient(app).get("/jobs/job-1")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
