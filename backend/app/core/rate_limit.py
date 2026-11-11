"""Redis-backed fixed-window rate limiting for public endpoints."""
from fastapi import HTTPException, Request
from redis import Redis
from redis.exceptions import RedisError
from app.core.config import get_settings

_client: Redis | None = None

def _redis() -> Redis:
    global _client
    if _client is None:
        _client = Redis.from_url(get_settings().redis_url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
    return _client

def enforce_rate_limit(request: Request, bucket: str, limit: int, window_seconds: int = 60) -> None:
    address = request.client.host if request.client else "unknown"
    key = f"factforge:ratelimit:{bucket}:{address}"
    try:
        client = _redis()
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds, nx=True)
        count, _ = pipe.execute()
    except RedisError:
        # Fail closed: do not silently disable abuse controls if Redis is down.
        raise HTTPException(status_code=503, detail="Request protection is temporarily unavailable") from None
    if int(count) > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please retry later.")

def check_redis() -> None:
    _redis().ping()
