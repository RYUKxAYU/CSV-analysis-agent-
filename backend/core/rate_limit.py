import redis.asyncio as redis
from fastapi import Request, HTTPException
from core.config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def rate_limit(request: Request, max_requests: int = 10, window: int = 60):
    user_id = request.state.user_id  # set by JWT middleware
    key = f"rate:{user_id}:{request.url.path}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, window)
    if count > max_requests:
        raise HTTPException(429, "Too many requests. Please wait a moment.")