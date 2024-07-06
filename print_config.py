from app.core.config import settings

# Вивід значень змінних
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"REDIS_URL: {settings.REDIS_URL}")
print(f"REDIS_DOMAIN: {settings.REDIS_DOMAIN}")
print(f"REDIS_HOST: {settings.REDIS_HOST}")
print(f"REDIS_PORT: {settings.REDIS_PORT}")
