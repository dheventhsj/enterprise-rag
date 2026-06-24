"""FastAPI authentication dependencies."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import get_auth_service
from app.auth.jwt import decode_access_token
from app.config.settings import Settings, get_settings
from app.exceptions import UnauthorizedError
from app.models.user import User
from app.services.auth_service import AuthService

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> User:
    """Resolve the authenticated user from a Bearer JWT."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing authentication credentials")

    user_id = decode_access_token(credentials.credentials, settings)
    return await auth_service.get_user_by_id(user_id)
