from fastapi import FastAPI
from database import engine, Base

# Створення таблиць у БД на основі моделей (виконається при запуску контейнера)
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "База даних підключена успішно!"}