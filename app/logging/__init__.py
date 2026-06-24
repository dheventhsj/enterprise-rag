"""Structured logging configuration."""

import logging
import sys
from typing import Any

from app.config.settings import Settings


class JSONFormatter(logging.Formatter):
    """Format log records as structured JSON-like key=value pairs."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize log record to a single line."""
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key in ("request_id", "user_id", "path", "method", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return " ".join(f"{k}={v!r}" for k, v in payload.items())


def setup_logging(settings: Settings) -> None:
    """Configure root logger for the application."""
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if settings.log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )

    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
