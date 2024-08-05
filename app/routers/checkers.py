from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.db.postgres import get_database
from app.db.redis import redis_client

router = APIRouter(prefix="", tags=["checkers"])


@router.get("/")
def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):
    try:
        result = await db.execute(select(1))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI"}
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@router.get("/test_redis")
async def test_redis_connection():
    try:
        await redis_client.ping()
        print("Successfully connected to Redis")

        await redis_client.set("test_key", "test_value")
        print("Successfully set key in Redis")

        value = await redis_client.get("test_key")
        print(f"Value for 'test_key': {value}")

        assert value == "test_value", "Value did not match expected result"

        await redis_client.delete("test_key")
        print("Successfully deleted key from Redis")

        return value

    except Exception as e:
        print(f"Error during Redis test: {e}")
