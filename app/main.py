import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_database
from app.db.redis import redis_client

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await FastAPILimiter.init(redis_client)
        logger.info("Підключення до Redis успішно ініціалізоване.")
    except Exception as e:
        logger.error(f"Помилка підключення до Redis: {e}")
        raise e

    yield

    await redis_client.close()
    logger.info("Підключення до Redis закрито.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@app.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI"}
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)
