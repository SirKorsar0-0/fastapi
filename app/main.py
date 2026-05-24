from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Імпорти для БД та моделей
from app.database import engine, Base, get_db
from app.crud import seed_initial_data, register_new_user, authenticate_user
from app.models import User, Profile, Car, ServiceRecord, Part
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.auth import create_access_token, get_current_user, verify_password

# 1. Функція lifespan (створення таблиць)
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# 2. Створення FastAPI додатку (ТІЛЬКИ ОДИН РАЗ)
app = FastAPI(title="JDM Service API with Auth", lifespan=lifespan)

# === ТВОЇ РУЧКИ (ROUTES) ===

@app.get("/", tags=["General"])
async def root():
    return {"message": "Welcome to the Secure JDM API!"}

# === АВТЕНТИФІКАЦІЯ ===
@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == user_data.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Користувач з таким ім'ям вже існує")
    return await register_new_user(db, user_data)

@app.post("/api/auth/login", response_model=Token, tags=["Authentication"])
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильне ім'я користувача або пароль"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# === БАЗА ДАНИХ (АВТО) ===
@app.post("/api/db/seed", tags=["Database"])
async def seed_database(db: AsyncSession = Depends(get_db)):
    return await seed_initial_data(db)

@app.get("/api/cars", tags=["Cars"])
async def get_all_cars(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car).options(selectinload(Car.owner)))
    cars = result.scalars().all()
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "vin": car.vin,
            "owner": car.owner.username if car.owner else "Немає власника"
        } for car in cars
    ]

@app.get("/api/cars/{car_id}/service-history", tags=["Cars"])
async def get_car_service_history(car_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ServiceRecord)
        .filter(ServiceRecord.car_id == car_id)
        .options(selectinload(ServiceRecord.parts))
    )
    records = result.scalars().all()
    return [
        {
            "id": rec.id,
            "description": rec.description,
            "mileage": rec.mileage,
            "cost": rec.cost,
            "date": rec.date,
            "parts": [{"name": p.name, "price": p.price} for p in rec.parts]
        } for rec in records
    ]