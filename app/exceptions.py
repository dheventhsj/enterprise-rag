"""Application-wide exception hierarchy."""

from typing import Any


class AppError(Exception):
    """Base application error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class UnauthorizedError(AppError):
    """Authentication required or invalid."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status_code=401)


class ForbiddenError(AppError):
    """Authenticated but not permitted."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status_code=403)


class ValidationError(AppError):
    """Input validation failed."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=422, details=details)


class ConflictError(AppError):
    """Resource conflict (e.g., duplicate email)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=409)


class RateLimitError(AppError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429)


class ExternalServiceError(AppError):
    """Upstream dependency failure."""

    def __init__(self, message: str, service: str) -> None:
        super().__init__(message, status_code=502, details={"service": service})
