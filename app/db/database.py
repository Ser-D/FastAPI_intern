from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# Функція для отримання сесії бази даних
async def get_database() -> async_session:
    async with async_session() as session:
        yield session
