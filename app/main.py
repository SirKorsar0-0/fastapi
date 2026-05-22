from fastapi import FastAPI
from app.database import engine, Base
from app.routers import user  # Імпортуємо наш майбутній роутер

# Створення таблиць у БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Lab 3")

@app.get("/")
def read_root():
    return {"message": "База даних підключена успішно!"}

# Підключаємо роутер користувачів до головного застосунку
app.include_router(user.router)