"""Authentication API routes."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest
from app.schemas.user import RegisterResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    """Create a new user and return a JWT access token."""
    return await auth_service.register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain JWT",
)
async def login(
    payload: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Validate credentials and return a JWT access token."""
    return await auth_service.login(payload)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)
