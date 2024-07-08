import logging

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

    class Config:
        env_file = ".env"


# Визначаємо, який .env файл використовувати
# env_file = ".env.nonlocal" if os.getenv("ENV") == ".env.nonlocal" else ".env"
#
# settings = Settings(_env_file=env_file)
settings = Settings()

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
