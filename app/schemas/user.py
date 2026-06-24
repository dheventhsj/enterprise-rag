"""User response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    """Public user profile returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime


class RegisterResponse(BaseModel):
    """Registration success response."""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int
