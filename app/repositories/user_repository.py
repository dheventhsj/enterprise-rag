"""User data access repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError
from app.models.user import User


class UserRepository:
    """Persistence layer for user accounts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by primary key."""
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by normalized email address."""
        normalized = email.strip().lower()
        result = await self._session.execute(select(User).where(User.email == normalized))
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str | None = None,
    ) -> User:
        """Create a new user account."""
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
            full_name=full_name,
        )
        self._session.add(user)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError("Email already registered") from exc
        await self._session.refresh(user)
        return user
