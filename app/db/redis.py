import logging

from redis.asyncio import from_url

from app.core.config import settings

logger = logging.getLogger(__name__)

HELP = f"redis://{settings.REDIS_HOST}:6379"

redis_client = from_url(HELP, encoding="utf-8", decode_responses=True)

logger.error(f"Redis host redis_client: {redis_client.connection_pool.connection_kwargs['host']}")
logger.error(f"Redis host: {settings.REDIS_HOST}")
logger.error(f"Redis host: {settings.REDIS_URL}")
