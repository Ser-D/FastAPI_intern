from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
