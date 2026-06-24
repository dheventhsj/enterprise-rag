"""Authentication business logic."""

from uuid import UUID

from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_password
from app.config.settings import Settings
from app.exceptions import ConflictError, UnauthorizedError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest
from app.schemas.user import RegisterResponse, UserResponse


class AuthService:
    """Handles registration, login, and token issuance."""

    def __init__(self, user_repository: UserRepository, settings: Settings) -> None:
        self._users = user_repository
        self._settings = settings

    async def register(self, payload: UserRegisterRequest) -> RegisterResponse:
        """Register a new user and return profile plus access token."""
        existing = await self._users.get_by_email(payload.email)
        if existing is not None:
            raise ConflictError("Email already registered")

        user = await self._users.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        token = create_access_token(user_id=user.id, settings=self._settings)
        return RegisterResponse(
            user=UserResponse.model_validate(user),
            access_token=token,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    async def login(self, payload: UserLoginRequest) -> TokenResponse:
        """Authenticate credentials and return an access token."""
        user = await self._authenticate(payload.email, payload.password)
        token = create_access_token(user_id=user.id, settings=self._settings)
        return TokenResponse(
            access_token=token,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    async def get_user_by_id(self, user_id: UUID) -> User:
        """Load an active user by ID or raise UnauthorizedError."""
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("User not found")
        if not user.is_active:
            raise UnauthorizedError("User account is inactive")
        return user

    async def _authenticate(self, email: str, password: str) -> User:
        """Verify email/password pair."""
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("User account is inactive")
        return user
