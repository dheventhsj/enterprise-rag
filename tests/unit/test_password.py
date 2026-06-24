"""Unit tests for password hashing."""

from app.auth.password import hash_password, verify_password


def test_hash_password_produces_verifiable_hash() -> None:
    """Hashed passwords verify correctly."""
    hashed = hash_password("securepass123")
    assert hashed != "securepass123"
    assert verify_password("securepass123", hashed) is True


def test_verify_password_rejects_wrong_password() -> None:
    """Wrong password does not verify."""
    hashed = hash_password("securepass123")
    assert verify_password("wrongpassword", hashed) is False
