import pytest
pytest.importorskip("rq")
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from backend.main import app

def test_health():
    assert TestClient(app).get("/health").json()=={"status":"ok"}

def test_invalid():
    assert TestClient(app).post("/jobs",json={"kind":"quantum","size":21}).status_code==422
