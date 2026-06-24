"""JWT token creation and validation."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.config.settings import Settings
from app.exceptions import UnauthorizedError

ALGORITHM = "HS256"


def create_access_token(
    *,
    user_id: UUID,
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token for the given user."""
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, settings: Settings) -> UUID:
    """Decode and validate a JWT access token; return the user ID."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    token_type = payload.get("type")
    if token_type != "access":
        raise UnauthorizedError("Invalid token type")

    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError("Invalid token payload")

    try:
        return UUID(subject)
    except ValueError as exc:
        raise UnauthorizedError("Invalid token subject") from exc
