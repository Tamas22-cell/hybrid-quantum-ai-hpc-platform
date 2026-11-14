import pytest
pytest.importorskip("fastapi")
from fastapi import HTTPException
from backend.security import authorize

def test_auth(monkeypatch):
    monkeypatch.setenv("HPC_API_KEY","test-secret")
    authorize("test-secret")
    with pytest.raises(HTTPException) as e:
        authorize("invalid")
    assert e.value.status_code==401

def test_unconfigured(monkeypatch):
    monkeypatch.delenv("HPC_API_KEY",raising=False)
    with pytest.raises(HTTPException) as e:
        authorize("")
    assert e.value.status_code==503
