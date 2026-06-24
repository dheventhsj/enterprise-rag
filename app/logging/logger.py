"""Logging utilities."""

import logging
from typing import Any

logger = logging.getLogger("enterprise_rag")


def log_extra(**kwargs: Any) -> dict[str, Any]:
    """Build extra dict for structured logging."""
    return kwargs
