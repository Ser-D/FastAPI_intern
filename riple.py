import redis.asyncio as aioredis


async def connect_to_redis():
    redis_url = "redis://myrediscluster-ro.n0q06z.ng.0001.use1.cache.amazonaws.com:6379"
    redis = aioredis.from_url(redis_url, password='', decode_responses=True)

    try:
        # Перевірка підключення
        await redis.ping()
        print("Successfully connected to Redis")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
    return redis


# Виклик функції
import asyncio

asyncio.run(connect_to_redis())


