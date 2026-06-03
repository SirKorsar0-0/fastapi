# app/routers/cars.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database import get_db
from app.models import Car, ServiceRecord, User
from app import crud
from app.security import get_current_user  # Імпортуємо захист для Лаби 5

router = APIRouter(prefix="/api", tags=["Cars & Database"])

# Схема для валідації даних при додаванні машини
class CarCreateSchema(BaseModel):
    brand: str
    model: str
    vin: str


# === СІД БАЗИ ДАНИХ (Лаба 4) ===
@router.post("/db/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    return await crud.seed_initial_data(db)


# === ОТРИМАТИ ВСІ АВТОМОБІЛІ (Публічний рут) ===
@router.get("/cars")
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


# === ОТРИМАТИ ТІЛЬКИ МОЇ АВТОМОБІЛІ (ЗАХИЩЕНИЙ РУТ ДЛЯ ЛАБИ 5) ===
@router.get("/cars/my")
async def get_my_cars(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Повертає автомобілі, які належать виключно авторизованому користувачу"""
    cars = await crud.get_cars_by_owner(db, owner_id=current_user.id)
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "vin": car.vin
        } for car in cars
    ]


# === ДОДАТИ НОВИЙ АВТОМОБІЛЬ (ЗАХИЩЕНИЙ РУТ ДЛЯ ЛАБИ 5) ===
@router.post("/cars", status_code=status.HTTP_201_CREATED)
async def add_new_car(
    car_data: CarCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Дозволяє авторизованому юзеру додати автомобіль, який автоматично прив'яжеться до нього"""
    # Перетворюємо Pydantic-модель у dict через .model_dump() і передаємо в CRUD
    new_car = await crud.create_car(db, car_data.model_dump(), owner_id=current_user.id)
    return {
        "message": "Автомобіль успішно додано в гараж!",
        "car": {
            "id": new_car.id,
            "brand": new_car.brand,
            "model": new_car.model,
            "vin": new_car.vin,
            "owner": current_user.username
        }
    }


# === ОТРИМАТИ ІСТОРІЮ ОБСЛУГОВУВАННЯ КОНКРЕТНОЇ МАШИНИ ===
@router.get("/cars/{car_id}/service-history")
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