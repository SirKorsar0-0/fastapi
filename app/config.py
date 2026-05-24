from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Налаштування бази даних
    DB_HOST: str = "db"  # назва сервісу в docker-compose
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "postgres"

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        # Формуємо асинхронний URL для asyncpg
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Налаштування для Лаби 5 (JWT)
    SECRET_KEY: str = "super_secret_key_change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Зчитування з файлу .env, якщо він є
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()