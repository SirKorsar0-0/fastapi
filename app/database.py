from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Додаємо +asyncpg до URL для асинхронної роботи
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@db:5432/mydb"

# Створюємо асинхронний двигун
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Фабрика асинхронних сесій
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовий клас
class Base(DeclarativeBase):
    pass

# АНСИНХРОННИЙ генератор сесії для роутів FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db