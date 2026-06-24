"""Unit tests for JWT utilities."""

from datetime import timedelta
from uuid import uuid4

import pytest
from jose import jwt

from app.auth.jwt import ALGORITHM, create_access_token, decode_access_token
from app.config.settings import Settings
from app.exceptions import UnauthorizedError


@pytest.fixture
def settings() -> Settings:
    """Minimal settings for JWT tests."""
    return Settings(
        secret_key="test-secret-key-minimum-32-characters-long",
        database_url="sqlite+aiosqlite:///./test.db",
    )


def test_create_and_decode_access_token(settings: Settings) -> None:
    """Valid tokens round-trip to the original user ID."""
    user_id = uuid4()
    token = create_access_token(user_id=user_id, settings=settings)
    decoded = decode_access_token(token, settings)
    assert decoded == user_id


def test_decode_rejects_tampered_token(settings: Settings) -> None:
    """Tampered tokens raise UnauthorizedError."""
    user_id = uuid4()
    token = create_access_token(user_id=user_id, settings=settings)
    tampered = f"{token}invalid"
    with pytest.raises(UnauthorizedError):
        decode_access_token(tampered, settings)


def test_decode_rejects_expired_token(settings: Settings) -> None:
    """Expired tokens raise UnauthorizedError."""
    user_id = uuid4()
    token = create_access_token(
        user_id=user_id,
        settings=settings,
        expires_delta=timedelta(seconds=-1),
    )
    with pytest.raises(UnauthorizedError):
        decode_access_token(token, settings)


def test_decode_rejects_wrong_token_type(settings: Settings) -> None:
    """Non-access tokens are rejected."""
    payload = {
        "sub": str(uuid4()),
        "type": "refresh",
        "exp": 9999999999,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    with pytest.raises(UnauthorizedError):
        decode_access_token(token, settings)
