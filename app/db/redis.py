import redis.asyncio as redis

from app.core.config import settings

REDIS_URL = settings.REDIS_URL or "redis://localhost:6379"
# REDIS_URL = (settings.REDIS_URL or "redis://localhost:6379")

# Create a Redis client
# redis_client = redis.Redis(
#         host=settings.REDIS_DOMAIN,
#         port=settings.REDIS_PORT,
#         db=0,
#     )


redis_client = redis.from_url(
    (REDIS_URL or "localhost"), encoding="utf-8", decode_responses=True
)
