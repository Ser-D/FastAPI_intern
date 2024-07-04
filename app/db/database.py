from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Функція для отримання сесії бази даних
async def get_database() -> AsyncSession:
    async with async_session() as session:
        yield session
