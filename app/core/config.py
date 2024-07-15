import logging
from typing import Optional, Union

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    PORT: int = 8000
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    REDIS_DOMAIN: str
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: Optional[Union[str, None]] = None
    SECRET_KEY_JWT: str
    ALGORITHM: str
    AUTH0_DOMAIN: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_AUDIENCE: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


# Визначаємо, який .env файл використовувати
# env_file = ".env.nonlocal" if os.getenv("ENV") == ".env.nonlocal" else ".env"
#
# settings = Settings(_env_file=env_file)
settings = Settings()

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
