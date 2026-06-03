# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import auth, cars  # Імпортуємо наші нові модулі роутерів

# 1. Функція lifespan для створення таблиць у базі даних (якщо їх ще немає)
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# 2. Створення додатка FastAPI
app = FastAPI(title="JDM Service API with Auth", lifespan=lifespan)

# 3. ПІДКЛЮЧЕННЯ РОУТЕРІВ (Ендпоінтів)
app.include_router(auth.router)
app.include_router(cars.router)

# Головна сторінка
@app.get("/", tags=["General"])
async def root():
    return {"message": "Welcome to the Secure JDM API! Use /docs to see all endpoints."}