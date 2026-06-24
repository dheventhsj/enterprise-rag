"""Unit tests for AuthService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.exceptions import ConflictError, UnauthorizedError
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserLoginRequest, UserRegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        secret_key="test-secret-key-minimum-32-characters-long",
        database_url="sqlite+aiosqlite:///./test.db",
        access_token_expire_minutes=30,
    )


@pytest.fixture
def auth_service(db_session: AsyncSession, settings: Settings) -> AuthService:
    return AuthService(UserRepository(db_session), settings)


@pytest.mark.asyncio
async def test_register_creates_user_and_token(auth_service: AuthService) -> None:
    """Registration returns user profile and bearer token."""
    result = await auth_service.register(
        UserRegisterRequest(
            email="newuser@example.com",
            password="securepass123",
            full_name="New User",
        )
    )
    assert result.user.email == "newuser@example.com"
    assert result.user.full_name == "New User"
    assert result.access_token
    assert result.token_type == "bearer"
    assert result.expires_in == 30 * 60


@pytest.mark.asyncio
async def test_register_duplicate_email_raises_conflict(auth_service: AuthService) -> None:
    """Duplicate registration is rejected."""
    payload = UserRegisterRequest(
        email="dup@example.com",
        password="securepass123",
    )
    await auth_service.register(payload)
    with pytest.raises(ConflictError):
        await auth_service.register(payload)


@pytest.mark.asyncio
async def test_login_with_valid_credentials(auth_service: AuthService) -> None:
    """Login succeeds after registration."""
    await auth_service.register(
        UserRegisterRequest(email="login@example.com", password="securepass123")
    )
    token = await auth_service.login(
        UserLoginRequest(email="login@example.com", password="securepass123")
    )
    assert token.access_token
    assert token.expires_in == 30 * 60


@pytest.mark.asyncio
async def test_login_with_invalid_password_raises_unauthorized(
    auth_service: AuthService,
) -> None:
    """Invalid password is rejected."""
    await auth_service.register(
        UserRegisterRequest(email="badlogin@example.com", password="securepass123")
    )
    with pytest.raises(UnauthorizedError):
        await auth_service.login(
            UserLoginRequest(email="badlogin@example.com", password="wrongpassword")
        )
