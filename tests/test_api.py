import pytest
pytest.importorskip("rq")
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from backend.main import app

def test_health():
    assert TestClient(app).get("/health").json()=={"status":"ok"}

def test_invalid(monkeypatch):
    from backend.main import limit
    monkeypatch.setenv("HPC_API_KEY","test-secret")
    monkeypatch.setitem(app.dependency_overrides,limit,lambda: None)
    assert TestClient(app).post("/jobs",headers={"X-API-Key":"test-secret"},json={"kind":"quantum","size":21}).status_code==422


def test_unauthorized(monkeypatch):
    monkeypatch.setenv("HPC_API_KEY","test-secret")
    assert TestClient(app).get("/jobs/unknown").status_code==401
