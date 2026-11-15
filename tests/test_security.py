import pytest

pytest.importorskip("fastapi")
from backend.security import hash_password, verify_password


def test_password_hash_is_salted_and_verified():
    first = hash_password("a-long-test-password")
    second = hash_password("a-long-test-password")
    assert first != second
    assert verify_password("a-long-test-password", first)
    assert not verify_password("wrong-password", first)


def test_password_verifier_rejects_malformed_hash():
    assert not verify_password("anything", "not-a-password-hash")
