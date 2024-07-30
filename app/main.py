from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger, settings
from app.db.postgres import get_database
from app.db.redis import redis_client
from app.routers.auth import router as auth_router
from app.routers.companies import router as companies_router
from app.routers.me import router as me_router
from app.routers.members import router as members_router
from app.routers.questions import router as questions_router
from app.routers.quizresult import router as quizresult_router
from app.routers.quizzes import router as quizzes_router
from app.routers.users import router as users_router
from app.routers.analytics import router as analytics_router



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

app.include_router(auth_router)
app.include_router(me_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(members_router)
app.include_router(questions_router)
app.include_router(quizzes_router)
app.include_router(quizresult_router)
app.include_router(analytics_router)


@app.get("/")
def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@app.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_database)):
    try:
        result = await db.execute(select(1))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI"}
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/test_redis")
async def test_redis_connection():
    try:
        # Перевірка підключення до Redis
        await redis_client.ping()
        print("Successfully connected to Redis")

        # Збереження значення у Redis
        await redis_client.set("test_key", "test_value")
        print("Successfully set key in Redis")

        # Отримання значення з Redis
        value = await redis_client.get("test_key")
        print(f"Value for 'test_key': {value}")

        # Перевірка значення
        assert value == "test_value", "Value did not match expected result"

        # Видалення ключа
        await redis_client.delete("test_key")
        print("Successfully deleted key from Redis")

        return value

    except Exception as e:
        print(f"Error during Redis test: {e}")


if __name__ == "__main__":
    import uvicorn

    # Запуск сервера FastAPI
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
