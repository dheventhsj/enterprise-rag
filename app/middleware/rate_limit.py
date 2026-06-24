"""Redis-backed rate limiting middleware."""

import time
from collections.abc import Callable

import redis.asyncio as aioredis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import Settings, get_settings
from app.exceptions import RateLimitError


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter using Redis."""

    def __init__(self, app, settings: Settings | None = None) -> None:
        super().__init__(app)
        self._settings = settings or get_settings()
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(
                self._settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in {"/health", "/metrics"}:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}:{int(time.time()) // self._settings.rate_limit_window_seconds}"

        try:
            redis = await self._get_redis()
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, self._settings.rate_limit_window_seconds)
            if count > self._settings.rate_limit_requests:
                raise RateLimitError()
        except RateLimitError:
            raise
        except Exception:
            pass

        return await call_next(request)
