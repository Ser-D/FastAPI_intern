import pytest
import pytest_asyncio
import asyncio
import contextlib
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from fastapi.testclient import TestClient
from app.core.config import settings
from app.models import Base, User
from app.main import app
from app.db.postgres import get_database
from app.services.auth import auth_service

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

test_user = {
    "firstname": "Test",
    "lastname": "User",
    "email": "test@example.com",
    "password": "testpassword"
}

class DataBaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine)
        self.engine = self._engine

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception('Session is not initialized')
        session = self._session_maker()
        try:
            yield session
        except:
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DataBaseSessionManager(SQLALCHEMY_DATABASE_URL)


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with sessionmanager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with sessionmanager.session() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(firstname=test_user["firstname"], lastname=test_user["lastname"], email=test_user["email"], hashed_password=hash_password)
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    async def override_get_database():
        async with sessionmanager.session() as session:
            yield session

    app.dependency_overrides[get_database] = override_get_database

    yield TestClient(app)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token
