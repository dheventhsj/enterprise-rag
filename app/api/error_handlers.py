"""Global exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import AppError
from app.logging.logger import logger


def register_exception_handlers(app: FastAPI) -> None:
    """Map application exceptions to HTTP responses."""

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "Application error: %s",
            exc.message,
            extra={"status_code": exc.status_code, "details": exc.details},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details},
        )
