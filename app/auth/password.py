"""Password hashing and verification."""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plaintext password matches the hash."""
    return _pwd_context.verify(plain_password, hashed_password)
