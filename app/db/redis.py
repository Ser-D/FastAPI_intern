import redis.asyncio as redis

from app.core.config import settings

REDIS_URL = settings.redis_url

# Create a Redis client
redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
