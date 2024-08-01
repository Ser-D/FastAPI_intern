from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from app.core.config import logger, settings
from app.db.redis import redis_client
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.checkers import router as checkers_router
from app.routers.companies import router as companies_router
from app.routers.me import router as me_router
from app.routers.members import router as members_router
from app.routers.questions import router as questions_router
from app.routers.quizresult import router as quizresult_router
from app.routers.quizzes import router as quizzes_router
from app.routers.users import router as users_router
from app.services.scheduler import check_quiz_completions

scheduler = AsyncIOScheduler()
scheduler.start()

scheduler.add_job(check_quiz_completions, "cron", hour=00, minute=1)


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
app.include_router(checkers_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
